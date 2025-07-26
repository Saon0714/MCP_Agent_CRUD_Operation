# import asyncio
# from dataclasses import dataclass, field
# from typing import Union, cast

# import anthropic
# from anthropic.types import MessageParam, TextBlock, ToolUnionParam, ToolUseBlock
# from dotenv import load_dotenv
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# load_dotenv()


# anthropic_client = anthropic.AsyncAnthropic()


# # Create server parameters for stdio connection
# server_params = StdioServerParameters(
#     command="python",  # Executable
#     args=["./mcp_server.py"],  # Optional command line arguments
#     env=None,  # Optional environment variables
# )


# @dataclass
# class Chat:
#     messages: list[MessageParam] = field(default_factory=list)

#     system_prompt: str = """You are a master SQLite assistant. 
#     Your job is to use the tools at your dispoal to execute SQL queries and provide the results to the user."""

#     async def process_query(self, session: ClientSession, query: str) -> None:
#         response = await session.list_tools()
#         available_tools: list[ToolUnionParam] = [
#             {
#                 "name": tool.name,
#                 "description": tool.description or "",
#                 "input_schema": tool.inputSchema,
#             }
#             for tool in response.tools
#         ]

#         # Initial Claude API call
#         res = await anthropic_client.messages.create(
#             model="claude-3-7-sonnet-latest",
#             system=self.system_prompt,
#             max_tokens=8000,
#             messages=self.messages,
#             tools=available_tools,
#         )

#         assistant_message_content: list[Union[ToolUseBlock, TextBlock]] = []
#         for content in res.content:
#             if content.type == "text":
#                 assistant_message_content.append(content)
#                 print(content.text)
#             elif content.type == "tool_use":
#                 tool_name = content.name
#                 tool_args = content.input

#                 # Execute tool call
#                 result = await session.call_tool(tool_name, cast(dict, tool_args))

#                 assistant_message_content.append(content)
#                 self.messages.append(
#                     {"role": "assistant", "content": assistant_message_content}
#                 )
#                 self.messages.append(
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "tool_result",
#                                 "tool_use_id": content.id,
#                                 "content": getattr(result.content[0], "text", ""),
#                             }
#                         ],
#                     }
#                 )
#                 # Get next response from Claude
#                 res = await anthropic_client.messages.create(
#                     model="claude-3-7-sonnet-latest",
#                     max_tokens=8000,
#                     messages=self.messages,
#                     tools=available_tools,
#                 )
#                 self.messages.append(
#                     {
#                         "role": "assistant",
#                         "content": getattr(res.content[0], "text", ""),
#                     }
#                 )
#                 print(getattr(res.content[0], "text", ""))

#     async def chat_loop(self, session: ClientSession):
#         while True:
#             query = input("\nQuery: ").strip()
#             self.messages.append(
#                 MessageParam(
#                     role="user",
#                     content=query,
#                 )
#             )

#             await self.process_query(session, query)

#     async def run(self):
#         async with stdio_client(server_params) as (read, write):
#             async with ClientSession(read, write) as session:
#                 # Initialize the connection
#                 await session.initialize()

#                 await self.chat_loop(session)


# chat = Chat()

# asyncio.run(chat.run())



import asyncio
import os
from dataclasses import dataclass, field
from typing import Union, List, Dict

import openai
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",
    args=["./mcp_server.py"],
    env=None,
)

@dataclass
class Chat:
    messages: List[Dict[str, Union[str, List[Dict[str, str]]]]] = field(default_factory=list)
    system_prompt: str = """You are a master MySQL assistant. 
    Your job is to use the tools at your disposal to execute MySQL queries and provide the results to the user."""

    async def process_query(self, session: ClientSession, query: str) -> None:
        # List available tools from the session
        response = await session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        # Append user query to messages
        self.messages.append({"role": "user", "content": query})

        # Initial OpenAI API call
        res = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
            tools=available_tools,
        )

        assistant_message = res.choices[0].message
        assistant_message_content = assistant_message.get("content", "")
        tool_calls = assistant_message.get("tool_calls", [])

        # Add the assistant's message (including tool_calls) to conversation history
        assistant_response = {"role": "assistant"}
        if assistant_message_content:
            assistant_response["content"] = assistant_message_content
        if tool_calls:
            assistant_response["tool_calls"] = tool_calls
        self.messages.append(assistant_response)

        if assistant_message_content:
            print("-------------------------------------",assistant_message_content)

        # Handle tool calls
        if tool_calls:
            for tool_call in tool_calls:
                tool_call_id = tool_call["id"]
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"].get("arguments", {})

                # Ensure tool_args is a dictionary
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse tool arguments: {e}")
                        continue

                # Execute tool call
                result = await session.call_tool(tool_name, tool_args)

                tool_result_content = result.content[0].text if result.content else ""
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": tool_result_content,
                    }
                )

            # Get next response from OpenAI after tool calls
            res = await openai.ChatCompletion.acreate(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
                tools=available_tools,
            )

            assistant_followup_content = res.choices[0].message.get("content", "")
            if assistant_followup_content:
                print(assistant_followup_content)
                self.messages.append({"role": "assistant", "content": assistant_followup_content})

    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in ["exit", "quit"]:
                break
            await self.process_query(session, query)

    async def run(self):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)

# Initialize and run the chat
chat = Chat()
asyncio.run(chat.run())
