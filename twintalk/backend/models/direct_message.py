"""Direct message conversation models."""

import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.session import Base


class DirectMessageConversation(Base):
    """Two-user direct message conversation."""

    __tablename__ = "direct_message_conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    participant_a_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    participant_b_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    source_community = Column(String(100), default="", comment="Conversation origin community")

    last_message = Column(Text, default="")
    last_message_at = Column(DateTime, nullable=True)

    is_pinned_a = Column(Boolean, default=False)
    is_pinned_b = Column(Boolean, default=False)
    is_archived_a = Column(Boolean, default=False)
    is_archived_b = Column(Boolean, default=False)
    blocked_by_id = Column(String(36), nullable=True)

    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    messages = relationship(
        "DirectMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="DirectMessage.created_at.asc()",
    )


class DirectMessage(Base):
    """A single direct message within a conversation."""

    __tablename__ = "direct_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String(36), ForeignKey("direct_message_conversations.id"), nullable=False
    )
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    sender_mode = Column(
        Enum("user", name="dm_sender_mode"),
        default="user",
        nullable=False,
    )
    content_type = Column(
        Enum("text", "image", "link", "card", name="dm_content_type"),
        default="text",
        nullable=False,
    )
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)

    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("DirectMessageConversation", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_mode": self.sender_mode,
            "content_type": self.content_type,
            "content": self.content,
            "meta_data": self.meta_data or {},
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
