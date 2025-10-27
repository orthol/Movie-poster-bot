import sys
import os

# Add your project directory to the Python path
path = '/home/orthol/movie-bot'
if path not in sys.path:
    sys.path.insert(0, path)

# Import the Flask app
from app import app as application

# Set environment variables (you can also set these in PythonAnywhere dashboard)
os.environ['BOT_TOKEN'] = '914686489:AAFiBRO_twxrFJexdlpimuOIlAa_qM8oUbE'
os.environ['TMDB_API_KEY'] = '2197eff09f710270032b79e6ceabdcdb'
os.environ['PYTHONANYWHERE_URL'] = 'https://yourusername.pythonanywhere.com'
