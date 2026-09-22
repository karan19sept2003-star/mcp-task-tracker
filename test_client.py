import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,  # use this same venv's python to launch server.py
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            print("\n--- Adding a task ---")
            result = await session.call_tool(
                "add_task", {"description": "Finish MCP assignment", "priority": "high"}
            )
            print(result.content)

            print("\n--- Adding a second task ---")
            result2 = await session.call_tool(
                "add_task", {"description": "Buy groceries", "priority": "low"}
            )
            print(result2.content)

            print("\n--- Reading the daily_summary prompt ---")
            prompt_result = await session.get_prompt("daily_summary", {})
            for msg in prompt_result.messages:
                print(msg.content.text)

            print("\n--- Completing task 1 ---")
            complete_result = await session.call_tool("complete_task", {"task_id": 1})
            print(complete_result.content)


if __name__ == "__main__":
    asyncio.run(main())