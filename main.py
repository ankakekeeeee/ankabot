import logging
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# -------------------- AYARLAR --------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("8870706943:AAFHGzWmIirFwynis6waxrRaZ49MJpFnvFs", "").strip()
ADMIN_CHAT_ID = os.getenv("8835514842", "").strip()

WAITING_DEKONT = 1

VIP_KANALLAR = [
    "https://t.me/+Aqi4UqSzr4JjZmRk",
    "https://t.me/+H2z-xlyZ6zM0OTE0",
    "https://t.me/+p01bQp6XeMmI0",
    "https://t.me/+HqtuwLtoMkkwMWQ0",
    "https://t.me/+BcHhS86B9ocyMWQ0",
]

# -------------------- MENÜLER --------------------

def build_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🔞 Türk +18 VIP Paket (350 TL)",
                callback_data="buy_turk_18",
            )
        ],
        [
            InlineKeyboardButton(
                "📲 SMS Onay Paneline Giriş",
                url="https://sonpanelanka.onrender.com/",
            )
        ],
        [
            InlineKeyboardButton(
                "🛡️ ANKA GÜVENCE KANALI",
                url="https://t.me/ankaguvence",
            ),
            InlineKeyboardButton(
                "💬 Canlı Destek / Admin",
                url="https://t.me/vipankaa",
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📄 Dekont Gönder",
            callback_data="send_dekont",
        )],
        [InlineKeyboardButton(
            "🔙 Ana Menüye Dön",
            callback_data="go_main",
        )],
    ])


def admin_keyboard(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Ödemeyi Onayla",
                callback_data=f"approve:{user_id}",
            ),
            InlineKeyboardButton(
                "❌ Reddet",
                callback_data=f"reject:{user_id}",
            ),
        ]
    ])


# -------------------- BAŞLANGIÇ --------------------

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "🌟 *ANKA VIP BOT'A HOŞ GELDİNİZ* 🌟\n\n"
        "Aşağıdaki menüden istediğiniz işlemi seçebilirsiniz.\n\n"
        "👇 *Lütfen bir seçenek belirleyin:*"
    )

    if update.message:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_main_keyboard(),
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_main_keyboard(),
        )


# -------------------- SATIN ALMA --------------------

async def buy_turk_18_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    details_text = (
        "🔥 *TÜRK +18 VIP PAKETİ SATIN ALMA* 🔥\n\n"
        "📦 *Paket içeriği:* 5 özel VIP Telegram kanalı\n"
        "💰 *Fiyat:* 350 TL\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💳 *BANKA ÖDEME BİLGİLERİ*\n\n"
        "🔹 *IBAN:* `TR62 0006 2000 5000 0006 8107 73`\n"
        "🔹 *Alıcı:* Resul Sakal\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "*NASIL SATIN ALINIR?*\n"
        "1. Belirtilen hesaba 350 TL gönderin.\n"
        "2. Ödeme dekontunuzu hazırlayın.\n"
        "3. Aşağıdaki Dekont Gönder butonuna basın.\n"
        "4. Yönetici ödemenizi kontrol edecektir.\n\n"
        "⚠️ Ödeme doğrulanmadan VIP bağlantıları gönderilmez."
    )

    await query.edit_message_text(
        details_text,
        parse_mode="Markdown",
        reply_markup=payment_keyboard(),
    )


# -------------------- DEKONT İŞLEMLERİ --------------------

async def prompt_dekont(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📄 Lütfen ödeme dekontunuzu fotoğraf veya PDF "
        "dosyası olarak gönderin.\n\n"
        "İşlemi iptal etmek için /cancel yazabilirsiniz."
    )

    return WAITING_DEKONT


