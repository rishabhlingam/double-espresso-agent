"""
Defines the two main Google ADK agents:
- primary_agent    : used for the normal/main chat
- secondary_agent  : used for forked/clarification chats
"""

from google.adk.agents import LlmAgent


# ----------------------------------------------------
# PRIMARY AGENT
# ----------------------------------------------------
primary_agent = LlmAgent(
    name="primary_agent",
    model="gemini-2.0-flash",   # you can change this later
    instruction="""
You are a helpful conversational assistant.
You respond with clear, concise, and logically structured answers.
Avoid unnecessary verbosity.
""",
)


# ----------------------------------------------------
# SECONDARY (FORK) AGENT
# ----------------------------------------------------
secondary_agent = LlmAgent(
    name="secondary_agent",
    model="gemini-2.0-flash",   # same model for now
    instruction="""
You are a clarification assistant.
The user is asking follow-up questions about a previous answer.
Your job is to simplify, expand, and explain concepts step-by-step.
Use examples and analogies when helpful.
Never refer to the original conversation unless explicitly provided.
""",
)
