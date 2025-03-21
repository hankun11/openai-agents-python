from __future__ import annotations

import asyncio
import time

from rich.console import Console

from agents import Runner, custom_span, gen_trace_id, trace

from .agents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from .agents.search_agent import search_agent
from .agents.writer_agent import ReportData, writer_agent
from .printer import Printer

from agents import AsyncOpenAI
import os


deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key=deepseek_api_key)
# perplexity_client = AsyncOpenAI(base_url="https://api.perplexity.ai/chat/completions", api_key=perplexity_api_key)
#claude_client = AsyncOpenAI(base_url="https://api.anthropic.com/v1/", api_key=claude_api_key)
# gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=gemini_api_key)
#huggingface_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=hf_api_key)


from agents import Agent, OpenAIChatCompletionsModel ,OpenAIResponsesModel


deepseek_agent = Agent(
    name="Deepseek agent",
    instructions="You only respond to queries about code refactoring queries.",
    model=OpenAIChatCompletionsModel( 
        model="deepseek-chat",
        openai_client=deepseek_client,
    ),
)


bugs_agent = Agent(
    name="Deepseek agent",
    instructions="You only respond to queries about bugs detection.",
    model=OpenAIChatCompletionsModel( 
        model="deepseek-chat",
        openai_client=deepseek_client,
    ),
)

documentation_agent = Agent(
    name="Perplexity agent",
    instructions="You only respond to queries about documentation search.",
    model=OpenAIChatCompletionsModel( 
        model="deepseek-chat",
        openai_client=deepseek_client,
    ),
)

code_refactoring_agent = Agent(
    name="Claude agent",
    instructions="You only respond to queries about code refactoring queries.",
    model=OpenAIChatCompletionsModel( 
        model="deepseek-chat",
        openai_client=deepseek_client,
    ),
)

triage_agent = Agent(
    name="Openai agent",
    instructions="Handoff to the appropriate agent based on the user query.",
    handoffs=[bugs_agent, documentation_agent, code_refactoring_agent],
    model="deepseek-chat",
)

messy_code = """
a = "a"
b = "b"
c = "c"
l = [a, b, c]
"""

result = await Runner.run(triage_agent, input=f"Refactor the following code:\n{messy_code}")
print(result.final_output)