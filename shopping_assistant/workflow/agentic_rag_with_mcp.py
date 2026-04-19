from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from shopping_assistant.prompt_library.prompt import PROMPT_REGISTRY, PromptType
from retriever.retrieval import Retriever
from utils.model_loader import ModelLoader
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


class AgenticRAG:
    """Agentic RAG pipeline using LangGraph."""

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]

    def __init__(self):
        self.retriever_obj = Retriever()
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm()
        self.checkpointer = MemorySaver()
        
        self.mcp_client = MultiServerMCPClient({
            "product_retriever": {
                "command": "python",
                "args": ["shopping_assistant/mcp/product_search_server.py"],  # absolute path recommended
                "transport": "stdio"
            }
        })
       
        self.mcp_tools = asyncio.run(self.mcp_client.get_tools())
        
        self.workflow = self.__build_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)

    def __ai_assistant(self, state: AgentState):
        print("--- CALL ASSISTANT ---")
        messages = state["messages"]
        last_message = messages[-1].content

        if any(word in last_message.lower() for word in ["price", "review", "product"]):
            return {"messages": [HumanMessage(content="TOOL: retriever")]}
        else:
            prompt = ChatPromptTemplate.from_template(
                "You are a helpful assistant. Answer the user directly.\n\nQuestion: {question}\nAnswer:"
            )
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({"question": last_message})
            return {"messages": [HumanMessage(content=response)]}

    def __vector_retriever(self, state: AgentState):
        print("--- RETRIEVER (MCP) ---")
        query = state["messages"][-1].content
        # Find the tool by name
        tool = next(t for t in self.mcp_tools if t.name == "get_product_info")
        # Call the tool (sync wrapper)
        result = asyncio.run(tool.ainvoke({"query": query}))
        context = result if result else "No data"
        return {"messages": [HumanMessage(content=context)]}

    def __grade_documents(self, state: AgentState) -> Literal["generator", "rewriter"]:
        print("--- GRADER ---")
        question = state["messages"][0].content
        docs = state["messages"][-1].content

        prompt = PromptTemplate(
            template="""You are a grader. Question: {question}\nDocs: {docs}\n
            Are docs relevant to the question? Answer yes or no.""",
            input_variables=["question", "docs"],
        )
        chain = prompt | self.llm | StrOutputParser()
        score = chain.invoke({"question": question, "docs": docs})
        return "generator" if "yes" in score.lower() else "rewriter"

    def __generate(self, state: AgentState):
        print("--- GENERATE ---")
        question = state["messages"][0].content
        docs = state["messages"][-1].content
        prompt = ChatPromptTemplate.from_template(
            PROMPT_REGISTRY[PromptType.PRODUCT_BOT].template
        )
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": docs, "question": question})
        return {"messages": [HumanMessage(content=response)]}

    def __rewrite(self, state: AgentState):
        print("--- REWRITE ---")
        question = state["messages"][0].content
        prompt = ChatPromptTemplate.from_template(
            "Rewrite this user query to make it more clear and specific for a search engine. "
            "Do NOT answer the query. Only rewrite it.\n\nQuery: {question}\nRewritten Query:"
        )
        chain = prompt | self.llm | StrOutputParser()
        new_q = chain.invoke({"question": question})
        return {"messages": [HumanMessage(content=new_q.strip())]}

    def __build_workflow(self):
        workflow = StateGraph(self.AgentState)
        workflow.add_node("Assistant", self.__ai_assistant)
        workflow.add_node("Retriever", self.__vector_retriever)
        workflow.add_node("Generator", self.__generate)
        workflow.add_node("Rewriter", self.__rewrite)

        workflow.add_edge(START, "Assistant")
        workflow.add_conditional_edges(
            "Assistant",
            lambda state: "Retriever" if "TOOL" in state["messages"][-1].content else END,
            {"Retriever": "Retriever", END: END},
        )
        workflow.add_conditional_edges(
            "Retriever",
            self.__grade_documents,
            {"generator": "Generator", "rewriter": "Rewriter"},
        )
        workflow.add_edge("Generator", END)
        workflow.add_edge("Rewriter", "Assistant")
        return workflow

    def run(self, query: str,thread_id: str = "default_thread") -> str:
        """Run the workflow for a given query and return the final answer."""
        result = self.app.invoke({"messages": [HumanMessage(content=query)]},
                                 config={"configurable": {"thread_id": thread_id}})
        return result["messages"][-1].content
    
if __name__ == "__main__":
    rag_agent = AgenticRAG()
    answer = rag_agent.run("Please provide obsessed lipstick?")
    print("\nFinal Answer:\n", answer)