async def receive_dekont(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not ADMIN_CHAT_ID:
        await update.message.reply_text(
            "⚠️ Yönetici ayarları henüz yapılandırılmamış. "
            "Lütfen daha sonra tekrar deneyin."
        )
        return ConversationHandler.END

    user = update.effective_user
    message = update.message

    if not message.photo and not (
        message.document
        and message.document.mime_type == "application/pdf"
    ):
        await message.reply_text(
            "Lütfen dekontu fotoğraf veya PDF olarak gönderin."
        )
        return WAITING_DEKONT

    context.user_data["pending_payment"] = True

    caption = (
        "🧾 *YENİ ÖDEME DEKONTU*\n\n"
        f"👤 Kullanıcı: {user.full_name}\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"🔗 Kullanıcı adı: @{user.username or 'yok'}\n\n"
        "Ödemeyi kontrol edip aşağıdan karar verin."
    )

    try:
        if message.photo:
            await context.bot.send_photo(
                chat_id=int(ADMIN_CHAT_ID),
                photo=message.photo[-1].file_id,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=admin_keyboard(user.id),
            )
        else:
            await context.bot.send_document(
                chat_id=int(ADMIN_CHAT_ID),
                document=message.document.file_id,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=admin_keyboard(user.id),
            )

        await message.reply_text(
            "✅ Dekontunuz yöneticiye iletildi.\n"
            "Ödeme kontrol edildikten sonra size bilgi verilecektir."
        )

    except Exception:
        logger.exception("Dekont yöneticiye gönderilemedi.")
        await message.reply_text(
            "❌ Dekont gönderilemedi. Lütfen daha sonra tekrar deneyin."
        )

    return ConversationHandler.END


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.pop("pending_payment", None)
    await update.message.reply_text(
        "İşlem iptal edildi.",
        reply_markup=build_main_keyboard(),
    )
    return ConversationHandler.END


# -------------------- YÖNETİCİ ONAYI --------------------

async def payment_decision(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    if not ADMIN_CHAT_ID:
        await query.message.reply_text("Yönetici ayarı eksik.")
        return

    if str(query.from_user.id) != ADMIN_CHAT_ID:
        await query.answer(
            "Bu işlemi yalnızca yönetici yapabilir.",
            show_alert=True,
        )
        return

    action, user_id_text = query.data.split(":", 1)
    user_id = int(user_id_text)

    if action == "approve":
        try:
            links_text = (
                "🎉 *Ödemeniz onaylandı!*\n\n"
                "VIP kanal bağlantılarınız aşağıdadır:\n\n"
            )

            for index, link in enumerate(VIP_KANALLAR, start=1):
                links_text += f"{index}. {link}\n"

            await context.bot.send_message(
                chat_id=user_id,
                text=links_text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

            await query.edit_message_caption(
                caption=(
                    (query.message.caption or "")
                    + "\n\n✅ Ödeme onaylandı."
                ),
            )

        except Exception:
            logger.exception("Onay işlemi tamamlanamadı.")
            await query.message.reply_text(
                "Kullanıcıya mesaj gönderilemedi. "
                "Kullanıcının botu başlattığını ve bağlantıların "
                "geçerli olduğunu kontrol edin."
            )

    elif action == "reject":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ Dekontunuz onaylanmadı. "
                    "Lütfen ödemenizi ve dekontunuzu kontrol edin "
                    "veya canlı destekle iletişime geçin."
                ),
            )

            await query.edit_message_caption(
                caption=(
                    (query.message.caption or "")
                    + "\n\n❌ Ödeme reddedildi."
                ),
            )

        except Exception:
            logger.exception("Ret bildirimi gönderilemedi.")
            await query.message.reply_text(
                "Kullanıcıya ret bildirimi gönderilemedi."
            )


# -------------------- ANA MENÜ --------------------

async def go_main(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🌟 *ANKA VIP BOT ANA MENÜ* 🌟\n\n"
        "Lütfen yapmak istediğiniz işlemi seçin.",
        parse_mode="Markdown",
        reply_markup=build_main_keyboard(),
    )


async def unknown_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Lütfen menüdeki seçenekleri kullanın veya /start yazın."
    )


# -------------------- HATA YÖNETİMİ --------------------

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "İşlenmeyen bot hatası:",
        exc_info=context.error,
    )


# -------------------- BOTU ÇALIŞTIR --------------------

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN eksik. Render Environment Variables "
            "bölümüne BOT_TOKEN ekleyin."
        )

    if not ADMIN_CHAT_ID or not ADMIN_CHAT_ID.lstrip("-").isdigit():
        raise RuntimeError(
            "ADMIN_CHAT_ID eksik veya geçersiz. "
            "Yönetici Telegram kullanıcı ID'nizi girin."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                prompt_dekont,
                pattern="^send_dekont$",
            )
        ],
        states={
            WAITING_DEKONT: [
                MessageHandler(
                    filters.PHOTO | filters.Document.PDF,
                    receive_dekont,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(
            buy_turk_18_callback,
            pattern="^buy_turk_18$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(go_main, pattern="^go_main$")
    )
    application.add_handler(
        CallbackQueryHandler(
            payment_decision,
            pattern="^(approve|reject):\\d+$",
        )
    )
    application.add_handler(conversation)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Bot başlatılıyor...")
    application.run_polling()


if __name__ == "__main__":
    main()
