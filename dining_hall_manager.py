from pymongo import MongoClient
import certifi
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DiningHallManager:
    """Manages dining hall menu items in MongoDB."""
    
    def __init__(self, mongodb_uri: Optional[str] = None, db_name: str = "food_preferences"):
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI")
        
        if not self.mongodb_uri:
            raise ValueError("MongoDB URI must be provided")
        
        self.client = MongoClient(
            self.mongodb_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        
        self.db = self.client[db_name]
        self.dining_items_collection = self.db['dining_hall_items']
        
        # Create indexes
        self.dining_items_collection.create_index("item_id", unique=True)
        self.dining_items_collection.create_index("dining_hall")
        self.dining_items_collection.create_index("meal_period")
        self.dining_items_collection.create_index("category")
    
    def populate_sample_items(self):
        """Populate database with realistic dining hall menu items."""
        
        sample_items = [
            # Proteins
            {
                "item_id": "protein_001",
                "name": "Grilled Chicken Breast",
                "dining_hall": "North Campus Dining",
                "category": "protein",
                "ingredients": ["chicken", "olive oil", "herbs", "garlic"],
                "tags": ["grilled", "healthy", "gluten-free"],
                "allergens": [],
                "nutrition": {"calories": 250, "protein": 45, "carbs": 0, "fat": 8},
                "available_days": ["Monday", "Wednesday", "Friday"],
                "meal_period": "lunch"
            },
            {
                "item_id": "protein_002",
                "name": "Baked Salmon",
                "dining_hall": "North Campus Dining",
                "category": "protein",
                "ingredients": ["salmon", "lemon", "dill", "butter"],
                "tags": ["baked", "omega-3", "healthy"],
                "allergens": ["fish"],
                "nutrition": {"calories": 350, "protein": 40, "carbs": 2, "fat": 20},
                "available_days": ["Tuesday", "Thursday"],
                "meal_period": "dinner"
            },
            {
                "item_id": "protein_003",
                "name": "Beef Stir Fry",
                "dining_hall": "South Campus Dining",
                "category": "protein",
                "ingredients": ["beef", "soy sauce", "ginger", "garlic", "vegetables"],
                "tags": ["stir-fried", "asian"],
                "allergens": ["soy"],
                "nutrition": {"calories": 400, "protein": 35, "carbs": 15, "fat": 22},
                "available_days": ["Monday", "Thursday"],
                "meal_period": "dinner"
            },
            {
                "item_id": "protein_004",
                "name": "Tofu Scramble",
                "dining_hall": "North Campus Dining",
                "category": "protein",
                "ingredients": ["tofu", "turmeric", "vegetables", "nutritional yeast"],
                "tags": ["vegan", "vegetarian", "healthy"],
                "allergens": ["soy"],
                "nutrition": {"calories": 180, "protein": 15, "carbs": 10, "fat": 9},
                "available_days": ["Daily"],
                "meal_period": "breakfast"
            },
            
            # Grains/Carbs
            {
                "item_id": "grain_001",
                "name": "Brown Rice",
                "dining_hall": "North Campus Dining",
                "category": "grain",
                "ingredients": ["brown rice", "water"],
                "tags": ["whole-grain", "vegan", "gluten-free"],
                "allergens": [],
                "nutrition": {"calories": 215, "protein": 5, "carbs": 45, "fat": 2},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            },
            {
                "item_id": "grain_002",
                "name": "Quinoa Pilaf",
                "dining_hall": "South Campus Dining",
                "category": "grain",
                "ingredients": ["quinoa", "vegetables", "herbs", "olive oil"],
                "tags": ["whole-grain", "vegan", "gluten-free", "protein-rich"],
                "allergens": [],
                "nutrition": {"calories": 220, "protein": 8, "carbs": 39, "fat": 4},
                "available_days": ["Tuesday", "Friday"],
                "meal_period": "dinner"
            },
            {
                "item_id": "grain_003",
                "name": "Garlic Bread",
                "dining_hall": "North Campus Dining",
                "category": "grain",
                "ingredients": ["bread", "garlic", "butter", "parsley"],
                "tags": ["baked"],
                "allergens": ["gluten", "dairy"],
                "nutrition": {"calories": 150, "protein": 4, "carbs": 20, "fat": 6},
                "available_days": ["Daily"],
                "meal_period": "dinner"
            },
            {
                "item_id": "grain_004",
                "name": "French Fries",
                "dining_hall": "South Campus Dining",
                "category": "grain",
                "ingredients": ["potatoes", "oil", "salt"],
                "tags": ["fried", "vegan"],
                "allergens": [],
                "nutrition": {"calories": 365, "protein": 4, "carbs": 48, "fat": 17},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            },
            
            # Vegetables
            {
                "item_id": "veg_001",
                "name": "Steamed Broccoli",
                "dining_hall": "North Campus Dining",
                "category": "vegetable",
                "ingredients": ["broccoli"],
                "tags": ["steamed", "vegan", "healthy"],
                "allergens": [],
                "nutrition": {"calories": 55, "protein": 4, "carbs": 11, "fat": 1},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            },
            {
                "item_id": "veg_002",
                "name": "Roasted Carrots",
                "dining_hall": "South Campus Dining",
                "category": "vegetable",
                "ingredients": ["carrots", "olive oil", "honey", "thyme"],
                "tags": ["roasted", "vegetarian"],
                "allergens": [],
                "nutrition": {"calories": 80, "protein": 1, "carbs": 15, "fat": 3},
                "available_days": ["Monday", "Wednesday", "Friday"],
                "meal_period": "dinner"
            },
            {
                "item_id": "veg_003",
                "name": "Caesar Salad",
                "dining_hall": "North Campus Dining",
                "category": "vegetable",
                "ingredients": ["romaine lettuce", "parmesan", "croutons", "caesar dressing"],
                "tags": ["salad", "vegetarian"],
                "allergens": ["dairy", "gluten"],
                "nutrition": {"calories": 180, "protein": 6, "carbs": 12, "fat": 12},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            },
            {
                "item_id": "veg_004",
                "name": "Grilled Asparagus",
                "dining_hall": "South Campus Dining",
                "category": "vegetable",
                "ingredients": ["asparagus", "olive oil", "lemon", "garlic"],
                "tags": ["grilled", "vegan", "healthy"],
                "allergens": [],
                "nutrition": {"calories": 60, "protein": 3, "carbs": 8, "fat": 3},
                "available_days": ["Tuesday", "Thursday"],
                "meal_period": "dinner"
            },
            
            # Dairy
            {
                "item_id": "dairy_001",
                "name": "Greek Yogurt",
                "dining_hall": "North Campus Dining",
                "category": "dairy",
                "ingredients": ["milk", "yogurt cultures"],
                "tags": ["healthy", "protein-rich"],
                "allergens": ["dairy"],
                "nutrition": {"calories": 100, "protein": 17, "carbs": 6, "fat": 0},
                "available_days": ["Daily"],
                "meal_period": "breakfast"
            },
            {
                "item_id": "dairy_002",
                "name": "Mac and Cheese",
                "dining_hall": "South Campus Dining",
                "category": "dairy",
                "ingredients": ["pasta", "cheese", "milk", "butter"],
                "tags": ["comfort-food", "vegetarian"],
                "allergens": ["dairy", "gluten"],
                "nutrition": {"calories": 350, "protein": 14, "carbs": 40, "fat": 15},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            },
            
            # Fruits
            {
                "item_id": "fruit_001",
                "name": "Fresh Fruit Bowl",
                "dining_hall": "North Campus Dining",
                "category": "fruit",
                "ingredients": ["strawberries", "blueberries", "melon", "grapes"],
                "tags": ["fresh", "vegan", "healthy"],
                "allergens": [],
                "nutrition": {"calories": 90, "protein": 1, "carbs": 22, "fat": 0},
                "available_days": ["Daily"],
                "meal_period": "breakfast"
            },
            {
                "item_id": "fruit_002",
                "name": "Apple Slices",
                "dining_hall": "South Campus Dining",
                "category": "fruit",
                "ingredients": ["apples"],
                "tags": ["fresh", "vegan", "healthy"],
                "allergens": [],
                "nutrition": {"calories": 95, "protein": 0, "carbs": 25, "fat": 0},
                "available_days": ["Daily"],
                "meal_period": "lunch"
            }
        ]
        
        # Clear existing items (for testing)
        self.dining_items_collection.delete_many({})
        
        # Insert sample items
        result = self.dining_items_collection.insert_many(sample_items)
        print(f"✅ Inserted {len(result.inserted_ids)} dining hall items")
        
        return len(result.inserted_ids)
    
    def get_items_by_hall_and_period(self, dining_hall: str, meal_period: str) -> List[Dict]:
        """Get all items for a specific dining hall and meal period."""
        items = list(self.dining_items_collection.find(
            {
                "dining_hall": dining_hall,
                "$or": [
                    {"meal_period": meal_period},
                    {"available_days": "Daily"}
                ]
            },
            {"_id": 0}
        ))
        return items
    
    def get_all_items(self) -> List[Dict]:
        """Get all dining hall items."""
        return list(self.dining_items_collection.find({}, {"_id": 0}))
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()


# Script to populate database
if __name__ == "__main__":
    manager = DiningHallManager()
    count = manager.populate_sample_items()
    print(f"\n🎉 Successfully populated {count} dining hall items!")
    
    # Show sample
    print("\nSample items from North Campus Dining (lunch):")
    items = manager.get_items_by_hall_and_period("North Campus Dining", "lunch")
    for item in items[:3]:
        print(f"  - {item['name']} ({item['category']})")
    
    manager.close()
