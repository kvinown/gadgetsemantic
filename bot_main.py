from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import semantic_engine 

# --- GANTI TOKEN BOT ANDA DI SINI ---
BOT_TOKEN = '8532630010:AAHHhX3ZjAA8lsu7PxHQfvGAxcxaKUAXYCE' 
# (Pastikan token ini benar, jika error ganti dengan token dari BotFather)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Halo! Saya Assistant Gadget Semantik.</b>\n\n"
        "Saya bisa membantu mencari HP berdasarkan kebutuhan spesifik Anda.\n\n"
        "💡 <b>Contoh Pencarian:</b>\n"
        "• <i>'Cari hp buat nonton konser'</i> (Mencari fitur Zoom/Kamera Bagus)\n"
        "• <i>'Hp ojol murah baterai awet'</i> (Mencari Baterai Besar & Harga Murah)\n"
        "• <i>'Hp kompetitif buat main MLBB'</i> (Mencari Layar 120Hz+)\n"
        "• <i>'Hp gaming murah'</i> (Mencari RAM besar harga terjangkau)\n"
        "• <i>'Google Pixel'</i> (Mencari Brand spesifik)\n\n"
        "Silakan ketik kebutuhan Anda...",
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan_user = update.message.text.lower()
    
    await update.message.reply_text("🔍 Menganalisis permintaan semantik Anda...")
    
    # --- 1. INISIALISASI PARAMETER ---
    param_brand = None
    param_ram = 0
    param_price = 0
    param_scenario = None
    
    # --- 2. DETEKSI BRAND (Vocabulary Matching) ---
    if "samsung" in pesan_user:
        param_brand = "Samsung"
    elif "apple" in pesan_user or "iphone" in pesan_user:
        param_brand = "Apple"
    elif "xiaomi" in pesan_user or "redmi" in pesan_user or "poco" in pesan_user:
        param_brand = "Xiaomi" 
        if "poco" in pesan_user: param_brand = "Poco" # Override jika spesifik
    elif "asus" in pesan_user or "rog" in pesan_user:
        param_brand = "Asus"
    elif "infinix" in pesan_user or "gt" in pesan_user:
        param_brand = "Infinix"
    elif "itel" in pesan_user:
        param_brand = "Itel"
    elif "tecno" in pesan_user or "pova" in pesan_user:
        param_brand = "Tecno"
    elif "realme" in pesan_user:
        param_brand = "Realme"
    elif "vivo" in pesan_user:
        param_brand = "Vivo"
    elif "oppo" in pesan_user or "reno" in pesan_user:
        param_brand = "Oppo"
    elif "google" in pesan_user or "pixel" in pesan_user:
        param_brand = "Google"

    # --- 3. DETEKSI SKENARIO (Semantic Context) ---
    # Skenario 1: Konser (Butuh Telephoto / Zoom)
    if "konser" in pesan_user or "nonton" in pesan_user or "zoom" in pesan_user or "kamera" in pesan_user:
        param_scenario = "konser"
    
    # Skenario 2: Kompetitif (Butuh Refresh Rate Tinggi)
    elif "kompetitif" in pesan_user or "esport" in pesan_user or "120hz" in pesan_user or "144hz" in pesan_user:
        param_scenario = "kompetitif"
        
    # Skenario 3: Ojol / Driver (Butuh Baterai Besar)
    elif "ojol" in pesan_user or "driver" in pesan_user or "grab" in pesan_user or "gojek" in pesan_user or "baterai" in pesan_user or "awet" in pesan_user:
        param_scenario = "ojol"
    
    # Skenario 4: Roblox / Ringan
    elif "roblox" in pesan_user or "anak" in pesan_user:
        param_scenario = "roblox"

    # --- 4. DETEKSI SPEK DASAR & HARGA ---
    # Deteksi Gaming Umum (RAM Besar)
    if "gaming" in pesan_user or "game" in pesan_user or "berat" in pesan_user:
        # Jika user tidak minta skenario kompetitif, kita set minimal RAM
        if not param_scenario: 
            param_ram = 8 # Standar gaming entry
            
    # Deteksi Harga
    if "murah" in pesan_user or "budget" in pesan_user or "terjangkau" in pesan_user:
        param_price = 7000000 # Definisi umum murah (< 7jt)
        if "ojol" in pesan_user or "pelajar" in pesan_user:
            param_price = 3000000 # Definisi murah banget (< 3jt)
            
    elif "jutaan" in pesan_user: # Misal "Gaming 2 jutaan"
        param_price = 3000000

    # --- 5. EKSEKUSI KE OTAK SEMANTIK ---
    try:
        jawaban = semantic_engine.cari_rekomendasi(
            scenario=param_scenario,
            brand_dicari=param_brand, 
            min_ram=param_ram, 
            max_price=param_price
        )
    except Exception as e:
        jawaban = f"⚠️ Terjadi kesalahan pada sistem semantik: {str(e)}"

    # Kirim Balasan
    await update.message.reply_text(jawaban, parse_mode='HTML')

if __name__ == '__main__':
    print("🤖 Bot Gadget Semantik sedang berjalan...")
    print("Tekan Ctrl + C untuk berhenti.")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()