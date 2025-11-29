from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db import models, schemas
from app.adk_client.session_manager import ADKSessionManager


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

    # We no longer rely on persistent ADK sessions.
    # adk_session_id is kept only as a placeholder / metadata if you want.
    chat = models.Chat(
        type=models.ChatType.primary,
        adk_session_id="",  # not used anymore
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
    chat = (
        db.query(models.Chat)
        .filter(models.Chat.id == chat_id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 1) Save user's new message
    user_msg = models.Message(
        chat_id=chat.id,
        role="user",
        content=payload.content,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2) Reload chat with all messages (includes the new user message)
    db.refresh(chat)

    # 3) Build history for ADK from DB messages
    history = [
        {"role": m.role, "content": m.content}
        for m in chat.messages
    ]

    # 4) Call ADK statelessly with full history
    reply_text = adk_manager.send_message(
        chat_type=chat.type.value,
        history=history,
    )

    # 5) Save assistant's reply
    assistant_msg = models.Message(
        chat_id=chat.id,
        role="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)
    db.commit()

    db.refresh(chat)
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

    # Create secondary chat
    chat = models.Chat(
        type=models.ChatType.secondary,
        parent_chat_id=req.parent_chat_id,
        parent_message_id=req.parent_message_id,
        adk_session_id="",  # not used
    )
    
    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Seed system message (hidden in UI)
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
        content=parent_msg.content
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