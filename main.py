from typing import Final
from telegram import Update
from telegram.ext import *
import secrets

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('')

async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.upper()
    await update.message.reply_text(response)

async def handle_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я не работаю с картинками")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('end', end_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_images))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling...")
    app.run_polling()
