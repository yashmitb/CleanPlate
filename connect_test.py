from pymongo import MongoClient

# Connection string format
connection_string = "mongodb+srv://cleanplate:cleanplatepassword@cluster0.foodapp.mongodb.net/?retryWrites=true&w=majority"

# Create client
client = MongoClient(connection_string)

# Access a database
db = client['foodapp']

# Access a collection
collection = db['users']

# Test the connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting: {e}")