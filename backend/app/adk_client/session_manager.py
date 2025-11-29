"""
ADK Session Manager (Stateful per chat)
---------------------------------------

New behavior:

- Each Chat row in the DB has a single ADK session ID (adk_session_id).
- We use DatabaseSessionService so that sessions (events + state) persist across
  application restarts.
- When the user sends a message:
    * We reuse the existing session_id from the Chat record.
    * We send ONLY the new user message to ADK.
    * The Runner loads full conversation context from the session (events + state).

For SECONDARY chats:
- We create the ADK session with initial state containing the parent answer:
    state["secondary:parent_answer"] = <parent_msg.content>
- The secondary agent instruction uses {secondary:parent_answer} templating.
"""

from typing import Literal, Optional

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from .agents import primary_agent, secondary_agent


APP_NAME = "CoffeeLM"

# ADK will store its own session tables here.
# This is separate from your SQLAlchemy chat.db and is managed by ADK itself.
SESSION_DB_URL = "sqlite:///./adk_sessions.db"


class ADKSessionManager:
    def __init__(self):
        # Persistent session service (sessions survive restarts)
        self.session_service = DatabaseSessionService(db_url=SESSION_DB_URL)

        # One runner per agent (primary / secondary), both sharing the same
        # session_service so they can load and update sessions.
        self.primary_runner = Runner(
            agent=primary_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

        self.secondary_runner = Runner(
            agent=secondary_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    # ------------------------------------------------------------------
    # SESSION CREATION
    # ------------------------------------------------------------------
    def create_session(
        self,
        chat_type: Literal["primary", "secondary"],
        user_id: str = "user",
        initial_state: Optional[dict] = None,
    ) -> str:
        """
        Create a new ADK session for a chat and return its session_id.

        - chat_type: "primary" or "secondary" (used only to pick runner if needed).
        - initial_state: dict that becomes session.state at creation time.
          This is where we can inject things like a parent answer for secondary chats.
        """
        # We don't actually need the runner here to create a session; we just use
        # the shared session_service.
        session = self.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=initial_state or {},
        )
        return session.id

    # ------------------------------------------------------------------
    # MESSAGE SEND (STATEFUL)
    # ------------------------------------------------------------------
    def send_message(
        self,
        chat_type: Literal["primary", "secondary"],
        session_id: str,
        text: str,
        user_id: str = "user",
    ) -> str:
        """
        Send a single user message into an EXISTING ADK session.

        - chat_type: "primary" or "secondary" -> selects which agent/runner to use
        - session_id: the ADK session ID stored in the Chat row
        - text: the latest user message (not full history)

        The Runner:
        - Loads the session (events + state) from DatabaseSessionService.
        - Appends this new user message as an event.
        - Lets the agent respond.
        - Saves updated events/state back to the DB automatically.
        """

        if not session_id:
            raise ValueError("session_id is empty; each chat must have an ADK session ID.")

        # Single user content representing ONLY the latest user message.
        msg = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )

        # Choose runner based on chat type
        runner = (
            self.primary_runner if chat_type == "primary" else self.secondary_runner
        )

        final_text = ""

        # Run the agent in the context of this existing session
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=msg,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    part = event.content.parts[0]
                    if part and part.text:
                        final_text = part.text or ""

        if final_text:
            final_text = final_text.strip()
            # Remove agent prefixes if present
            for agent_name in ["primary_agent:", "secondary_agent:", "Assistant:"]:
                lower_prefix = agent_name.lower()
                if final_text.lower().startswith(lower_prefix):
                    final_text = final_text[len(agent_name):].strip()

        return final_text
