import logging
from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Setup logger for tracing the agents' progress
logger = logging.getLogger(__name__)

# Define the sub-agents with specialized instructions and output keys.
# They will use the curly-brace '{competitor}' placeholder to refer to the
# competitor state variable injected from the session state.

price_analyst = Agent(
    name="price_analyst",
    model="gemini-2.5-flash",
    instruction=(
        "You are a professional price analyst. Gather and analyze the pricing structure of "
        "the competitor product: {competitor}. Identify their pricing plans, tiering details, "
        "subscription models, target pricing, discounts, and value-for-money metrics. "
        "Use the google_search tool to find pricing pages, review blogs, or articles discussing their cost."
    ),
    tools=[google_search],
    output_key="price_insights"
)

sentiment_analyst = Agent(
    name="sentiment_analyst",
    model="gemini-2.5-flash",
    instruction=(
        "You are a professional sentiment analyst. Gather and analyze public sentiment, user reviews, "
        "satisfaction rates, major pain points, common complaints, and praised features for the "
        "competitor product: {competitor}. Use the google_search tool to look for user reviews "
        "on platforms like G2, Capterra, Reddit, Trustpilot, or industry forums."
    ),
    tools=[google_search],
    output_key="sentiment_insights"
)

marketing_analyst = Agent(
    name="marketing_analyst",
    model="gemini-2.5-flash",
    instruction=(
        "You are a professional marketing and brand analyst. Gather and analyze the marketing strategies, "
        "unique value propositions, target audience, acquisition channels, key features, and product "
        "messaging of the competitor product: {competitor}. Use the google_search tool to inspect "
        "their website, landing pages, marketing campaigns, blogs, and press releases."
    ),
    tools=[google_search],
    output_key="marketing_insights"
)

# Define the orchestrator ParallelAgent to execute all three analysts concurrently.
market_analyst_group = ParallelAgent(
    name="market_analyst_group",
    sub_agents=[price_analyst, sentiment_analyst, marketing_analyst]
)


async def run_market_analysis(competitor: str, is_website: bool) -> dict:
    """
    Executes the market analysis workflow programmatically.
    
    1. Initializes an in-memory session service.
    2. Seeds the session state with the competitor information.
    3. Runs the ParallelAgent via the Runner and consumes the execution event stream.
    4. Retrieves and returns the final insights from the session state.
    """
    session_service = InMemorySessionService()
    
    # Initialize session with the competitor variable in state
    session = await session_service.create_session(
        app_name="market-insights",
        user_id="system",
        state={
            "competitor": competitor,
            "is_website": is_website
        }
    )
    
    # Initialize the Runner with our ParallelAgent
    runner = Runner(
        agent=market_analyst_group,
        app_name="market-insights",
        session_service=session_service
    )
    
    # Create the user message initiating the run
    input_type = "website URL" if is_website else "product name"
    query_text = f"Perform a comprehensive market insights analysis for the competitor ({input_type}): {competitor}"
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query_text)]
    )
    
    logger.info(f"Starting parallel market insights analysis for competitor: {competitor} ({input_type})")
    
    # Run the ParallelAgent and consume the stream to drive execution to completion
    try:
        async for event in runner.run_async(
            user_id="system",
            session_id=session.id,
            new_message=content
        ):
            # Log intermediate events for debugging / visibility
            if hasattr(event, 'content') and event.content and event.content.parts:
                part_text = "".join(part.text for part in event.content.parts if hasattr(part, 'text') and part.text)
                if part_text:
                    logger.debug(f"[Agent Event] {event.author or 'system'}: {part_text[:100]}...")
            elif hasattr(event, 'is_final_response') and event.is_final_response():
                logger.info("ParallelAgent completed execution stream.")
    except Exception as e:
        logger.error(f"Error during parallel agent execution: {str(e)}", exc_info=True)
        raise e

    # Retrieve the updated session containing the outputs populated by each sub-agent
    updated_session = await session_service.get_session(
        app_name="market-insights",
        user_id="system",
        session_id=session.id
    )
    
    # Extract outputs from the session state
    results = {
        "price_insights": updated_session.state.get("price_insights"),
        "sentiment_insights": updated_session.state.get("sentiment_insights"),
        "marketing_insights": updated_session.state.get("marketing_insights")
    }
    
    logger.info("Market analysis results successfully gathered from session state.")
    return results
