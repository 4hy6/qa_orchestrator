from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TestRun(Base):
    """
    Stores execution results for analytics and history tracking.
    """

    __tablename__ = "test_runs"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    test_name: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column()
    duration: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=True
    )

    def __repr__(self) -> str:
        return f"<TestRun(test='{self.test_name}', status='{self.status}')>"
