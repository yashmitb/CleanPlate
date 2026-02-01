import requests
import json

BASE_URL = "http://localhost:5001"  # Using port 5001 as seen in server output

print("Testing CleanPlate API Endpoints\n")
print("=" * 50)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Create a test user
print("\n2. Creating test user...")
try:
    response = requests.post(
        f"{BASE_URL}/api/user/create",
        json={"user_id": "test_user_123", "user_name": "Test User"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Get recommendations (should be empty for new user)
print("\n3. Testing /api/user/test_user_123/recommendations...")
try:
    response = requests.get(f"{BASE_URL}/api/user/test_user_123/recommendations?limit=5")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result.get('success')}")
    print(f"   Count: {result.get('count')}")
    if result.get('recommendations'):
        print(f"   Sample recommendation: {json.dumps(result['recommendations'][0], indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Get dislikes (should be empty for new user)
print("\n4. Testing /api/user/test_user_123/dislikes...")
try:
    response = requests.get(f"{BASE_URL}/api/user/test_user_123/dislikes")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result.get('success')}")
    print(f"   Count: {result.get('count')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Add some preferences via waste analysis
print("\n5. Updating user preferences with sample waste analysis...")
sample_analysis = {
    "user_id": "test_user_123",
    "waste_analysis": {
        "original_meal": {
            "name": "Chicken and Rice Bowl",
            "description": "Grilled chicken with rice and vegetables"
        },
        "thrown_away": [
            {"item": "broccoli", "quantity": "1/2 cup", "percentage_of_original": "50%"},
            {"item": "carrots", "quantity": "1/4 cup", "percentage_of_original": "30%"}
        ],
        "eaten": [
            {"item": "chicken", "quantity": "6 oz", "percentage_of_original": "100%"},
            {"item": "rice", "quantity": "1 cup", "percentage_of_original": "90%"}
        ],
        "food_preferences": {
            "likely_dislikes": ["broccoli", "carrots"],
            "likely_likes": ["chicken", "rice"],
            "insights": "User prefers protein and grains over vegetables"
        },
        "waste_summary": {
            "total_waste_percentage": "25%",
            "waste_value": "low"
        }
    }
}

try:
    response = requests.post(
        f"{BASE_URL}/api/user/preferences/update",
        json=sample_analysis
    )
    print(f"   Status: {response.status_code}")
    print(f"   Success: {response.json().get('success')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 6: Get recommendations again (should have data now)
print("\n6. Testing recommendations after adding preferences...")
try:
    response = requests.get(f"{BASE_URL}/api/user/test_user_123/recommendations?limit=5")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result.get('success')}")
    print(f"   Count: {result.get('count')}")
    if result.get('recommendations'):
        print(f"   Recommendations:")
        for rec in result['recommendations']:
            print(f"      - {rec['name']}: {rec['match_percentage']}% match ({rec['confidence']} confidence)")
except Exception as e:
    print(f"   Error: {e}")

# Test 7: Get dislikes
print("\n7. Testing dislikes after adding preferences...")
try:
    response = requests.get(f"{BASE_URL}/api/user/test_user_123/dislikes")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result.get('success')}")
    print(f"   Count: {result.get('count')}")
    if result.get('dislikes'):
        print(f"   Dislikes:")
        for dislike in result['dislikes']:
            print(f"      - {dislike['name']} (frequency: {dislike['frequency']}, category: {dislike['category']})")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("Testing complete!")
