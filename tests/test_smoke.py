from app.schemas import HttpMethod


def test_health_check():
    """
    Smoke test to verify pytest integration.
    Always passes if environment is set up correctly.
    """
    assert True


def test_core_imports():
    """
    Verify that app modules can be imported in tests.
    """
    assert HttpMethod.GET == "GET"
