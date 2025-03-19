import os
import pytest
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Runner, Agent, RunConfig
from agents.model_settings import ModelSettings
from examples.research_bot.agents.writer_agent import ReportData
from tests.fake_model import FakeModel
from agents.tool import function_tool
from  .test_responses import get_text_message


# Mock the writer agent configuration for testing
@pytest.fixture
def mock_writer_agent():
    # Use set_structured_output tool to indicate this is a final output
    fake_model = FakeModel([{
        "role": "assistant",
        "content": None,  # content should be None when using tool calls
        "tool_calls": [{
            "type": "function",
            "function": {
                "name": "set_structured_output",  # Special tool to set final output
                "arguments": '{"summary": "Test summary", "key_findings": ["Finding 1", "Finding 2"], "follow_up_questions": ["Question 1?"]}'
            }
        }]
    }])
    
    return Agent(
        name="WriterAgent",
        instructions="Test instructions",
        model=fake_model,
        output_type=ReportData
    )

@pytest.mark.asyncio
async def test_writer_agent_model_selection(mocker):
    # Mock AsyncOpenAI client
    mock_client = mocker.Mock(spec=AsyncOpenAI)
    mocker.patch('agents.AsyncOpenAI', return_value=mock_client)
    
    # Test OpenAI model selection (default case)
    os.environ.pop('DEEPSEEK_API_KEY', None)  # Ensure DEEPSEEK_API_KEY is not set
    model = OpenAIChatCompletionsModel(
        model="o3-mini",
        openai_client=mock_client
    )
    assert isinstance(model, OpenAIChatCompletionsModel)
    assert model.model == "o3-mini"

@pytest.mark.asyncio
async def test_writer_agent_deepseek_model_selection(mocker):
    # Mock AsyncOpenAI client
    mock_client = mocker.Mock(spec=AsyncOpenAI)
    mocker.patch('agents.AsyncOpenAI', return_value=mock_client)
    
    # Test DeepSeek model selection
    os.environ['DEEPSEEK_API_KEY'] = 'test_key'
    model = OpenAIChatCompletionsModel(
        model="deepseek-reasoner",
        openai_client=mock_client
    )
    assert isinstance(model, OpenAIChatCompletionsModel)
    assert model.model == "deepseek-reasoner"
    os.environ.pop('DEEPSEEK_API_KEY')  # Clean up

@pytest.mark.asyncio
async def test_writer_agent_output(mock_writer_agent):
    run_config = RunConfig(
        tracing_disabled=True,
        model_settings=None
    )
    
    result = await Runner.run(
        mock_writer_agent, 
        "Test research data about AI",
        run_config=run_config,
        max_turns=1
    )
    
    assert isinstance(result.final_output, ReportData)
    assert result.final_output.summary == "Test summary"
    assert result.final_output.key_findings == ["Finding 1", "Finding 2"]
    assert result.final_output.follow_up_questions == ["Question 1?"] 