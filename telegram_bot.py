import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MovieBot:
    def __init__(self, token):
        self.token = token
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        
    async def start(self, update: Update, context: CallbackContext) -> None:
        """Send welcome message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
🎬 Welcome to Movie Updates Bot, {user.first_name}!

I'll keep you updated with the latest movie information including:
• New Releases
• Ratings & Reviews
• Release Dates
• Movie Descriptions
• And much more!

Available Commands:
/start - Show this welcome message
/latest - Get latest movie updates
/trending - Trending movies this week
/upcoming - Upcoming movies
/search <movie_name> - Search for a specific movie
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Latest Movies", callback_data="latest")],
            [InlineKeyboardButton("🔥 Trending", callback_data="trending")],
            [InlineKeyboardButton("📅 Upcoming", callback_data="upcoming")],
            [InlineKeyboardButton("🔍 Search Movie", callback_data="search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    def get_movies(self, endpoint, params=None):
        """Generic method to fetch movies from TMDB API"""
        url = f"{self.tmdb_base_url}/{endpoint}"
        default_params = {
            'api_key': self.tmdb_api_key,
            'language': 'en-US'
        }
        if params:
            default_params.update(params)
            
        try:
            response = requests.get(url, params=default_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error: {e}")
            return None

    def format_movie_message(self, movie):
        """Format movie data into a readable message"""
        title = movie.get('title', 'N/A')
        release_date = movie.get('release_date', 'TBA')
        rating = movie.get('vote_average', 'N/A')
        overview = movie.get('overview', 'No description available.')
        popularity = movie.get('popularity', 'N/A')
        
        # Truncate overview if too long
        if len(overview) > 400:
            overview = overview[:400] + "..."
            
        message = f"""
🎬 <b>{title}</b>

📅 <b>Release Date:</b> {release_date}
⭐ <b>Rating:</b> {rating}/10
🔥 <b>Popularity:</b> {popularity}

📖 <b>Description:</b>
{overview}
        """
        
        # Add poster if available
        poster_path = movie.get('poster_path')
        if poster_path:
            return message, f"{self.image_base_url}{poster_path}"
        
        return message, None

    async def send_latest_movies(self, update: Update, context: CallbackContext):
        """Send latest movie updates"""
        query = update.callback_query
        if query:
            await query.answer()
            chat_id = query.message.chat_id
        else:
            chat_id = update.message.chat_id

        await context.bot.send_chat_action(chat_id, action='typing')
        
        # Get now playing movies
        data = self.get_movies("movie/now_playing", {'page': 1})
        
        if not data or 'results' not in data:
            await self.send_error_message(context, chat_id)
            return

        movies = data['results'][:5]
        
        for movie in movies:
            message, poster_url = self.format_movie_message(movie)
            
            if poster_url:
                try:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=poster_url,
                        caption=message,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='HTML'
                    )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )

    async def send_trending_movies(self, update: Update, context: CallbackContext):
        """Send trending movies"""
        query = update.callback_query
        await query.answer()
        
        await context.bot.send_chat_action(query.message.chat_id, action='typing')
        
        data = self.get_movies("trending/movie/week")
        
        if not data or 'results' not in data:
            await self.send_error_message(context, query.message.chat_id)
            return

        movies = data['results'][:5]
        
        for movie in movies:
            message, poster_url = self.format_movie_message(movie)
            
            if poster_url:
                try:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=poster_url,
                        caption=message,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=message,
                        parse_mode='HTML'
                    )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='HTML'
                )

    async def send_upcoming_movies(self, update: Update, context: CallbackContext):
        """Send upcoming movies"""
        query = update.callback_query
        await query.answer()
        
        await context.bot.send_chat_action(query.message.chat_id, action='typing')
        
        data = self.get_movies("movie/upcoming")
        
        if not data or 'results' not in data:
            await self.send_error_message(context, query.message.chat_id)
            return

        movies = data['results'][:5]
        
        for movie in movies:
            message, poster_url = self.format_movie_message(movie)
            
            if poster_url:
                try:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=poster_url,
                        caption=message,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=message,
                        parse_mode='HTML'
                    )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='HTML'
                )

    async def search_movie(self, update: Update, context: CallbackContext):
        """Search for a specific movie"""
        if not context.args:
            await update.message.reply_text("Please provide a movie name. Example: /search Avengers")
            return

        movie_name = " ".join(context.args)
        await context.bot.send_chat_action(update.message.chat_id, action='typing')
        
        data = self.get_movies("search/movie", {'query': movie_name})
        
        if not data or 'results' not in data or not data['results']:
            await update.message.reply_text(f"No movies found for '{movie_name}'")
            return

        movie = data['results'][0]
        message, poster_url = self.format_movie_message(movie)
        
        if poster_url:
            try:
                await update.message.reply_photo(
                    photo=poster_url,
                    caption=message,
                    parse_mode='HTML'
                )
            except Exception as e:
                await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text(message, parse_mode='HTML')

    async def button_handler(self, update: Update, context: CallbackContext) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "latest":
            await self.send_latest_movies(update, context)
        elif query.data == "trending":
            await self.send_trending_movies(update, context)
        elif query.data == "upcoming":
            await self.send_upcoming_movies(update, context)
        elif query.data == "search":
            await query.message.reply_text("Use the command: /search <movie_name>")

    async def send_error_message(self, context, chat_id):
        """Send error message"""
        error_text = "❌ Sorry, I couldn't fetch movie data at the moment. Please try again later."
        await context.bot.send_message(chat_id=chat_id, text=error_text)

    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Send help message"""
        help_text = """
🤖 <b>Movie Bot Help</b>

<b>Commands:</b>
/start - Start the bot and see main menu
/latest - Get latest movie releases
/trending - See trending movies this week
/upcoming - Check upcoming movies
/search <movie_name> - Search for a specific movie
/help - Show this help message

<b>Features:</b>
• Latest movie updates
• Ratings and reviews
• Release dates
• Movie descriptions
• High-quality posters

Just click the buttons or use commands to explore!
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    def setup_handlers(self, application):
        """Setup all command handlers"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("latest", self.send_latest_movies))
        application.add_handler(CommandHandler("trending", self.send_trending_movies))
        application.add_handler(CommandHandler("upcoming", self.send_upcoming_movies))
        application.add_handler(CommandHandler("search", self.search_movie))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
