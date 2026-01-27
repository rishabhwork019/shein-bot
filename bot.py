import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

TOKEN = os.getenv("8433092044:AAFLcElVT1mjsiEX3mwzESTL6ZBqosZJVlA")
ADMIN_ID = 5951377518

orders = {}


# ================== HELPERS ==================

def generate_order_id():
    return "SH-" + "".join(random.choices(string.digits, k=6))


def get_voucher(file_name):
    if not os.path.exists(file_name):
        return None

    with open(file_name, "r") as f:
        lines = f.read().strip().splitlines()

    if not lines:
        return None

    code = lines[0]
    remaining = lines[1:]

    with open(file_name, "w") as f:
        f.write("\n".join(remaining))

    return code


# ================== START ==================

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("🛒 Buy Shein Voucher", callback_data="BUY")]]

    update.message.reply_text(
        "👗 Welcome to *Shein Voucher Store*\n\n"
        "🎟 Choose your discount voucher below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ================== BUTTON HANDLER ==================

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "BUY":
        keyboard = [
            [InlineKeyboardButton("🎟 ₹500 OFF | ₹20", callback_data="V500")],
            [InlineKeyboardButton("🎟 ₹1000 OFF | ₹50", callback_data="V1000")],
            [InlineKeyboardButton("🎟 ₹2000 OFF | ₹75", callback_data="V2000")],
            [InlineKeyboardButton("🎟 ₹4000 OFF | ₹150", callback_data="V4000")],
        ]

        query.edit_message_text(
            "🛍 Select your voucher:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in ["V500", "V1000", "V2000", "V4000"]:
        user = query.from_user
        order_id = generate_order_id()

        voucher_map = {
            "V500": ("₹500 OFF", 20),
            "V1000": ("₹1000 OFF", 50),
            "V2000": ("₹2000 OFF", 75),
            "V4000": ("₹4000 OFF", 150),
        }

        voucher_name, price = voucher_map[query.data]

        orders[order_id] = {
            "user_id": user.id,
            "username": user.username,
            "name": user.first_name,
            "voucher_type": query.data,
            "voucher_name": voucher_name,
            "price": price
        }

        query.edit_message_text(
            f"🧾 *Order Created*\n\n"
            f"Order ID: `{order_id}`\n"
            f"Voucher: {voucher_name}\n"
            f"Amount: ₹{price}\n\n"
            f"💳 Pay via UPI:\n"
            f"`sheinvouchear@ptyes`\n\n"
            f"📸 Send payment screenshot after payment.",
            parse_mode="Markdown"
        )

        # Notify admin
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📥 *New Order*\n\n"
                f"Order ID: `{order_id}`\n"
                f"User: {user.first_name}\n"
                f"User ID: `{user.id}`\n"
                f"Voucher: {voucher_name}\n"
                f"Amount: ₹{price}"
            ),
            parse_mode="Markdown"
        )


# ================== SCREENSHOT FORWARD ==================

def handle_photo(update: Update, context: CallbackContext):
    context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    update.message.reply_text("✅ Screenshot received. Waiting for verification.")


# ================== APPROVE ORDER ==================

def approve(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not context.args:
        update.message.reply_text("❌ Usage: /approve ORDER_ID")
        return

    order_id = context.args[0]

    if order_id not in orders:
        update.message.reply_text("❌ Order not found.")
        return

    order = orders[order_id]

    file_map = {
        "V500": "vouchers_500.txt",
        "V1000": "vouchers_1000.txt",
        "V2000": "vouchers_2000.txt",
        "V4000": "vouchers_4000.txt",
    }

    file_name = file_map[order["voucher_type"]]
    code = get_voucher(file_name)

    if not code:
        update.message.reply_text("❌ No vouchers left in stock!")
        return

    # Send voucher to user
    context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            "🎉 *Payment Verified!*\n\n"
            f"🎟 Your Shein Voucher Code:\n`{code}`\n\n"
            "Use it on Shein checkout 🛍"
        ),
        parse_mode="Markdown"
    )

    update.message.reply_text(f"✅ Voucher sent for Order {order_id}")

    del orders[order_id]


# ================== MAIN ==================

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(CommandHandler("approve", approve))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
