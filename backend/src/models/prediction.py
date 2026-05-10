"""
Prediction ORM model.

Stores disease prediction results
with full input/output data for audit and history tracking.
"""

import enum
from typing import Any

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin


class PredictionType(enum.StrEnum):
    """Enumeration of supported prediction types."""

    DISEASE = "disease"


class Prediction(UUIDMixin, TimestampMixin, Base):
    """
    Prediction history model.

    each prediction made by a user.
    """

    __tablename__ = "predictions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_type: Mapped[PredictionType] = mapped_column(
        Enum(PredictionType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    input_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    result: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationship back to user
    user = relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        return (
            f"<Prediction(id={self.id}, type={self.prediction_type}, "
            f"confidence={self.confidence})>"
        )
