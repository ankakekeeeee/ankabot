import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8870706943:AAGxDZkEV-bfVAETv4566nBE6jUpekISNJA"
ADMIN_CHAT_ID = "BURAYA_KENDI_TELEGRAM_IDNIZI_YAZIN"  # Dekontların geleceği Telegram ID'niz

# Conversation durumları
WAITING_DEKONT = 1

# Ürün Linkleri
VIP_KANALLAR = [
    "https://t.me/+Aqi4UqSzr4JjZmRk",
    "https://t.me/+H2z-xlyZ6zM0OTE0",
    "https://t.me/+p01bQp6XeMmI0",
    "https://t.me/+HqtuwLtoMkkwMWQ0",
    "https://t.me/+BcHhS86B9ocyMWQ0"
]

# Ana Menü Oluşturucu
def build_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔞 Türk +18 VIP Paket (350 TL)", callback_data="buy_turk_18")
        ],
        [
            InlineKeyboardButton("📲 SMS Onay Paneline Giriş", url="https://sonpanelanka.onrender.com/")
        ],
        [
            InlineKeyboardButton("🛡️ ANKA GÜVENCE KANALI", url="https://t.me/ankaguvence"),
            InlineKeyboardButton("💬 Canlı Destek / Admin", url="https://t.me/vipankaa")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start Komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 **ANKA VIP BOT'A HOŞ GELDİNİZ** 🌟\n\n"
        "Aşağıdaki menüyü kullanarak VIP içeriklerimize erişebilir, SMS Onay Paneline katılabilir "
        "veya güvence kanalımızı inceleyebilirsiniz.\n\n"
        "👇 **Lütfen işlem yapmak istediğiniz seçeneğe tıklayın:**"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=build_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=build_main_keyboard())

# Ürün Satın Alma Ekranı
async def buy_turk_18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    details_text = (
        "🔥 **TÜRK +18 VIP PAKETİ SATIN ALMA TALİMATLARI** 🔥\n\n"
        "📦 **Paket İçeriği:** 5 Adet Özel VIP Telegram Kanalı\n"
        "💰 **Fiyat:** 350 TL (Tek Seferlik Ödeme)\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "💳 **BANKA ÖDEME BİLGİLERİ:**\n\n"
        "🔹 **IBAN:** `TR62 0006 2000 5000 0006 8107 73`\n"
        "🔹 **Alıcı Adı Soyadı:** Resul Sakal\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        "📌 **AÇIKLAMA / NASIL SATIN ALINIR?**\n"
        "1️⃣ Yukarıda verilen IBAN adresine **350 TL** transferini gerçekleştirin.\n"
        "2️⃣ Ödemeyi tamamladıktan sonra dekontunuzun (ekran görüntüsü veya PDF) çıktısını alın.\n"
        "3️⃣ Aşağıdaki **'📄 Dekont Gönder'** butonuna basarak dekontunuzu bota yükleyin.\n"
        "4️⃣ Sistem yöneticilerimiz dekontunuzu kontrol ettikten hemen sonra VIP linkleriniz otomatik olarak tarafınıza iletilecektir.\n\n"
        "⚡ *Herhangi bir sorunuz olursa menüdeki Canlı Destek butonundan bize ulaşabilirsiniz.*"
    )

    keyboard = [
        [InlineKeyboardButton("📄 Dekont Gönder", callback_data="send_dekont")],
        [InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="go_main")]
    ]

    await query.edit_message_text(details_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Dekont Bekleme Durumu
async def prompt_dekont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query
