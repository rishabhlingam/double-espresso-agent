from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db import models, schemas
from app.adk_client.session_manager import ADKSessionManager

from app.observability.metrics import inc

router = APIRouter(prefix="/chats", tags=["chats"])
adk_manager = ADKSessionManager()


# ------------------------------------------------------
# DB Dependency
# ------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------
# Create PRIMARY chat
# ------------------------------------------------------
@router.post("/", response_model=schemas.ChatRead)
def create_primary_chat(db: Session = Depends(get_db)):
    """
    Create a new PRIMARY chat and a matching ADK session.

    - One Chat row <-> one ADK session (stored in Chat.adk_session_id).
    - The ADK session is persisted via DatabaseSessionService.
    """

    user_id = "user"  # TODO: wire this to real authenticated user if needed

    # Create ADK session first
    adk_session_id = adk_manager.create_session(
        chat_type="primary",
        user_id=user_id,
        initial_state={},  # can be extended later if needed
    )

    # Create Chat row with the ADK session ID
    chat = models.Chat(
        type=models.ChatType.primary,
        adk_session_id=adk_session_id,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


# ------------------------------------------------------
# Send a message to ANY chat (primary or secondary)
# ------------------------------------------------------
@router.post("/{chat_id}/messages", response_model=schemas.ChatRead)
def send_message(
    chat_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
):
    """
    Send a user message into an existing chat.

    Flow:
    1) Load Chat row (has type + adk_session_id).
    2) Ensure the chat has an ADK session (create lazily if needed for legacy rows).
    3) Save user message to DB.
    4) Call ADK using the existing session_id.
    5) Save assistant reply to DB.
    6) Return updated Chat with messages.
    """

    chat = (
        db.query(models.Chat)
        .filter(models.Chat.id == chat_id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_id = "user"  # TODO: real user ID if you have auth

    # Backward compatibility / safety:
    # If old rows exist with empty adk_session_id, create a session now.
    if not chat.adk_session_id:
        chat.adk_session_id = adk_manager.create_session(
            chat_type=chat.type.value,
            user_id=user_id,
            initial_state={},
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # 1) Save user's new message in DB
    user_msg = models.Message(
        chat_id=chat.id,
        role="user",
        content=payload.content,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    inc("messages.user") 
    inc(f"messages.user.{chat.type.value}") 

    # 2) Call ADK with ONLY the latest user message,
    #    letting the session carry context via events/state.
    reply_text = adk_manager.send_message(
        chat_type=chat.type.value,
        session_id=chat.adk_session_id,
        text=payload.content,
        user_id=user_id,
    )

    # 3) Save assistant's reply in DB
    assistant_msg = models.Message(
        chat_id=chat.id,
        role="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(chat)

    inc("messages.assistant")
    inc(f"messages.assistant.{chat.type.value}")

    return chat


# ------------------------------------------------------
# Get chat + messages
# ------------------------------------------------------
@router.get("/{chat_id}", response_model=schemas.ChatRead)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = (
        db.query(models.Chat)
        .filter(models.Chat.id == chat_id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat


# ------------------------------------------------------
# Create OR get a SECONDARY (forked) chat
# ------------------------------------------------------
@router.post("/fork", response_model=schemas.ChatRead)
def create_or_get_secondary_chat(
    req: schemas.ForkRequest,
    db: Session = Depends(get_db),
):
    """
    Secondary chats are clarification threads attached to a specific
    parent message in a primary chat.

    - We ensure at most 1 secondary chat per parent_message_id.
    - When creating a new secondary chat:
        * We create a NEW ADK session for the secondary agent.
        * We initialize session.state["secondary:parent_answer"] with the
          content of the parent message (usually an assistant answer).
        * The secondary agent instruction uses {secondary:parent_answer}
          so it always has access to that answer.
        * We also seed DB messages so the UI shows the original answer.
    """

    # Validate parent message
    parent_msg = (
        db.query(models.Message)
        .filter(
            models.Message.id == req.parent_message_id,
            models.Message.chat_id == req.parent_chat_id,
        )
        .first()
    )

    if not parent_msg:
        raise HTTPException(status_code=404, detail="Parent message not found")

    # Check if a fork already exists for this message
    existing = (
        db.query(models.Chat)
        .filter(models.Chat.parent_message_id == req.parent_message_id)
        .first()
    )

    if existing:
        return existing

    user_id = "user"  # TODO: real user id

    # Create ADK session for the SECONDARY chat with initial state
    # containing the parent answer.
    initial_state = {
        "secondary:parent_answer": parent_msg.content,
    }
    adk_session_id = adk_manager.create_session(
        chat_type="secondary",
        user_id=user_id,
        initial_state=initial_state,
    )

    # Create secondary chat row
    chat = models.Chat(
        type=models.ChatType.secondary,
        parent_chat_id=req.parent_chat_id,
        parent_message_id=req.parent_message_id,
        adk_session_id=adk_session_id,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Seed system message (hidden in UI, but kept for clarity).
    seed_msg = models.Message(
        chat_id=chat.id,
        role="system",
        content=(
            "The user is asking follow-up questions about this previous answer:\n\n"
            f"{parent_msg.content}\n\n"
            "Explain concepts in simpler, step-by-step detail."
        ),
    )
    db.add(seed_msg)
    db.commit()

    # Insert the actual assistant message INTO the forked chat (visible to the user)
    original_assistant_msg = models.Message(
        chat_id=chat.id,
        role="assistant",
        content=parent_msg.content,
    )
    db.add(original_assistant_msg)
    db.commit()

    db.refresh(chat)
    return chat


# ------------------------------------------------------
# Get all chats
# ------------------------------------------------------
@router.get("/", response_model=List[schemas.ChatRead])
def get_all_chats(db: Session = Depends(get_db)):
    return (
        db.query(models.Chat)
        .filter(models.Chat.type == models.ChatType.primary)
        .order_by(models.Chat.id.desc())
        .all()
    )

@router.get("/metrics")
def get_metrics_endpoint():
    from app.observability.metrics import get_metrics
    return get_metrics()