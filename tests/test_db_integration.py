from sqlalchemy.orm import Session

from app.db.models import TestRun


def test_db_connection_and_write(db_session: Session):
    """
    INTERNAL TEST: Verifies that the Orchestrator can talk to the Database.
    This ensures that our reporting mechanism is functional.
    """
    test_name = "Internal_DB_Check"
    status = "OK"
    duration = 0.001

    new_run = TestRun(test_name=test_name, status=status, duration=duration)
    db_session.add(new_run)
    db_session.commit()

    saved_run = db_session.query(TestRun).filter_by(test_name=test_name).first()

    assert saved_run is not None, "Data was not saved to DB!"
    assert saved_run.status == status
    assert saved_run.id is not None

    db_session.delete(saved_run)
    db_session.commit()
