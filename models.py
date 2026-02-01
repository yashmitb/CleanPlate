from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

# --- Shared Models (Waste Analysis) ---

class OriginalMeal(BaseModel):
    name: str = Field(default="Unknown")
    description: str = Field(default="")

class FoodItem(BaseModel):
    item: str
    quantity: str
    percentage_of_original: str

class FoodPreferences(BaseModel):
    likely_dislikes: List[str] = []
    likely_likes: List[str] = []
    insights: str = ""

class WasteSummary(BaseModel):
    total_waste_percentage: str
    waste_value: str

class WasteAnalysis(BaseModel):
    original_meal: OriginalMeal
    thrown_away: List[FoodItem]
    eaten: List[FoodItem]
    food_preferences: FoodPreferences
    waste_summary: WasteSummary

# --- User Models ---

class UserCreate(BaseModel):
    user_id: str
    user_name: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    liked_foods: List[str] = []
    disliked_foods: List[str] = []
    meal_count: int = 0
    total_waste_percentage: float = 0.0
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserSummary(UserResponse):
    total_meals_analyzed: int
    average_waste_percentage: float
    recent_meals: List[Dict[str, Any]]

# --- API Request/Response Models ---

class UpdatePreferencesRequest(BaseModel):
    user_id: str
    waste_analysis: WasteAnalysis

class StandardResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Any] = None

class MealHistoryResponse(BaseModel):
    success: bool
    history: List[Dict[str, Any]] 
    count: int

class AnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[WasteAnalysis] = None
    error: Optional[str] = None

# --- Recommendation Models ---

class FoodRecommendation(BaseModel):
    name: str
    match_percentage: float = Field(ge=0, le=100)
    image_url: str
    category: str
    description: str
    confidence: str  # "high", "medium", "low"
    tags: List[str] = []

class DislikedFood(BaseModel):
    name: str
    frequency: int
    last_seen: Optional[str] = None
    category: str

class RecommendationsResponse(BaseModel):
    success: bool
    recommendations: List[FoodRecommendation]
    count: int

class DislikesResponse(BaseModel):
    success: bool
    dislikes: List[DislikedFood]
    count: int

# --- Dining Hall Models ---

class NutritionInfo(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class DiningHallItem(BaseModel):
    item_id: str
    name: str
    dining_hall: str
    category: str
    ingredients: List[str]
    tags: List[str] = []
    allergens: List[str] = []
    nutrition: NutritionInfo
    available_days: List[str]
    meal_period: str  # "breakfast", "lunch", "dinner"

class MatchedItem(BaseModel):
    item: DiningHallItem
    match_score: float = Field(ge=0, le=100)
    match_reasons: List[str]
    confidence: str  # "high", "medium", "low"

class MatchedItemsResponse(BaseModel):
    success: bool
    matched_items: List[MatchedItem]
    count: int
    dining_hall: str
    meal_period: str

