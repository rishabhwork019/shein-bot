from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)
from datetime import datetime

TOKEN = "8433092044:AAFLcElVT1mjsiEX3mwzESTL6ZBqosZJVlA"
ADMIN_ID = 5951377518

# 🧠 Store users (simple memory store)
USERS = set()


# ================= START =================
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    USERS.add(user.id)

    keyboard = [
        [InlineKeyboardButton("🛒 Buy Shein Discount Voucher", callback_data="BUY")]
    ]

    update.message.reply_text(
        "👗 *Welcome to Shein Voucher Store*\n\n"
        "Authentic Shein discount vouchers at best prices.\n\n"
        "Tap below to continue 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    # Notify admin
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "👤 *New User Started Bot*\n\n"
            f"Name: {user.first_name}\n"
            f"User ID: `{user.id}`\n"
            f"Username: @{user.username if user.username else 'NA'}\n"
            f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        ),
        parse_mode="Markdown"
    )


# ================= BUTTON HANDLER =================
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "BUY":
        keyboard = [
            [InlineKeyboardButton("🎟 ₹500 OFF | Pay ₹20", callback_data="V500")],
            [InlineKeyboardButton("🎟 ₹1K OFF | Pay ₹50", callback_data="V1000")],
            [InlineKeyboardButton("🎟 ₹2K OFF | Pay ₹75", callback_data="V2000")],
            [InlineKeyboardButton("🎟 ₹4K OFF | Pay ₹150", callback_data="V4000")],
        ]
        query.edit_message_text(
            "🛍 *Select your voucher:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data in ["V500", "V1000", "V2000", "V4000"]:
        query.edit_message_text(
            "💳 *Payment Details*\n\n"
            "UPI ID:\n"
            "`sheinvouchear@ptyes`\n\n"
            "📸 Please send payment screenshot here.",
            parse_mode="Markdown"
        )


# ================= FORWARD ALL NON-COMMAND MESSAGES =================
def forward_messages(update: Update, context: CallbackContext):
    user = update.message.from_user
    USERS.add(user.id)

    # Ignore admin messages
    if user.id == ADMIN_ID:
        return

    # Forward message
    context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )


# ================= SEND VOUCHER =================
def sendvoucher(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        code = context.args[1]

        context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 *Your Shein Voucher*\n\n"
                f"🎟 Code: `{code}`\n\n"
                "Apply at checkout on Shein.\n"
                "Happy Shopping 🛍"
            ),
            parse_mode="Markdown"
        )

        update.message.reply_text("✅ Voucher sent.")

    except:
        update.message.reply_text(
            "❌ Usage:\n/sendvoucher USER_ID CODE"
        )


# ================= BROADCAST =================
def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)
    if not message:
        update.message.reply_text("❌ Usage:\n/broadcast MESSAGE")
        return

    sent = 0
    for user_id in USERS:
        try:
            context.bot.send_message(chat_id=user_id, text=message)
            sent += 1
        except:
            pass

    update.message.reply_text(f"📢 Broadcast sent to {sent} users.")


# ================= SEND TO SPECIFIC USER =================
def send(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        message = " ".join(context.args[1:])

        context.bot.send_message(chat_id=user_id, text=message)
        update.message.reply_text("✅ Message sent.")

    except:
        update.message.reply_text(
            "❌ Usage:\n/send USER_ID MESSAGE"
        )


# ================= MAIN =================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(CommandHandler("sendvoucher", sendvoucher))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("send", send))

    # Forward all non-command messages
    dp.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.document, forward_messages))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
