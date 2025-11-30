import logging
import os
from contextlib import contextmanager
from typing import Literal, Optional

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app.observability.metrics import inc
from .agents import primary_agent, secondary_agent
from app.config import settings

logger = logging.getLogger("adk")
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)

APP_NAME = "DoubleEspressoAgent"

# ADK session storage Databse
SESSION_DB_URL = settings.adk_session_db_url

# Temporary override for GOOGLE_API_KEY (per request)
@contextmanager
def temporary_google_api_key(api_key: str):
    """
    Temporarily override GOOGLE_API_KEY for the duration of the ADK call.
    Restores the previous value after completion.

    This allows each user to use their own Gemini API key in demo mode.
    """
    old_value = os.environ.get("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = api_key
    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop("GOOGLE_API_KEY", None)
        else:
            os.environ["GOOGLE_API_KEY"] = old_value


class ADKSessionManager:
    def __init__(self):
        # Persistent session service
        self.session_service = DatabaseSessionService(db_url=SESSION_DB_URL)

        # Base runners
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

    # SESSION CREATION
    def create_session(
        self,
        chat_type: Literal["primary", "secondary"],
        user_id: str = "user",
        initial_state: Optional[dict] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """
        Creates a new ADK session and returns its session_id.
        """
        logger.info(f"[ADK] Creating session for chat_type={chat_type} user={user_id}")

        # Creating session does NOT call Gemini. api_key is optional.
        session = self.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=initial_state or {},
        )

        logger.info(f"[ADK] New session created: session_id={session.id}")
        return session.id

    # MESSAGE SEND
    def send_message(
        self,
        chat_type: Literal["primary", "secondary"],
        session_id: str,
        text: str,
        user_id: str = "user",
        api_key: Optional[str] = None,
    ) -> str:
        """
        Sends a single user message into an EXISTING ADK session.
        """

        if not session_id:
            raise ValueError("session_id is empty; each chat must have an ADK session ID.")

        if not api_key:
            raise ValueError("Missing API key for ADK call")

        msg = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )

        # Selecting appropiate agent based on request
        runner = (
            self.primary_runner if chat_type == "primary" else self.secondary_runner
        )

        final_text = ""

        logger.info(
            f"[ADK] Sending message to {chat_type}_agent | session={session_id} | text={text[:80]}"
        )

        inc("agent.calls")
        inc(f"agent.calls.{chat_type}")

        # Run the LLM with THIS USER'S API KEY temporarily
        with temporary_google_api_key(api_key):
            
            for event in runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=msg,
            ):
                logger.info(
                    "[ADK EVENT] id=%s author=%s partial=%s is_final=%s",
                    event.id,
                    event.author,
                    event.partial,
                    event.is_final_response(),
                )
                if event.is_final_response():
                    if event.content and event.content.parts:
                        part = event.content.parts[0]
                        if part and part.text:
                            final_text = part.text or ""

        # Cleanup output formatting
        if final_text:
            final_text = final_text.strip()
            for prefix in ["primary_agent:", "secondary_agent:", "Assistant:"]:
                if final_text.lower().startswith(prefix.lower()):
                    final_text = final_text[len(prefix):].strip()

        logger.info(
            f"[ADK] Final response from {chat_type}_agent | session={session_id} | reply={final_text[:80]}"
        )
        return final_text
