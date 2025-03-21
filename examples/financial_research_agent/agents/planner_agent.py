from pydantic import BaseModel
from datetime import datetime

from agents import Agent

# Generate a plan of searches to ground the financial analysis.
# For a given financial question or company, we want to search for
# recent news, official filings, analyst commentary, and other
# relevant background.
PROMPT = (
    "You are a financial research planner. Today is {current_date}. Given a request for financial analysis, "
    "generate a set of targeted web searches to gather the context needed. Aim for recent "
    "headlines, earnings calls or 10‑K/10-Q snippets, analyst commentary, and industry background. "
    "Provide between 5 and 15 search terms to query for."
    "Examples of useful queries for stock XYZ include, but are not limited to:"
    "XYZ latest earnings call transcript"
    "XYZ SEC filing 10-K or 10-Q highlights"
    "Recent statements from XYZ CEO"
    "XYZ recent trending news"
    "Analyst price targets for XYZ"
)


class FinancialSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""


class FinancialSearchPlan(BaseModel):
    searches: list[FinancialSearchItem]
    """A list of searches to perform."""


def get_planner_instructions(context, agent):
    current_date = datetime.now().strftime("%B %d, %Y")
    return PROMPT.format(current_date=current_date)

planner_agent = Agent(
    name="PlannerAgent",
    instructions=get_planner_instructions,
    model="gpt-4o",
    output_type=FinancialSearchPlan,
)
