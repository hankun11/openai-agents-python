# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel
import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.model_settings import ModelSettings

PROMPT = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research "
    "assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""

    follow_up_questions: list[str]
    """Suggested topics to research further"""


# Configure the model based on environment variables
def get_writer_model():
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if deepseek_api_key:
        # Use DeepSeek API with modified settings
        deepseek_client = AsyncOpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com/v1",  # Replace with actual DeepSeek API endpoint
        )
        # Create model settings that don't use json_schema response format
        model_settings = ModelSettings(
            response_format=None  # Disable response_format for DeepSeek
        )
        return OpenAIChatCompletionsModel(
            model="deepseek-reasoner",  # Replace with actual DeepSeek model name
            openai_client=deepseek_client,
        ), model_settings
    else:
        # Use default OpenAI configuration
        return "o3-mini", None

model, custom_settings = get_writer_model()
writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model=model,
    model_settings=custom_settings if custom_settings else ModelSettings(),
    output_type=ReportData,
)
