from mcp.server.fastmcp import FastMCP
from shopping_assistant.retriever.retrieval import Retriever  
from langchain_community.tools import DuckDuckGoSearchRun

from shopping_assistant.utils.format_docs import format_docs

mcp = FastMCP("hybrid_search")

retriever = Retriever()
retriever = retriever.load_retriever()

duckduckgo = DuckDuckGoSearchRun()
   
@mcp.tool()
async def get_product_info(query: str) -> str:
    """Retrieve product information for a given query from local retriever."""
    try:
        docs = retriever.invoke(query)
        context = format_docs(docs)
        if not context.strip():
            return "No local results found."
        return context
    except Exception as e:
        return f"Error retrieving product info: {str(e)}"

@mcp.tool()
async def web_search(query: str) -> str:
    """Search the web using DuckDuckGo if retriever has no results."""
    try:
        return duckduckgo.run(query)
    except Exception as e:
        return f"Error during web search: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="streamable-http")