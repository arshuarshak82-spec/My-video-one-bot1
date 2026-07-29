import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_ceo_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ ᴄᴏɴᴛᴀᴄᴛ ᴄᴇᴏ 🛡️", url="https://t.me/ARSHAK74")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "AR Downloader Bot\n\n"
        "Send me any video link from YouTube, Instagram, or Facebook to download video or audio."
    )
    await update.message.reply_text(welcome_text, reply_markup=get_ceo_button())

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data['url'] = url
    
    keyboard = [
        [InlineKeyboardButton("🎵 MP3 (Low)", callback_data='mp3_low'), InlineKeyboardButton("🎵 MP3 (Medium)", callback_data='mp3_med'), InlineKeyboardButton("🎵 MP3 (High/HD)", callback_data='mp3_high')],
        [InlineKeyboardButton("🎧 M4A (Low)", callback_data='m4a_low'), InlineKeyboardButton("🎧 M4A (Medium)", callback_data='m4a_med'), InlineKeyboardButton("🎧 M4A (High/HD)", callback_data='m4a_high')],
        [InlineKeyboardButton("📱 MP4 (Low Quality)", callback_data='mp4_low')],
        [InlineKeyboardButton("💻 MP4 (Medium Quality)", callback_data='mp4_med')],
        [InlineKeyboardButton("🖥️ MP4 (High/HD Quality)", callback_data='mp4_high')],
        [InlineKeyboardButton("🛡️ ᴄᴏɴᴛᴀᴄᴛ ᴄᴇᴏ 🛡️", url="https://t.me/ARSHAK74")]
    ]
    await update.message.reply_text("Please select your preferred format and quality:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    url = context.user_data.get('url')
    
    await query.edit_message_text(f"Downloading... Please wait.")
    
    is_audio = False
    filename = 'file.mp4'
    ydl_opts = {}
    
    if choice.startswith('mp3'):
        is_audio = True
        filename = 'audio.mp3'
        quality = '64' if 'low' in choice else ('128' if 'med' in choice else '320')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        }
    elif choice.startswith('m4a'):
        is_audio = True
        filename = 'audio.m4a'
        quality = '64' if 'low' in choice else ('128' if 'med' in choice else '320')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': quality,
            }],
        }
    elif choice == 'mp4_low':
        filename = 'video.mp4'
        ydl_opts = {'format': 'worst[ext=mp4]/worst', 'outtmpl': filename}
    elif choice == 'mp4_med':
        filename = 'video.mp4'
        ydl_opts = {'format': 'best[height<=480][ext=mp4]/best[height<=480]', 'outtmpl': filename}
    elif choice == 'mp4_high':
        filename = 'video.mp4'
        ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': filename}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if is_audio:
            with open(filename, 'rb') as audio_file:
                await query.message.reply_voice(voice=audio_file, reply_markup=get_ceo_button())
        else:
            with open(filename, 'rb') as video_file:
                await query.message.reply_video(video=video_file, reply_markup=get_ceo_button())
        
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        await query.message.reply_text(f"Error: {str(e)}", reply_markup=get_ceo_button())
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    TOKEN = '8809575029:AAH82KEPaVKB5wkBzgHPrNPE9g0FQMGrQc8'
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    app.add_handler(CallbackQueryHandler(button_click))
    
    app.run_polling()
