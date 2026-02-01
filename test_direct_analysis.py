"""
Test script to debug the OpenAI API call directly
"""
import sys
sys.path.append('.')

from food_analysis_service import analyze_image_url

# Test with a food image
test_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800"

print("Testing food analysis with debug logging...")
print(f"Image URL: {test_url}\n")

try:
    result = analyze_image_url(test_url)
    print("\n✅ SUCCESS!")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
