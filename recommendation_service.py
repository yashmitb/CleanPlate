from typing import List, Dict, Optional
from datetime import datetime
from user_preference_manager import UserFoodPreferenceManager
import os
from dotenv import load_dotenv

load_dotenv()

# Food category mapping (can be expanded)
FOOD_CATEGORIES = {
    # Proteins
    "chicken": "protein", "beef": "protein", "pork": "protein", "fish": "protein",
    "salmon": "protein", "tuna": "protein", "shrimp": "protein", "turkey": "protein",
    "eggs": "protein", "tofu": "protein", "beans": "protein", "lentils": "protein",
    
    # Vegetables
    "broccoli": "vegetable", "carrots": "vegetable", "spinach": "vegetable",
    "lettuce": "vegetable", "tomatoes": "vegetable", "onions": "vegetable",
    "peppers": "vegetable", "mushrooms": "vegetable", "celery": "vegetable",
    "cucumber": "vegetable", "zucchini": "vegetable", "asparagus": "vegetable",
    
    # Grains/Carbs
    "rice": "grain", "pasta": "grain", "bread": "grain", "quinoa": "grain",
    "oats": "grain", "noodles": "grain", "tortilla": "grain", "fries": "grain",
    "potatoes": "grain", "sweet potato": "grain",
    
    # Dairy
    "cheese": "dairy", "milk": "dairy", "yogurt": "dairy", "butter": "dairy",
    "cream": "dairy", "sour cream": "dairy",
    
    # Fruits
    "apple": "fruit", "banana": "fruit", "orange": "fruit", "berries": "fruit",
    "strawberries": "fruit", "grapes": "fruit", "watermelon": "fruit",
    
    # Other
    "sauce": "condiment", "dressing": "condiment", "salsa": "condiment",
    "guacamole": "condiment", "toppings": "condiment"
}

# Placeholder image URLs (using placeholder service)
def get_food_image_url(food_name: str) -> str:
    """Generate a placeholder image URL for a food item."""
    # Using a placeholder image service - can be replaced with real food API
    food_slug = food_name.replace(" ", "-").lower()
    return f"https://source.unsplash.com/400x300/?{food_slug},food"

def categorize_food(food_name: str) -> str:
    """Categorize a food item."""
    food_lower = food_name.lower()
    
    # Check exact matches first
    if food_lower in FOOD_CATEGORIES:
        return FOOD_CATEGORIES[food_lower]
    
    # Check if any category keyword is in the food name
    for keyword, category in FOOD_CATEGORIES.items():
        if keyword in food_lower:
            return category
    
    return "other"

def get_recommendations(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Get food recommendations for a user based on their preferences.
    
    Args:
        user_id: User identifier
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Initialize manager
        manager = UserFoodPreferenceManager(
            mongodb_uri=os.getenv("MONGODB_URI"),
            db_name="food_preferences"
        )
        
        # Get user data
        user = manager.get_user(user_id)
        if not user:
            return []
        
        liked_foods = user.get('liked_foods', [])
        meal_count = user.get('meal_count', 0)
        
        if not liked_foods:
            return []
        
        recommendations = []
        
        # Get meal history to calculate frequencies
        history = manager.get_meal_history(user_id, limit=100)
        
        # Count how often each liked food appears
        food_frequency = {}
        for meal in history:
            eaten_items = meal.get('eaten', [])
            for item in eaten_items:
                food_name = item.get('item', '').lower().strip()
                if food_name in liked_foods:
                    food_frequency[food_name] = food_frequency.get(food_name, 0) + 1
        
        # Calculate match percentages based on frequency
        max_frequency = max(food_frequency.values()) if food_frequency else 1
        
        for food in liked_foods[:limit]:
            frequency = food_frequency.get(food, 1)
            
            # Calculate match percentage (higher frequency = higher match)
            match_percentage = min(100, (frequency / max_frequency) * 100)
            
            # Determine confidence based on meal count and frequency
            if meal_count >= 5 and frequency >= 3:
                confidence = "high"
            elif meal_count >= 3 and frequency >= 2:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Get category
            category = categorize_food(food)
            
            # Generate tags
            tags = [category]
            if frequency >= 3:
                tags.append("favorite")
            if match_percentage >= 80:
                tags.append("highly-recommended")
            
            recommendations.append({
                "name": food.title(),
                "match_percentage": round(match_percentage, 1),
                "image_url": get_food_image_url(food),
                "category": category,
                "description": f"You've enjoyed {food} in {frequency} meal{'s' if frequency != 1 else ''}",
                "confidence": confidence,
                "tags": tags
            })
        
        # Sort by match percentage (descending)
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        manager.close()
        return recommendations[:limit]
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

def get_dislikes(user_id: str) -> List[Dict]:
    """
    Get disliked foods for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of disliked food dictionaries
    """
    try:
        # Initialize manager
        manager = UserFoodPreferenceManager(
            mongodb_uri=os.getenv("MONGODB_URI"),
            db_name="food_preferences"
        )
        
        # Get user data
        user = manager.get_user(user_id)
        if not user:
            return []
        
        disliked_foods = user.get('disliked_foods', [])
        
        if not disliked_foods:
            return []
        
        # Get meal history to find when foods were last wasted
        history = manager.get_meal_history(user_id, limit=100)
        
        # Track frequency and last seen
        dislike_data = {}
        for meal in history:
            thrown_away = meal.get('thrown_away', [])
            timestamp = meal.get('timestamp', '')
            
            for item in thrown_away:
                food_name = item.get('item', '').lower().strip()
                if food_name in disliked_foods:
                    if food_name not in dislike_data:
                        dislike_data[food_name] = {
                            'frequency': 0,
                            'last_seen': timestamp
                        }
                    dislike_data[food_name]['frequency'] += 1
                    # Update last seen if this is more recent
                    if timestamp and (not dislike_data[food_name]['last_seen'] or 
                                     timestamp > dislike_data[food_name]['last_seen']):
                        dislike_data[food_name]['last_seen'] = timestamp
        
        dislikes = []
        for food in disliked_foods:
            data = dislike_data.get(food, {'frequency': 1, 'last_seen': None})
            
            dislikes.append({
                "name": food.title(),
                "frequency": data['frequency'],
                "last_seen": data['last_seen'],
                "category": categorize_food(food)
            })
        
        # Sort by frequency (descending)
        dislikes.sort(key=lambda x: x['frequency'], reverse=True)
        
        manager.close()
        return dislikes
        
    except Exception as e:
        print(f"Error getting dislikes: {e}")
        return []
