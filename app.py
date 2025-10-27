from flask import Flask, request
from telegram.ext import Application
from telegram_bot import MovieBot
import os
import logging

app = Flask(__name__)

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
application = Application.builder().token(BOT_TOKEN).build()
movie_bot = MovieBot(BOT_TOKEN)

# Add handlers to application
movie_bot.setup_handlers(application)

@app.route('/')
def home():
    return "🎬 Movie Bot is running! Send /start to your Telegram bot."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram"""
    try:
        # Process the update
        update = Update.de_json(request.get_json(), application.bot)
        application.update_queue.put(update)
        return 'ok'
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook for PythonAnywhere"""
    pythonanywhere_url = os.getenv('PYTHONANYWHERE_URL', 'https://yourusername.pythonanywhere.com')
    webhook_url = f"{pythonanywhere_url}/webhook"
    
    try:
        success = application.bot.set_webhook(webhook_url)
        if success:
            return f"✅ Webhook set successfully to: {webhook_url}"
        else:
            return "❌ Failed to set webhook"
    except Exception as e:
        return f"❌ Error setting webhook: {str(e)}"

@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    """Remove webhook"""
    try:
        success = application.bot.delete_webhook()
        if success:
            return "✅ Webhook removed successfully"
        else:
            return "❌ Failed to remove webhook"
    except Exception as e:
        return f"❌ Error removing webhook: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)
