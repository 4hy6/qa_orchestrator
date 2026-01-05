from sqlalchemy.orm import Session

from app.db.models import TestRun


def test_db_connection_and_write(db_session: Session) -> None:
    test_name = "Internal_DB_Check"
    status = "OK"

    # Verify write operation
    new_run = TestRun(test_name=test_name, status=status, duration=0.001)
    db_session.add(new_run)
    db_session.commit()

    # Verify read operation
    saved_run = db_session.query(TestRun).filter_by(test_name=test_name).first()

    assert saved_run is not None
    assert saved_run.status == status
    assert saved_run.id is not None

    # Teardown: Clean up synthetic data to avoid polluting metrics
    db_session.delete(saved_run)
    db_session.commit()
