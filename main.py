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

BOT_TOKEN = "8870706943:AAETY5GWKKWF3p5NrZPoV93dbRrCD5QLXjs"
ADMIN_CHAT_ID = "8835514842"  # Dekontların geleceği Telegram ID'niz

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
        "4️⃣ Sistem yöneticilerimiz dekontunuzu kontrol ettikten hemen sonraVIP linkleriniz otomatik olarak tarafınıza iletilecektir.\n\n"
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
    await query.answer()

    await query.edit_message_text(
        "📸 **Lütfen ödemenize ait dekontu (fotoğraf veya belge) bu mesaja yanıt olarak gönderin.**\n\n"
        "❌ İptal etmek için /cancel yazabilirsiniz.",
        parse_mode="Markdown"
    )
    return WAITING_DEKONT

# Dekontu Alıp Admin'e İletme
async def receive_dekont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Kullanıcıya bilgi ver
    await update.message.reply_text(
        "⏳ **Dekontunuz başarıyla alındı!**\n\n"
        "Ödemeniz yetkililerimiz tarafından kontrol ediliyor. Onaylandığı anda linkleriniz buradan gönderilecektir.",
        parse_mode="Markdown"
    )

    # Admin'e İlet
    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Onayla ve Linkleri Gönder", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reddet", callback_data=f"reject_{user.id}")
        ]
    ])

    admin_msg = (
        f"🚨 **YENİ ÖDEME DEKONTU!**\n\n"
        f"👤 **Kullanıcı:** {user.full_name} (@{user.username})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"📦 **Ürün:** Türk +18 VIP (350 TL)"
    )

    if update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=update.message.photo[-1].file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=admin_keyboard)
    elif update.message.document:
        await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=update.message.document.file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=admin_keyboard)
    
    return ConversationHandler.END

# Admin Onay/Red İşlemleri
async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "approve":
        # Kullanıcıya Kanalları Gönder
        links_formatted = "\n".join([f"🔗 [VIP Kanal {i+1}]({link})" for i, link in enumerate(VIP_KANALLAR)])
        success_text = (
            "🎉 **ÖDEMENİZ ONAYLANDI!** 🎉\n\n"
            "Satın aldığınız **Türk +18 VIP Paket** linkleriniz aşağıdadır. "
            "Linklere tıklayarak kanallara katılabilirsiniz:\n\n"
            f"{links_formatted}\n\n"
            "✨ Bizi tercih ettiğiniz için teşekkür ederiz!"
        )
        
        await context.bot.send_message(chat_id=user_id, text=success_text, parse_mode="Markdown", disable_web_page_preview=True)
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ **ÖDEMA ONAYLANDI VE LİNKLER İLETİLDİ.**")

    elif action == "reject":
        reject_text = (
            "❌ **Ödemeniz Onaylanmadı!**\n\n"
            "Gönderdiğiniz dekont doğrulanamadı. Bir hata olduğunu düşünüyorsanız lütfen @vipankaa adresi üzerinden iletişime geçin."
        )
        await context.bot.send_message(chat_id=user_id, text=reject_text, parse_mode="Markdown")
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ **ÖDEMA REDDEDİLDİ.**")

# İşlem İptali
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("İşlem iptal edildi.", reply_markup=build_main_keyboard())
    return ConversationHandler.END

# Ana Menüye Dönüş Callback
async def go_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    welcome_text = (
        "🌟 **ANKA VIP BOT'A HOŞ GELDİNİZ** 🌟\n\n"
        "Aşağıdaki menüyü kullanarak VIP içeriklerimize erişebilir, SMS Onay Paneline katılabilir "
        "veya güvence kanalımızı inceleyebilirsiniz.\n\n"
        "👇 **Lütfen işlem yapmak istediğiniz seçeneğe tıklayın:**"
    )
    await query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=build_main_keyboard())

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation Handler (Dekont Akışı)
    dekont_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(prompt_dekont, pattern="^send_dekont$")],
        states={
            WAITING_DEKONT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_dekont)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_turk_18_callback, pattern="^buy_turk_18$"))
    app.add_handler(CallbackQueryHandler(go_main_callback, pattern="^go_main$"))
    app.add_handler(CallbackQueryHandler(handle_admin_action, pattern="^(approve|reject)_"))
    app.add_handler(dekont_handler)

    print("Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
