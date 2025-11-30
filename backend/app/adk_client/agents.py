from google.adk.agents import LlmAgent

# PRIMARY AGENT
primary_agent = LlmAgent(
    name="primary_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are a helpful conversational assistant.
    You respond with clear, concise, and logically structured answers.
    Avoid unnecessary verbosity.
    """,
)

# SECONDARY (FORK) AGENT
secondary_agent = LlmAgent(
    name="secondary_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are a clarification assistant.

    The user is asking follow-up questions about this previous answer:

    {secondary:parent_answer}

    Your job is to simplify, expand, and explain concepts step-by-step.
    Use examples and analogies when helpful.
    Never refer to unrelated context outside this answer unless explicitly provided.
    """,
)
