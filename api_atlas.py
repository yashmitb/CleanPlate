from flask import Flask, request, jsonify, render_template
from user_preference_manager import UserFoodPreferenceManager
import json
import os
import socket
from dotenv import load_dotenv
import services
# from pyngrok import ngrok

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Documentation ---
@app.route('/')
@app.route('/docs')
def documentation():
    """
    Serve API documentation page.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CleanPlate API Documentation</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .endpoint { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #3498db; }
            .method { font-weight: bold; color: #fff; padding: 3px 8px; border-radius: 3px; font-size: 0.9em; display: inline-block; min-width: 60px; text-align: center; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            .delete { background: #f93e3e; }
            .url { font-family: monospace; font-weight: bold; font-size: 1.1em; color: #333; margin-left: 10px; }
            pre { background: #2d3436; color: #f1f1f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .desc { margin: 10px 0; font-size: 0.95em; }
            .response-format { margin-top: 10px; font-size: 0.9em; color: #555; }
        </style>
    </head>
    <body>
        <h1>🍽️ CleanPlate API Documentation</h1>
        <p>Welcome to the CleanPlate API. Below is a list of available endpoints.</p>

        <h2>Analysis</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> <span class="url">/api/analyze/image</span>
            <div class="desc">Analyze uploaded food image for waste data. expects <code>multipart/form-data</code> with <code>file</code> field.</div>
            <div class="response-format">
                <strong>Returns:</strong>
                <pre>{
  "success": true,
  "analysis": {
    "original_meal": { "name": "...", "description": "..." },
    "thrown_away": [ { "item": "...", "quantity": "...", "percentage_of_original": "..." } ],
    "eaten": [ { "item": "...", "quantity": "...", "percentage_of_original": "..." } ],
    "food_preferences": { "likely_likes": [], "likely_dislikes": [], "insights": "..." },
    "waste_summary": { "total_waste_percentage": "...", "waste_value": "..." }
  }
}</pre>
            </div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span> <span class="url">/api/analyze/url</span>
            <div class="desc">Analyze food image from a URL. Expects JSON body.</div>
            <pre>{ "image_url": "https://example.com/food.jpg" }</pre>
             <div class="response-format">
                <strong>Returns:</strong> Same structure as <code>/api/analyze/image</code>.
            </div>
        </div>

        <h2>User Management</h2>

        <div class="endpoint">
            <span class="method post">POST</span> <span class="url">/api/user/create</span>
            <div class="desc">Create a new user.</div>
            <pre>{ "user_id": "u123", "user_name": "Alice" }</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/api/user/&lt;user_id&gt;</span>
            <div class="desc">Get basic user profile information.</div>
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span> <span class="url">/api/user/&lt;user_id&gt;</span>
            <div class="desc">Delete a user and their history.</div>
        </div>

        <h2>Preferences & History</h2>

        <div class="endpoint">
            <span class="method post">POST</span> <span class="url">/api/user/preferences/update</span>
            <div class="desc">Update user preferences with new analysis data.</div>
            <pre>{
  "user_id": "u123",
  "waste_analysis": { ... }
}</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/api/user/&lt;user_id&gt;/summary</span>
            <div class="desc">Get comprehensive user summary and stats.</div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/api/user/&lt;user_id&gt;/history</span>
            <div class="desc">Get meal analysis history. Optional param: <code>?limit=10</code></div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/api/user/&lt;user_id&gt;/recommendations</span>
            <div class="desc">Get personalized food recommendations based on user preferences. Optional param: <code>?limit=10</code></div>
            <div class="response-format">
                <strong>Returns:</strong>
                <pre>{
  "success": true,
  "recommendations": [
    {
      "name": "Chicken",
      "match_percentage": 95.5,
      "image_url": "https://...",
      "category": "protein",
      "description": "You've enjoyed chicken in 5 meals",
      "confidence": "high",
      "tags": ["protein", "favorite", "highly-recommended"]
    }
  ],
  "count": 5
}</pre>
            </div>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/api/user/&lt;user_id&gt;/dislikes</span>
            <div class="desc">Get list of foods the user dislikes based on waste patterns.</div>
            <div class="response-format">
                <strong>Returns:</strong>
                <pre>{
  "success": true,
  "dislikes": [
    {
      "name": "Broccoli",
      "frequency": 3,
      "last_seen": "2026-01-15T10:30:00",
      "category": "vegetable"
    }
  ],
  "count": 2
}</pre>
            </div>
        </div>

        <h2>System</h2>

        <div class="endpoint">
            <span class="method get">GET</span> <span class="url">/health</span>
            <div class="desc">Check API health status.</div>
        </div>

    </body>
    </html>
    """

