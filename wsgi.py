import sys
import os

# Add your project directory to the Python path
path = '/home/yourusername/movie-bot'
if path not in sys.path:
    sys.path.insert(0, path)

# Import the Flask app
from app import app as application

# Set environment variables (you can also set these in PythonAnywhere dashboard)
os.environ['BOT_TOKEN'] = 'your_bot_token_here'
os.environ['TMDB_API_KEY'] = 'your_tmdb_api_key_here'
os.environ['PYTHONANYWHERE_URL'] = 'https://yourusername.pythonanywhere.com'
