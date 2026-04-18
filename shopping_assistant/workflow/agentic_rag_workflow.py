from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from shopping_assistant.prompt_library.prompt import PROMPT_REGISTRY, PromptType
from shopping_assistant.retriever.retrieval import Retriever
from shopping_assistant.utils.model_loader import ModelLoader

class AgenticRAG:
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
    def __init__(self):
        self.retriever = Retriever()
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm()
        self.memory_saver = MemorySaver()
        self.workflow = self.__build_workflow()
        self.app = self.workflow.compile(checkpointer = self.memory_saver)
    
    def __ai_assistant(self, state: AgentState):
        """
        Calls assistant LLM
        """
        messages = state["messages"]
        query = messages[-1].content
        
        if any(word in query.lower() for word in ["price", "product", "review"]):
            return {"messages": [HumanMessage(content="Tool: Retriever")]}
        else:
            prompt = ChatPromptTemplate.from_template(
                "You are a helpful assistant. Answer the user directly.\n\nQuestion: {question}\nAnswer:"
            )
            chain = prompt | self.llm | StrOutputParser()
            res = chain.invoke({"question": query})
            return {"messages": [HumanMessage(content=res)]}
        
    def __format_docs(self, docs) -> str:
        if not docs:
            return "No relevant documents found."
        
        formatted_docs = []
        
        for doc in docs:
            metadata = doc.metadata or {}
            formatted_doc = (
                f"Title: {metadata.get('product_title','N/A')}\n"
                f"Price: {metadata.get('price','N/A')}\n"
                f"Rating: {metadata.get('rating','N/A')}\n"
                f"Review: \n {doc.page_content.strip()}"
            )
            formatted_docs.append(formatted_doc)
        return "\n\n---\n\n".join(formatted_docs)
    
    def __vector_retriever(self, state: AgentState):
        """Retriever"""
        query = state["messages"][-1].content
        retriever = self.retriever.load_retriever()
        docs = retriever.invoke(query)
        formatted_docs = self.__format_docs(docs)
        return {"messages": [HumanMessage(content=formatted_docs)]}
    
    def __grade_documents(self, state: AgentState):
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
        new_q = self.llm.invoke(
            [HumanMessage(content=f"Rewrite the query to be clearer: {question}")]
        )
        return {"messages": [HumanMessage(content=new_q.content)]}
    
    def __build_workflow(self):
        workflow = StateGraph(self.AgentState)
        workflow.add_node("Assistant", self.__ai_assistant)
        workflow.add_node("Retriever", self.__vector_retriever)
        workflow.add_node("Generate", self.__generate)
        workflow.add_node("Rewrite", self.__rewrite)
        
        workflow.add_edge(START, "Assistant")
        workflow.add_conditional_edges(
            "Assistant",
            lambda state: "Retriever" if "Tool" in state["messages"][-1].content else "end",
            {
                "Retriever": "Retriever",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "Retriever",
            lambda state: self.__grade_documents(state),
            {
                "generator": "Generate",
                "rewriter": "Rewrite"
            }
        )
        workflow.add_edge("Generate", END)
        workflow.add_edge("Rewrite", "Assistant")
        return workflow
    
    def run(self, query, thread_id: str = "default_thread"):
        """
        Run the workflow for a given query and return the final answer.
        """
        result = self.app.invoke({"messages": [HumanMessage(content=query)]},
                                 config={"configurable": {"thread_id": thread_id}})
        return result["messages"][-1].content
    
if __name__ == "__main__":
    agentic_rag = AgenticRAG()
    query = "What is the best product for lipstick under $100?"
    response = agentic_rag.run(query)
    print("Final Response:", response)