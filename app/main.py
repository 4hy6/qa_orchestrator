import platform
import sys

from app.schemas.run_test import TestRunRequest


def main() -> None:
    """
    Entry point for the QA Orchestrator sanity check.
    Validates environment and imports.
    """
    python_version: str = sys.version.split()[0]
    os_info: str = platform.platform()

    print("--- QA Orchestrator Environment Diagnostic ---")
    print(f"Host OS Kernel:     {os_info}")
    print(f"Python Version:     {python_version}")
    print(f"Executable Path:    {sys.executable}")

    try:
        sample_request = TestRunRequest(
            test_suite="smoke_tests",
            browser="chrome",
            retries=2,
            headless=True,
        )

        print("\n[SUCCESS] Pydantic Model Loaded:")
        print(f" -> Suite:   {sample_request.test_suite}")
        print(f" -> Browser: {sample_request.browser.value}")
        print(f" -> Retries: {sample_request.retries}")
        print(f" -> Headless:{sample_request.headless}")

    except Exception as e:
        print(f"\n[ERROR] Model Validation Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
