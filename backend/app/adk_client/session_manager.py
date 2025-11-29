"""
ADK Session Manager (Stateless per message)
-------------------------------------------

We do NOT persist ADK sessions across requests.

For each user message:
- We take the full chat history (from the DB)
- We build a combined prompt as a single user message
- We create a fresh in-memory ADK session
- We call runner.run(...) once
- We return the final text

Chats and messages are persisted in our database, not in ADK.
"""

import uuid
from typing import Literal, List, Dict

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents import primary_agent, secondary_agent


class ADKSessionManager:
    def __init__(self):
        # One in-memory session service used ONLY per-request
        self.session_service = InMemorySessionService()

        # One runner per agent (primary / secondary)
        self.primary_runner = Runner(
            agent=primary_agent,
            app_name="CoffeeLM",
            session_service=self.session_service,
        )

        self.secondary_runner = Runner(
            agent=secondary_agent,
            app_name="CoffeeLM",
            session_service=self.session_service,
        )

    def _build_prompt_from_history(self, history: List[Dict[str, str]]) -> str:
        """
        Convert a list of {role, content} dicts into a plain-text prompt.

        Example:
        System: ...
        User: ...
        Assistant: ...
        User: <latest question>
        """
        lines = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prefix = "System"
            elif role == "assistant":
                prefix = "Assistant"
            else:
                prefix = "User"

            lines.append(f"{prefix}: {content}")

        return "\n".join(lines)

    def send_message(
        self,
        chat_type: Literal["primary", "secondary"],
        history: List[Dict[str, str]],
    ) -> str:
        """
        Stateless call:
        - history: list of dicts with ['role', 'content'] for this chat
        - returns the assistant's reply text
        """

        if not history:
            raise ValueError("History is empty; cannot send message to ADK.")

        # Build combined prompt from entire history
        full_prompt = self._build_prompt_from_history(history)

        # Fresh session each call
        session_id = str(uuid.uuid4())
        user_id = "user"  # Later you can use real user IDs

        # Create session with empty or minimal state
        self.session_service.create_session(
            app_name="CoffeeLM",
            user_id=user_id,
            session_id=session_id,
            state={},
        )

        # Single user content containing full context
        msg = types.Content(
            role="user",
            parts=[types.Part(text=full_prompt)],
        )

        # Choose runner based on chat type
        runner = (
            self.primary_runner if chat_type == "primary" else self.secondary_runner
        )

        final_text = ""

        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=msg,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_text = event.content.parts[0].text or ""

        if final_text:
            final_text = final_text.strip()
            # Remove agent prefixes if present
            for agent_name in ["primary_agent:", "secondary_agent:", "Assistant:"]:
                if final_text.lower().startswith(agent_name):
                    final_text = final_text[len(agent_name):].strip()

        return final_text
