from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.db.base import Base


class TestRun(Base):
    """
    Model representing a single execution of a test case.
    Stores the result, duration, and timestamp for analytics.
    """

    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)  # e.g., "PASS", "FAIL", "BROKEN"
    duration = Column(Float, nullable=False)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TestRun(test='{self.test_name}', status='{self.status}')>"
