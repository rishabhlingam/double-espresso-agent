from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
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
def create_primary_chat(
    db: Session = Depends(get_db),
    x_user_api_key: str = Header(None, alias="x-user-api-key"),
):
    """
    Create a new PRIMARY chat and matching ADK session.
    """

    if not x_user_api_key:
        raise HTTPException(400, "Missing x-user-api-key header")

    user_id = "user"  # demo mode

    # Create ADK session with the user's API key
    adk_session_id = adk_manager.create_session(
        chat_type="primary",
        user_id=user_id,
        initial_state={},
        api_key=x_user_api_key,
    )

    chat = models.Chat(
        type=models.ChatType.primary,
        adk_session_id=adk_session_id,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


# ------------------------------------------------------
# Send a message
# ------------------------------------------------------
@router.post("/{chat_id}/messages", response_model=schemas.ChatRead)
def send_message(
    chat_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    x_user_api_key: str = Header(None, alias="x-user-api-key"),
):
    """
    Send a user message into an existing chat.
    """

    if not x_user_api_key:
        raise HTTPException(400, "Missing x-user-api-key header")

    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_id = "user"

    # Safety: create session if missing
    if not chat.adk_session_id:
        chat.adk_session_id = adk_manager.create_session(
            chat_type=chat.type.value,
            user_id=user_id,
            initial_state={},
            api_key=x_user_api_key,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # Save user message in DB
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

    # Call ADK with THIS user's API key
    reply_text = adk_manager.send_message(
        chat_type=chat.type.value,
        session_id=chat.adk_session_id,
        text=payload.content,
        user_id=user_id,
        api_key=x_user_api_key,
    )

    # Save assistant reply in DB
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
# Get chat
# ------------------------------------------------------
@router.get("/{chat_id}", response_model=schemas.ChatRead)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


# ------------------------------------------------------
# Create or get SECONDARY chat
# ------------------------------------------------------
@router.post("/fork", response_model=schemas.ChatRead)
def create_or_get_secondary_chat(
    req: schemas.ForkRequest,
    db: Session = Depends(get_db),
    x_user_api_key: str = Header(None, alias="x-user-api-key"),
):
    """
    Secondary chat with parent context.
    """

    if not x_user_api_key:
        raise HTTPException(400, "Missing x-user-api-key header")

    # Validate parent
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

    # Check existing fork
    existing = (
        db.query(models.Chat)
        .filter(models.Chat.parent_message_id == req.parent_message_id)
        .first()
    )
    if existing:
        return existing

    user_id = "user"

    initial_state = {
        "secondary:parent_answer": parent_msg.content,
    }

    adk_session_id = adk_manager.create_session(
        chat_type="secondary",
        user_id=user_id,
        initial_state=initial_state,
        api_key=x_user_api_key,
    )

    chat = models.Chat(
        type=models.ChatType.secondary,
        parent_chat_id=req.parent_chat_id,
        parent_message_id=req.parent_message_id,
        adk_session_id=adk_session_id,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Seed system message
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

    # Copy original assistant message
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


# ------------------------------------------------------
# Metrics endpoint
# ------------------------------------------------------
@router.get("/metrics")
def get_metrics_endpoint():
    from app.observability.metrics import get_metrics
    return get_metrics()
