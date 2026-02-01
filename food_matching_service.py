from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from user_preference_manager import UserFoodPreferenceManager
from dining_hall_manager import DiningHallManager

load_dotenv()

def calculate_match_score(user_likes: List[str], user_dislikes: List[str], food_item: Dict) -> tuple[float, List[str], str]:
    """
    Calculate how well a food item matches user preferences.
    
    Returns:
        (match_score, match_reasons, confidence)
    """
    score = 50.0  # Base score
    reasons = []
    
    ingredients = [ing.lower().strip() for ing in food_item.get('ingredients', [])]
    item_name = food_item.get('name', '').lower()
    category = food_item.get('category', '').lower()
    tags = [tag.lower() for tag in food_item.get('tags', [])]
    
    # Check for disliked ingredients (major penalty)
    dislike_penalty = 0
    for dislike in user_dislikes:
        dislike_lower = dislike.lower().strip()
        # Check in ingredients
        if any(dislike_lower in ing for ing in ingredients):
            dislike_penalty += 30
            reasons.append(f"Contains disliked ingredient: {dislike}")
        # Check in item name
        elif dislike_lower in item_name:
            dislike_penalty += 25
            reasons.append(f"Item name contains disliked food: {dislike}")
    
    score -= dislike_penalty
    
    # If score is already very low due to dislikes, return early
    if score < 20:
        return (max(0, score), reasons, "low")
    
    # Check for liked ingredients/foods (bonus points)
    like_bonus = 0
    matched_likes = []
    for like in user_likes:
        like_lower = like.lower().strip()
        # Check in ingredients
        if any(like_lower in ing for ing in ingredients):
            like_bonus += 20
            matched_likes.append(like)
        # Check in item name
        elif like_lower in item_name:
            like_bonus += 15
            matched_likes.append(like)
        # Check in category
        elif like_lower == category:
            like_bonus += 10
            matched_likes.append(like)
    
    if matched_likes:
        reasons.append(f"Matches your preferences: {', '.join(matched_likes)}")
    
    score += like_bonus
    
    # Bonus for healthy tags
    if 'healthy' in tags:
        score += 5
        reasons.append("Healthy option")
    
    # Bonus for dietary preferences
    if 'vegan' in tags or 'vegetarian' in tags:
        score += 3
    
    # Cap score at 100
    score = min(100, score)
    
    # Determine confidence
    if score >= 75:
        confidence = "high"
    elif score >= 50:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Add default reason if no specific reasons
    if not reasons:
        reasons.append(f"General {category} option")
    
    return (score, reasons, confidence)


def get_matched_items(user_id: str, dining_hall: str = "North Campus Dining", 
                     meal_period: str = "lunch", limit: int = 10) -> List[Dict]:
    """
    Get dining hall items matched to user preferences.
    
    Args:
        user_id: User identifier
        dining_hall: Name of dining hall
        meal_period: Meal period (breakfast/lunch/dinner)
        limit: Maximum number of items to return
        
    Returns:
        List of matched items with scores
    """
    try:
        # Get user preferences
        user_manager = UserFoodPreferenceManager(
            mongodb_uri=os.getenv("MONGODB_URI"),
            db_name="food_preferences"
        )
        
        user = user_manager.get_user(user_id)
        if not user:
            print(f"User {user_id} not found")
            return []
        
        user_likes = user.get('liked_foods', [])
        user_dislikes = user.get('disliked_foods', [])
        
        # Get dining hall items
        dining_manager = DiningHallManager(
            mongodb_uri=os.getenv("MONGODB_URI"),
            db_name="food_preferences"
        )
        
        items = dining_manager.get_items_by_hall_and_period(dining_hall, meal_period)
        
        # Calculate match scores
        matched_items = []
        for item in items:
            score, reasons, confidence = calculate_match_score(user_likes, user_dislikes, item)
            
            matched_items.append({
                "item": item,
                "match_score": round(score, 1),
                "match_reasons": reasons,
                "confidence": confidence
            })
        
        # Sort by match score (descending)
        matched_items.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Close connections
        user_manager.close()
        dining_manager.close()
        
        return matched_items[:limit]
        
    except Exception as e:
        print(f"Error getting matched items: {e}")
        return []


def get_all_dining_halls() -> List[str]:
    """Get list of all dining halls."""
    try:
        dining_manager = DiningHallManager(
            mongodb_uri=os.getenv("MONGODB_URI"),
            db_name="food_preferences"
        )
        
        items = dining_manager.get_all_items()
        halls = list(set(item['dining_hall'] for item in items))
        
        dining_manager.close()
        return sorted(halls)
        
    except Exception as e:
        print(f"Error getting dining halls: {e}")
        return []