# --- Analysis Endpoints ---

@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    """
    Analyze an uploaded image file for food waste.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400

        image_bytes = file.read()
        analysis_result = services.analyze_food_waste_image(image_bytes)
        return jsonify({"success": True, "analysis": analysis_result}), 200
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze/url', methods=['POST'])
def analyze_url():
    """
    Analyze an image from a URL for food waste.
    """
    try:
        data = request.get_json()
        if not data or 'image_url' not in data:
            return jsonify({"success": False, "error": "image_url is required"}), 400
            
        image_url = data['image_url']
        analysis_result = services.analyze_food_waste_url(image_url)
        return jsonify({"success": True, "analysis": analysis_result}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    print("⚠️  WARNING: MONGODB_URI not set. Please set it as an environment variable or in the code.")
    print("   The app will fail when trying to connect to MongoDB.")

# Initialize the preference manager with Atlas (lazy initialization)
manager = None

def get_manager():
    """Get or initialize the preference manager."""
    global manager
    if manager is None:
        try:
            manager = UserFoodPreferenceManager(
                mongodb_uri=MONGODB_URI,
                db_name="food_preferences"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to MongoDB Atlas. "
                f"Please check your MONGODB_URI environment variable or connection string. "
                f"Error: {str(e)}"
            )
    return manager

@app.route('/api/user/preferences/update', methods=['POST'])
def update_preferences():
    """
    Update user food preferences based on waste analysis.
    
    Expected JSON body:
    {
        "user_id": "user123",
        "waste_analysis": { ... }  // Full waste analysis JSON from OpenAI
    }
    
    Returns:
    {
        "success": true,
        "user": { ... },
        "message": "Preferences updated successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        user_id = data.get('user_id')
        waste_analysis = data.get('waste_analysis')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        if not waste_analysis:
            return jsonify({
                "success": False,
                "error": "waste_analysis is required"
            }), 400
        
        # Update user preferences
        updated_user = get_manager().update_user_preferences(user_id, waste_analysis)
        
        # Remove MongoDB _id field for JSON serialization
        if '_id' in updated_user:
            del updated_user['_id']
        
        return jsonify({
            "success": True,
            "user": json.loads(json.dumps(updated_user, default=str)),
            "message": "Preferences updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    """
    Get comprehensive user summary with preferences and statistics.
    
    Returns:
    {
        "success": true,
        "summary": { ... }
    }
    """
    try:
        summary = get_manager().get_user_summary(user_id)
        
        if not summary:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        return jsonify({
            "success": True,
            "summary": summary
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/history', methods=['GET'])
def get_meal_history(user_id):
    """
    Get meal history for a user.
    
    Query params:
    - limit: Number of meals to return (default: 10)
    
    Returns:
    {
        "success": true,
        "history": [ ... ]
    }
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        
        history = get_manager().get_meal_history(user_id, limit=limit)
        
        return jsonify({
            "success": True,
            "history": history,
            "count": len(history)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """
    Get food recommendations for a user based on their preferences.
    
    Query params:
    - limit: Number of recommendations to return (default: 10)
    
    Returns:
    {
        "success": true,
        "recommendations": [ ... ],
        "count": 5
    }
    """
    try:
        import recommendation_service
        
        limit = request.args.get('limit', default=10, type=int)
        recommendations = recommendation_service.get_recommendations(user_id, limit=limit)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/dislikes', methods=['GET'])
def get_dislikes(user_id):
    """
    Get disliked foods for a user.
    
    Returns:
    {
        "success": true,
        "dislikes": [ ... ],
        "count": 3
    }
    """
    try:
        import recommendation_service
        
        dislikes = recommendation_service.get_dislikes(user_id)
        
        return jsonify({
            "success": True,
            "dislikes": dislikes,
            "count": len(dislikes)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get basic user information.
    
    Returns:
    {
        "success": true,
        "user": { ... }
    }
    """
    try:
        user = get_manager().get_user(user_id)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        # Remove MongoDB _id field
        if '_id' in user:
            del user['_id']
        
        return jsonify({
            "success": True,
            "user": json.loads(json.dumps(user, default=str))
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/create', methods=['POST'])
def create_user():
    """
    Create a new user.
    
    Expected JSON body:
    {
        "user_id": "user123",
        "user_name": "John Doe"  // optional
    }
    
    Returns:
    {
        "success": true,
        "user": { ... },
        "message": "User created successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Check if user already exists
        existing_user = get_manager().get_user(user_id)
        if existing_user:
            return jsonify({
                "success": False,
                "error": "User already exists"
            }), 409
        
        # Create user
        new_user = get_manager().create_user(user_id, user_name)
        
        # Remove MongoDB _id field
        if '_id' in new_user:
            del new_user['_id']
        
        return jsonify({
            "success": True,
            "user": json.loads(json.dumps(new_user, default=str)),
            "message": "User created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user and all their data.
    
    Returns:
    {
        "success": true,
        "message": "User deleted successfully"
    }
    """
    try:
        deleted = get_manager().delete_user(user_id)
        
        if not deleted:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/dining-halls', methods=['GET'])
def get_dining_halls():
    """Get list of all dining halls."""
    try:
        import food_matching_service
        halls = food_matching_service.get_all_dining_halls()
        return jsonify({"success": True, "dining_halls": halls, "count": len(halls)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dining-halls/<hall_name>/menu', methods=['GET'])
def get_dining_hall_menu(hall_name):
    """Get menu items for a specific dining hall and meal period."""
    try:
        from dining_hall_manager import DiningHallManager
        meal_period = request.args.get('meal_period', default='lunch', type=str)
        manager = DiningHallManager(mongodb_uri=os.getenv("MONGODB_URI"), db_name="food_preferences")
        items = manager.get_items_by_hall_and_period(hall_name, meal_period)
        manager.close()
        return jsonify({"success": True, "items": items, "count": len(items), "dining_hall": hall_name, "meal_period": meal_period}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/user/<user_id>/matched-items', methods=['GET'])
def get_user_matched_items(user_id):
    """Get dining hall items matched to user preferences."""
    try:
        import food_matching_service
        dining_hall = request.args.get('dining_hall', default='North Campus Dining', type=str)
        meal_period = request.args.get('meal_period', default='lunch', type=str)
        limit = request.args.get('limit', default=10, type=int)
        matched_items = food_matching_service.get_matched_items(user_id, dining_hall=dining_hall, meal_period=meal_period, limit=limit)
        return jsonify({"success": True, "matched_items": matched_items, "count": len(matched_items), "dining_hall": dining_hall, "meal_period": meal_period}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/waste-insights', methods=['GET'])
def get_admin_waste_insights():
    """
    Get aggregated waste insights across all users for admin dashboard.
    Shows most disliked foods to help reduce waste.
    
    Query params:
    - limit: Number of top items to return (default: 20)
    
    Returns:
    {
        "success": true,
        "summary": {
            "total_users_analyzed": 50,
            "users_with_preferences": 45,
            "total_unique_disliked_items": 25,
            "average_dislikes_per_user": 3.2
        },
        "top_disliked_items": [
            {
                "food_item": "Broccoli",
                "dislike_count": 30,
                "percentage_of_users": 60.0,
                "severity": "critical",
                "recommendation": "Consider removing or reformulating broccoli"
            }
        ],
        "recommendations": {...}
    }
    """
    try:
        import admin_analytics_service
        
        limit = request.args.get('limit', default=20, type=int)
        insights = admin_analytics_service.get_admin_waste_insights(limit=limit)
        
        return jsonify({
            "success": True,
            **insights
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/admin/waste-by-category', methods=['GET'])
def get_waste_by_category():
    """Get waste insights grouped by food category."""
    try:
        import admin_analytics_service
        
        trends = admin_analytics_service.get_waste_trends_by_category()
        
        return jsonify({
            "success": True,
            **trends
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Serve the admin analytics dashboard."""
    return render_template('admin_dashboard.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Food Preference API",
        "database": "MongoDB Atlas"
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

def find_free_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    return None

if __name__ == '__main__':
    print("🚀 Starting Food Preference API")
    print("☁️  Using MongoDB Atlas (Cloud)")
    
    # Try to find an available port
    port = find_free_port(5000)
    if port is None:
        print("❌ Error: Could not find an available port")
        exit(1)
    
    if port != 5000:
        print(f"⚠️  Port 5000 is in use, using port {port} instead")
    
    print(f"\n🌐 Server running on:")
    print(f"   Local:   http://localhost:{port}")
    print(f"\n📱 To make this accessible anywhere:")
    print(f"   1. Open a new terminal")
    print(f"   2. Run this: ssh -R 80:localhost:port_number serveo.net")
    
    app.run(debug=True, host='0.0.0.0', port=port)