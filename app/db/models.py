from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.db.base import Base


class TestRun(Base):
    """
    Stores execution results for analytics and history tracking.
    """

    __tablename__ = "test_runs"
    __test__ = False

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<TestRun(test='{self.test_name}', status='{self.status}')>"
