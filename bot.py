import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"привет {user_name}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /stop command"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"пока {user_name}")

def main():
    """Start the bot"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("Error: Set the TELEGRAM_BOT_TOKEN environment variable")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    
    # Start the bot
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
