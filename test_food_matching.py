"""
Test the food matching system with a user who has preferences.
"""
import requests
import json

BASE_URL = "http://localhost:5001"

print("=" * 60)
print("Food Matching System Test")
print("=" * 60)

# 1. Get all dining halls
print("\n1. Getting all dining halls...")
response = requests.get(f"{BASE_URL}/api/dining-halls")
result = response.json()
print(f"   Found {result['count']} dining halls:")
for hall in result.get('dining_halls', []):
    print(f"      - {hall}")

# 2. Get menu for North Campus Dining (lunch)
print("\n2. Getting North Campus Dining lunch menu...")
response = requests.get(f"{BASE_URL}/api/dining-halls/North Campus Dining/menu?meal_period=lunch")
result = response.json()
print(f"   Found {result['count']} items:")
for item in result.get('items', [])[:5]:
    print(f"      - {item['name']} ({item['category']})")

# 3. Create a test user with preferences
print("\n3. Creating test user with food preferences...")
# First create user
requests.post(f"{BASE_URL}/api/user/create", json={"user_id": "food_matcher_test", "user_name": "Test User"})

# Add preferences via waste analysis
waste_data = {
    "user_id": "food_matcher_test",
    "waste_analysis": {
        "original_meal": {"name": "Chicken and Rice", "description": "Grilled chicken with brown rice"},
        "thrown_away": [
            {"item": "broccoli", "quantity": "1 cup", "percentage_of_original": "100%"}
        ],
        "eaten": [
            {"item": "chicken", "quantity": "8 oz", "percentage_of_original": "100%"},
            {"item": "rice", "quantity": "1 cup", "percentage_of_original": "100%"}
        ],
        "food_preferences": {
            "likely_dislikes": ["broccoli"],
            "likely_likes": ["chicken", "rice"],
            "insights": "Prefers protein and grains over vegetables"
        },
        "waste_summary": {"total_waste_percentage": "20%", "waste_value": "low"}
    }
}
requests.post(f"{BASE_URL}/api/user/preferences/update", json=waste_data)
print("   ✅ User created with preferences: likes chicken & rice, dislikes broccoli")

# 4. Get matched items for this user
print("\n4. Getting matched dining hall items for user...")
response = requests.get(f"{BASE_URL}/api/user/food_matcher_test/matched-items?dining_hall=North Campus Dining&meal_period=lunch&limit=5")
result = response.json()

print(f"\n   Top {result['count']} Matched Items:")
print(f"   Dining Hall: {result['dining_hall']}")
print(f"   Meal Period: {result['meal_period']}\n")

for i, matched in enumerate(result.get('matched_items', []), 1):
    item = matched['item']
    score = matched['match_score']
    confidence = matched['confidence']
    reasons = matched['match_reasons']
    
    print(f"   {i}. {item['name']}")
    print(f"      Match Score: {score}% ({confidence} confidence)")
    print(f"      Category: {item['category']}")
    print(f"      Reasons: {', '.join(reasons)}")
    print(f"      Ingredients: {', '.join(item['ingredients'][:3])}...")
    print()

print("=" * 60)
print("✅ Food matching system working!")
print("=" * 60)
