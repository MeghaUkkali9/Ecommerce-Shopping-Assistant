import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client  = MultiServerMCPClient({
        "hybrid_search": {
            "command": "python",
            "args": [
                    r"/Users/meghaukkali/Documents/ecommerce-shopping-assistant/shopping_assistant/mcp/product_search_server.py"
                    ],
            "transport": "stdio",
        }
    })
    
    tools = await client.get_tools()
    print("\n\n\nTools:", [tool.name for tool in tools])
    
    retriever_tool = next(tool for tool in tools if tool.name == "get_product_info")
    web_search_tool = next(tool for tool in tools if tool.name == "web_search")
    
    query = "provide obsessed lipstick"
    retriever_result = await retriever_tool.ainvoke({"query": query})
    print("\nRetriever Result:\n", retriever_result)

    if not retriever_result.strip() or "No local results found." in retriever_result:
        
        print("\n No local results, falling back to web search...\n")
        web_result = await web_search_tool.ainvoke({"query": query})
        print("Web Search Result:\n", web_result)

if __name__ == "__main__":
    print("\n\n\nStarting MCP Client...")
    asyncio.run(main())