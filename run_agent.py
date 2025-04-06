import asyncio
from llm_agents import EnhancedAgent, ChatLLM
from llm_agents.tools import PythonREPLTool, HackerNewsSearchTool, GoogleSearchTool
from llm_agents.tools.enhanced_tool_manager import EnhancedToolManager

async def setup_agent():
    # Initialize tools
    tools = [
        PythonREPLTool(),
        HackerNewsSearchTool(),
        GoogleSearchTool()
    ]
    
    # Create enhanced tool manager
    tool_manager = EnhancedToolManager(tools)
    
    # Define some useful tool chains
    tool_manager.define_tool_chain(
        "search_and_analyze",
        ["GoogleSearchTool", "PythonREPLTool"]
    )
    
    # Create enhanced agent
    agent = EnhancedAgent(
        llm=ChatLLM(),
        tools=tools
    )
    
    return agent, tool_manager

async def main():
    agent, tool_manager = await setup_agent()
    
    while True:
        try:
            prompt = input("\nEnter a question / task for the agent (or 'quit' to exit): ")
            if prompt.lower() == 'quit':
                break
                
            result = await agent.run(prompt)
            print(f"\nFinal answer: {result}")
            
            # Show tool usage statistics
            print("\nTool Usage Statistics:")
            for tool, stats in tool_manager.get_tool_stats().items():
                print(f"{tool}: {stats.usage_count} uses, {stats.success_count} successes, {stats.error_count} errors")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue

if __name__ == '__main__':
    asyncio.run(main())
