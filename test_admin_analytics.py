"""
Test the admin analytics endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:5001"

print("=" * 70)
print("Admin Analytics Test - Waste Reduction Insights")
print("=" * 70)

# First, create some test users with dislikes
print("\n1. Setting up test data with multiple users...")
test_users = [
    {
        "user_id": "student_001",
        "dislikes": ["broccoli", "carrots", "brussels sprouts"],
        "likes": ["chicken", "rice"]
    },
    {
        "user_id": "student_002",
        "dislikes": ["broccoli", "spinach"],
        "likes": ["beef", "potatoes"]
    },
    {
        "user_id": "student_003",
        "dislikes": ["carrots", "asparagus", "broccoli"],
        "likes": ["salmon", "quinoa"]
    },
    {
        "user_id": "student_004",
        "dislikes": ["brussels sprouts", "kale"],
        "likes": ["chicken", "pasta"]
    }
]

for user_data in test_users:
    # Create user
    requests.post(f"{BASE_URL}/api/user/create", 
                 json={"user_id": user_data["user_id"], "user_name": f"Test {user_data['user_id']}"})
    
    # Add preferences
    waste_analysis = {
        "user_id": user_data["user_id"],
        "waste_analysis": {
            "original_meal": {"name": "Test Meal", "description": "Test"},
            "thrown_away": [{"item": d, "quantity": "1 cup", "percentage_of_original": "50%"} for d in user_data["dislikes"]],
            "eaten": [{"item": l, "quantity": "1 cup", "percentage_of_original": "100%"} for l in user_data["likes"]],
            "food_preferences": {
                "likely_dislikes": user_data["dislikes"],
                "likely_likes": user_data["likes"],
                "insights": "Test data"
            },
            "waste_summary": {"total_waste_percentage": "30%", "waste_value": "medium"}
        }
    }
    requests.post(f"{BASE_URL}/api/user/preferences/update", json=waste_analysis)

print(f"   ✅ Created {len(test_users)} test users with preferences")

# 2. Get admin waste insights
print("\n2. Getting admin waste insights...")
response = requests.get(f"{BASE_URL}/api/admin/waste-insights?limit=10")
result = response.json()

if result.get('success'):
    summary = result.get('summary', {})
    print(f"\n   📊 SUMMARY:")
    print(f"      Total Users: {summary.get('total_users_analyzed')}")
    print(f"      Users with Preferences: {summary.get('users_with_preferences')}")
    print(f"      Unique Disliked Items: {summary.get('total_unique_disliked_items')}")
    print(f"      Avg Dislikes/User: {summary.get('average_dislikes_per_user')}")
    
    print(f"\n   🚨 TOP DISLIKED ITEMS:")
    for i, item in enumerate(result.get('top_disliked_items', [])[:10], 1):
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(item['severity'], "⚪")
        
        print(f"\n      {i}. {item['food_item']}")
        print(f"         {severity_emoji} Severity: {item['severity'].upper()}")
        print(f"         Disliked by: {item['dislike_count']} users ({item['percentage_of_users']}%)")
        print(f"         💡 {item['recommendation']}")
    
    recommendations = result.get('recommendations', {})
    if recommendations.get('critical_items'):
        print(f"\n   ⚠️  CRITICAL ITEMS TO ADDRESS:")
        for item in recommendations['critical_items']:
            print(f"      - {item}")
    
    if recommendations.get('action_items'):
        print(f"\n   📋 RECOMMENDED ACTIONS:")
        for action in recommendations['action_items']:
            print(f"      • {action}")
else:
    print(f"   ❌ Error: {result.get('error')}")

# 3. Get waste by category
print("\n3. Getting waste breakdown by category...")
response = requests.get(f"{BASE_URL}/api/admin/waste-by-category")
result = response.json()

if result.get('success'):
    print(f"\n   📈 CATEGORY BREAKDOWN:")
    for cat in result.get('category_breakdown', []):
        print(f"\n      Category: {cat['category'].upper()}")
        print(f"      Total Dislikes: {cat['total_dislikes']}")
        print(f"      Unique Items: {cat['unique_items']}")
        if cat.get('most_common'):
            print(f"      Most Common: {', '.join([f'{item[0]} ({item[1]}x)' for item in cat['most_common']])}")
    
    print(f"\n   💡 {result.get('insight')}")
else:
    print(f"   ❌ Error: {result.get('error')}")

print("\n" + "=" * 70)
print("✅ Admin analytics testing complete!")
print("=" * 70)
