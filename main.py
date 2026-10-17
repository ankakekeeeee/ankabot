import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# =============== AYARLAR ===============
BOT_TOKEN = "8870706943:AAGZF6lhv153wsahoFCYrzJgQOhMM7xFLM8"
ADMIN_CHAT_ID = 8835514842  # Kendi Telegram kullanıcı ID'n

WAITING_DEKONT = 1

VIP_KANALLAR = [
    "https://t.me/+Aqi4UqSzr4JjZmRk",
    "https://t.me/+H2z-xlyZ6zM0OTE0",
    "https://t.me/+p01bQp6XeMmI0",
    "https://t.me/+HqtuwLtoMkkwMWQ0",
    "https://t.me/+BcHhS86B9ocyMWQ0",
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =============== MENÜ ===============
def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🔞 Türk +18 VIP Paket (350 TL)",
            callback_data="buy_turk_18",
        )],
        [InlineKeyboardButton(
            "📲 SMS Onay Paneline Giriş",
            url="https://sonpanelanka.onrender.com/",
        )],
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
    ])


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


# =============== START ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 *ANKA VIP BOT'A HOŞ GELDİNİZ* 🌟\n\n"
        "Aşağıdaki menüden istediğiniz işlemi seçebilirsiniz.\n\n"
        "👇 *Lütfen bir seçenek belirleyin:*"
    )
    await update.effective_message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_main_keyboard(),
    )


# =============== SATIN ALMA ===============
async def buy_turk_18_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    text = (
        "🔥 *TÜRK +18 VIP PAKETİ* 🔥\n\n"
        "📦 Paket içeriği: 5 özel VIP Telegram kanalı\n"
        "💰 Fiyat: 350 TL (tek seferlik)\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💳 *BANKA ÖDEME BİLGİLERİ*\n\n"
        "🔹 IBAN: `TR62 0006 2000 5000 0006 8107 73`\n"
        "🔹 Alıcı: Resul Sakal\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1. Belirtilen hesaba 350 TL gönderin.\n"
        "2. Dekontunuzu hazırlayın.\n"
        "3. Aşağıdaki Dekont Gönder butonuna basın.\n"
        "4. Yönetici ödemenizi kontrol edecektir.\n\n"
        "⚠️ Ödeme onaylanmadan VIP bağlantıları gönderilmez."
    )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=payment_keyboard(),
    )


# =============== DEKONT İSTEME ===============
async def prompt_dekont(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📄 Dekontunuzu fotoğraf veya PDF olarak gönderin.\n"
        "İptal etmek için /cancel yazın."
    )
    return WAITING_DEKONT


# =============== DEKONT ALMA ===============
async def receive_dekont(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    user = update.effective_user

    if not message.photo and not (
        message.document
        and message.document.mime_type == "application/pdf"
    ):
        await message.reply_text(
            "Lütfen dekontu fotoğraf veya PDF olarak gönderin."
        )
        return WAITING_DEKONT

    caption = (
        "🧾 YENİ ÖDEME DEKONTU\n\n"
        f"Kullanıcı: {user.full_name}\n"
        f"Telegram ID: {user.id}\n"
        f"Kullanıcı adı: @{user.username or 'yok'}\n\n"
        "Ödemeyi kontrol edip karar verin."
    )

    try:
        if message.photo:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_keyboard(user.id),
            )
        else:
            await context.bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=message.document.file_id,
                caption=caption,
                reply_markup=admin_keyboard(user.id),
            )

        await message.reply_text(
            "✅ Dekontunuz yöneticiye iletildi. "
            "Ödeme kontrol edildikten sonra bilgi verilecektir."
        )

    except Exception:
        logger.exception("Dekont gönderilemedi")
        await message.reply_text(
            "❌ Dekont gönderilemedi. Yönetici ID'sini kontrol edin."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "İşlem iptal edildi.",
        reply_markup=build_main_keyboard(),
    )
    return ConversationHandler.END


# =============== YÖNETİCİ KARARI ===============
async def payment_decision(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer(
            "Bu işlem yalnızca yöneticiye açıktır.",
            show_alert=True,
        )
        return

    await query.answer()
    action, user_text = query.data.split(":", 1)
    user_id = int(user_text)

    try:
        if action == "approve":
            links = "\n".join(
                f"{i}. {link}"
                for i, link in enumerate(VIP_KANALLAR, 1)
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🎉 Ödemeniz onaylandı!\n\n"
                    "VIP kanal bağlantılarınız:\n\n" + links
                ),
                disable_web_page_preview=True,
            )
            result = "✅ Ödeme onaylandı."

        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ Dekontunuz onaylanmadı. "
                    "Lütfen dekontunuzu kontrol edin veya destekle iletişime geçin."
                ),
            )
            result = "❌ Ödeme reddedildi."

        if query.message.caption is not None:
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n" + result,
                reply_markup=None,
            )
        else:
            await query.edit_message_text(result, reply_markup=None)

    except Exception:
        logger.exception("Yönetici kararı işlenemedi")
        await query.message.reply_text(
            "İşlem sırasında hata oluştu. Kullanıcının botu başlattığını kontrol edin."
        )


# =============== ANA MENÜ ===============
async def go_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌟 *ANKA VIP BOT ANA MENÜ* 🌟\n\nBir seçenek seçin:",
        parse_mode="Markdown",
        reply_markup=build_main_keyboard(),
    )


async def unknown_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.effective_message.reply_text(
        "Lütfen menü seçeneklerini kullanın veya /start yazın."
    )


async def error_handler(
    update: object, context: ContextTypes.DEFAULT_TYPE
):
    logger.error("Bot hatası: %s", context.error)


# =============== BOTU BAŞLAT ===============
def main():
    if BOT_TOKEN == "YENI_BOT_TOKENINI_BURAYA_YAZ" or not BOT_TOKEN:
        raise RuntimeError("Kodun başına yeni BOT_TOKEN değerini yaz.")

    if not isinstance(ADMIN_CHAT_ID, int) or ADMIN_CHAT_ID == 123456789:
        raise RuntimeError("ADMIN_CHAT_ID değerini kendi Telegram ID'n ile değiştir.")

    app = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(prompt_dekont, pattern="^send_dekont$")
        ],
        states={
            WAITING_DEKONT: [
                MessageHandler(
                    filters.PHOTO | filters.Document.PDF,
                    receive_dekont,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(
            buy_turk_18_callback,
            pattern="^buy_turk_18$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(go_main, pattern="^go_main$")
    )
    app.add_handler(
        CallbackQueryHandler(
            payment_decision,
            pattern=r"^(approve|reject):\d+$",
        )
    )
    app.add_handler(conversation)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message)
    )
    app.add_error_handler(error_handler)

    logger.info("Bot başlatılıyor...")
    app.run_polling()


if __name__ == "__main__":
    main()
