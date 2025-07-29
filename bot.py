from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import os

# Bot token and admin ID from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8312166299:AAHufnKmqsgDQ0WfBbXAA4k9GVxDUtcgmLs")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6118937921"))
WELCOME_PHOTO = "https://ibb.co/fYjnXNjD"  # ImgBB URL

# Set to store user IDs
user_ids = set()
# Dictionary to map forwarded message ID to user ID
message_id_to_user_id = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)  # User ko add karo

    # Welcome message ke liye buttons (ek line mein ek)
    keyboard = [
        [InlineKeyboardButton("Register now", url="http://lakshmiwin.com/register?campaignId=prize")],
        [InlineKeyboardButton("Join Lakshmiwin now", url="http://lakshmiwin.com/register?campaignId=prize")],
        [InlineKeyboardButton("Message on Whatsapp", url="https://wa.link/Lakshmiwin")],
        [InlineKeyboardButton("Join our Telegram Channel", url="https://t.me/+pQNlTK5rRZhlNTVl")],
        [InlineKeyboardButton("Our open group", url="https://t.me/+YE1qMd28Urg1M2Q1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Welcome message with photo
    try:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption="♻️ WELCOME TO LAKSHMIWIN BOOK ♻️!",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(
            f"Photo load nahi hua: {str(e)}\nCaption: ♻️ WELCOME TO LAKSHMIWIN BOOK ♻️!",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message

    # Agar admin message bhejta hai
    if user_id == ADMIN_ID:
        # Check if admin replied to a forwarded message
        if message.reply_to_message:
            # Forwarded message ka ID check karo
            forwarded_message_id = message.reply_to_message.message_id
            target_user_id = message_id_to_user_id.get(forwarded_message_id)

            if target_user_id:
                try:
                    # Admin ka reply user ko bhejo
                    if message.photo:
                        await context.bot.send_photo(
                            chat_id=target_user_id,
                            photo=message.photo[-1].file_id,
                            caption=message.caption if message.caption else "Admin ka reply!"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=message.text if message.text else "Admin ka reply!"
                        )
                    await update.message.reply_text(f"Reply bheja user {target_user_id} ko!")
                except Exception as e:
                    await update.message.reply_text(f"Reply bhejne mein error: {str(e)}\nTarget User ID: {target_user_id}")
            else:
                await update.message.reply_text("Target user ID nahi mila. Forwarded message pe reply karein.")
            return

        # Admin ka naya message broadcast karo
        if message.photo or message.text:
            # Broadcast ke liye buttons (ek line mein ek)
            keyboard = [
                [InlineKeyboardButton("Register now", url="http://lakshmiwin.com/register?campaignId=prize")],
                [InlineKeyboardButton("Join Lakshmiwin now", url="http://lakshmiwin.com/register?campaignId=prize")],
                [InlineKeyboardButton("Message on Whatsapp", url="https://wa.link/Lakshmiwin")],
                [InlineKeyboardButton("Join our Telegram Channel", url="https://t.me/+pQNlTK5rRZhlNTVl")],
                [InlineKeyboardButton("Our open group", url="https://t.me/+YE1qMd28Urg1M2Q1")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            caption = message.caption if message.caption else (
                "Exclusive A To Z Bets Available 🔥\n"
                "500%% Signup Bonus\n"
                "Minimum ID Just 300 Rs\n"
                "Minimum Bet Just 100 Rs\n"
                "24*7 Super Fast Service\n"
                "Biggest Book of India"
            )
            photo = message.photo[-1].file_id if message.photo else None

            sent_count = 0
            failed_count = 0
            failed_users = []

            for uid in user_ids:
                try:
                    if photo:
                        await context.bot.send_photo(
                            chat_id=uid,
                            photo=photo,
                            caption=caption,
                            reply_markup=reply_markup
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=uid,
                            text=message.text if message.text else caption,
                            reply_markup=reply_markup
                        )
                    sent_count += 1
                    await asyncio.sleep(0.05)  # Telegram rate limits ke liye
                except Exception as e:
                    failed_count += 1
                    failed_users.append(f"User {uid}: {str(e)}")
                    print(f"Error bhejne mein {uid}: {e}")

            # Admin ko detailed confirmation bhejo
            if failed_count == 0:
                await update.message.reply_text(f"Message {sent_count} users ko bhej diya!")
            else:
                await update.message.reply_text(
                    f"Message {sent_count} users ko bheja, {failed_count} users ko nahi bheja gaya.\nErrors:\n" + "\n".join(failed_users)
                )
            return

    # Non-admin ke messages admin ko forward karo
    else:
        if message.photo or message.text:
            try:
                # Forward message aur user ID save karo
                forwarded_message = await context.bot.forward_message(
                    chat_id=ADMIN_ID,
                    from_chat_id=user_id,
                    message_id=message.message_id
                )
                # Forwarded message ka ID aur user ID map karo
                message_id_to_user_id[forwarded_message.message_id] = user_id
            except Exception as e:
                print(f"Error forwarding message from {user_id}: {e}")

def main():
    # Bot initialize karo
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers add karo
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))

    # Bot start karo
    print("Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
