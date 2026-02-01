import os
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

load_dotenv()

def populate_user123():
    mongodb_uri = os.getenv("MONGODB_URI")
    client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
    db = client["food_preferences"]
    users_collection = db["users"]
    
    user_id = "user123"
    
    # Niche likes and dislikes
    likes = [
        "yellowtail sashimi", "truffle risotto", "miso glazed black cod", 
        "wagyu beef sliders", "burrata salad", "matcha mille crepe",
        "lobster ravioli", "duck confit", "hamachi crudo"
    ]
    
    dislikes = [
        "coriander", "blue cheese", "uni (sea urchin)", "raw oysters", 
        "liquorice", "cilantro", "okra", "anchovies"
    ]
    
    # Map food items to high-quality image URLs
    food_images = {
        "yellowtail sashimi": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
        "truffle risotto": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=800&q=80",
        "miso glazed black cod": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
        "wagyu beef sliders": "https://images.unsplash.com/photo-1521390188846-e2a3a97455a0?auto=format&fit=crop&w=800&q=80",
        "burrata salad": "https://images.unsplash.com/photo-1608897013039-887f3c0cac56?auto=format&fit=crop&w=800&q=80",
        "matcha mille crepe": "https://images.unsplash.com/photo-1536441589741-94896eb9729d?auto=format&fit=crop&w=800&q=80",
        "lobster ravioli": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
        "duck confit": "https://images.unsplash.com/photo-1514516872720-394013fd7826?auto=format&fit=crop&w=800&q=80",
        "hamachi crudo": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
        "uni (sea urchin)": "https://images.unsplash.com/photo-1604135398284-88469d784a9b?auto=format&fit=crop&w=800&q=80",
        "blue cheese": "https://images.unsplash.com/photo-1452195100486-9cc805987862?auto=format&fit=crop&w=800&q=80"
    }
    
    # Generate a rich meal history (25 meals for better categorization)
    meal_history = []
    import random
    
    for i in range(25):
        days_ago = 30 - i
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        eaten_items = []
        selected_likes = random.sample(likes, min(2, len(likes)))
        for item in selected_likes:
            eaten_items.append({
                "item": item,
                "quantity": "1 portion",
                "percentage_of_original": "100%"
            })
            
        thrown_away_items = []
        if i % 2 == 0:
            dislike_item = random.choice(dislikes)
            thrown_away_items.append({
                "item": dislike_item,
                "quantity": "1/2 cup",
                "percentage_of_original": "85%"
            })
            
        meal_history.append({
            "meal_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "original_meal": {
                "name": f"Gourmet Dining Event #{i+1}",
                "description": "Exquisite culinary experience with premium ingredients."
            },
            "eaten": eaten_items,
            "thrown_away": thrown_away_items
        })
        
    user_doc = {
        "user_id": user_id,
        "name": "Alex Smith",
        "liked_foods": likes,
        "disliked_foods": dislikes,
        "food_images": food_images, # Direct mapping in DB
        "meal_count": len(meal_history),
        "meal_history": meal_history,
        "last_updated": datetime.now().isoformat()
    }
    
    # Update or insert
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": user_doc},
        upsert=True
    )
    
    print(f"✅ Successfully populated data for {user_id}")
    print(f"   - Likes: {len(likes)}")
    print(f"   - Dislikes: {len(dislikes)}")
    print(f"   - Meal History: {len(meal_history)} entries")
    
    client.close()

if __name__ == "__main__":
    populate_user123()
