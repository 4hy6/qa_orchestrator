import platform
import sys

from app.schemas import ContentType, HttpMethod


def main() -> None:
    """
    Entry point for the application sanity checks.
    """
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")

    # Verify Enums usage
    print("\n--- HTTP Constants Check ---")
    print(f"Method: {HttpMethod.POST} (Type: {type(HttpMethod.POST)})")
    print(f"Header: {ContentType.JSON}")

    # Demonstration of equality check
    if HttpMethod.GET == "GET":
        print("SUCCESS: StrEnum works as a string.")
    else:
        print("ERROR: StrEnum implementation is incorrect.")


if __name__ == "__main__":
    main()
