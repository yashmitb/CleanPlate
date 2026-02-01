from pymongo import MongoClient
import certifi
from typing import List, Dict
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

def get_admin_waste_insights(limit: int = 20) -> Dict:
    """
    Get aggregated insights about food waste across all users.
    Helps admins understand what foods should be reduced or improved.
    
    Args:
        limit: Number of top disliked items to return
        
    Returns:
        Dictionary with waste insights and recommendations
    """
    try:
        # Connect to MongoDB
        mongodb_uri = os.getenv("MONGODB_URI")
        client = MongoClient(
            mongodb_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        
        db = client["food_preferences"]
        users_collection = db['users']
        
        # Get all users
        all_users = list(users_collection.find({}, {"_id": 0, "user_id": 1, "disliked_foods": 1, "meal_count": 1}))
        
        # Aggregate dislikes across all users
        dislike_counter = Counter()
        total_users = len(all_users)
        users_with_data = 0
        
        for user in all_users:
            dislikes = user.get('disliked_foods', [])
            if dislikes:
                users_with_data += 1
                for food in dislikes:
                    dislike_counter[food] += 1
        
        # Calculate percentages and create insights
        top_dislikes = []
        for food, count in dislike_counter.most_common(limit):
            percentage = (count / total_users) * 100 if total_users > 0 else 0
            
            # Determine severity
            if percentage >= 50:
                severity = "critical"
                recommendation = f"Consider removing or significantly reformulating {food}"
            elif percentage >= 30:
                severity = "high"
                recommendation = f"High waste item - review preparation method for {food}"
            elif percentage >= 15:
                severity = "medium"
                recommendation = f"Monitor {food} - consider alternative preparation"
            else:
                severity = "low"
                recommendation = f"Minor concern for {food}"
            
            top_dislikes.append({
                "food_item": food.title(),
                "dislike_count": count,
                "percentage_of_users": round(percentage, 1),
                "severity": severity,
                "recommendation": recommendation
            })
        
        # Calculate overall stats
        total_unique_dislikes = len(dislike_counter)
        avg_dislikes_per_user = sum(len(u.get('disliked_foods', [])) for u in all_users) / total_users if total_users > 0 else 0
        
        client.close()
        
        return {
            "summary": {
                "total_users_analyzed": total_users,
                "users_with_preferences": users_with_data,
                "total_unique_disliked_items": total_unique_dislikes,
                "average_dislikes_per_user": round(avg_dislikes_per_user, 1)
            },
            "top_disliked_items": top_dislikes,
            "recommendations": {
                "critical_items": [item["food_item"] for item in top_dislikes if item["severity"] == "critical"],
                "high_priority_items": [item["food_item"] for item in top_dislikes if item["severity"] == "high"],
                "action_items": [
                    "Review preparation methods for high-waste items",
                    "Consider menu alternatives for critical items",
                    "Survey students for specific feedback on problem items",
                    "Monitor waste trends over time"
                ]
            }
        }
        
    except Exception as e:
        print(f"Error getting admin insights: {e}")
        return {
            "error": str(e),
            "summary": {},
            "top_disliked_items": [],
            "recommendations": {}
        }

def get_waste_trends_by_category() -> Dict:
    """Get waste insights grouped by food category."""
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        client = MongoClient(mongodb_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        
        db = client["food_preferences"]
        users_collection = db['users']
        
        # Get all users' dislikes
        all_users = list(users_collection.find({}, {"_id": 0, "disliked_foods": 1}))
        
        # Categorize dislikes
        from recommendation_service import categorize_food
        
        category_dislikes = {}
        for user in all_users:
            for food in user.get('disliked_foods', []):
                category = categorize_food(food)
                if category not in category_dislikes:
                    category_dislikes[category] = []
                category_dislikes[category].append(food)
        
        # Count by category
        category_stats = []
        for category, foods in category_dislikes.items():
            category_stats.append({
                "category": category,
                "total_dislikes": len(foods),
                "unique_items": len(set(foods)),
                "most_common": Counter(foods).most_common(3)
            })
        
        # Sort by total dislikes
        category_stats.sort(key=lambda x: x['total_dislikes'], reverse=True)
        
        client.close()
        
        return {
            "category_breakdown": category_stats,
            "insight": f"Most problematic category: {category_stats[0]['category']}" if category_stats else "No data"
        }
        
    except Exception as e:
        print(f"Error getting category trends: {e}")
        return {"error": str(e)}
