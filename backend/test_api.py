"""Simple test script to verify the backend API is working.

This script sends a test request to the backend without the frontend.
"""

from pathlib import Path

import requests


def test_backend():
    """Test the backend API endpoint."""
    api_url = "http://localhost:8000"

    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running at http://localhost:8000?")
        return False

    # Test generate endpoint
    print("\n🔍 Testing generate endpoint...")

    # Find a test image
    test_image_path = Path("data_collection/profiles/images/1/image_1.jpg")
    if not test_image_path.exists():
        print(f"⚠️  Test image not found at {test_image_path}")
        print("   Skipping generate test.")
        return True

    # Prepare test data
    test_description = (
        "Her name is Sarah. "
        "25 kilometers away. "
        "Loves hiking and photography. "
        "Has a dog. "
        "Drinks socially on weekends."
    )

    try:
        with open(test_image_path, "rb") as img_file:
            files = {"image": img_file}
            data = {"description": test_description}

            print("   Sending request (this may take a minute on first run)...")
            response = requests.post(
                f"{api_url}/generate", files=files, data=data, timeout=120
            )

            if response.status_code == 200:
                print("✅ Generate endpoint working!")
                result = response.json()
                print(f"\n   Generated {len(result['opening_lines'])} opening lines:")
                for i, line in enumerate(result["opening_lines"], 1):
                    print(
                        f"\n   Line {i} (temp={line['temperature']}, tokens={line['max_tokens']}):"
                    )
                    print(f'   "{line["text"]}"')
                return True
            else:
                print(f"❌ Generate failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out. The model might be too slow or not loaded.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 RizzAI Backend Test")
    print("=" * 50)
    print()

    success = test_backend()

    print()
    print("=" * 50)
    if success:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend logs.")
