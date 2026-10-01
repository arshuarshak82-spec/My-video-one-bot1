
import logging
import os
import time
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest
import yt_dlp
import google.generativeai as genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

BOT_TOKEN = "8809575029:AAE1cL_RWB2x0R7w4dOyGqw_qyOVbnWbP_k"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

users_set = set()

def get_start_buttons():
  return InlineKeyboardMarkup([
      [
          InlineKeyboardButton("💬 Contact CEO", url="https://t.me/ARSHAK74"),
          InlineKeyboardButton("🔒 Privacy Policy", callback_data='privacy_policy'),
      ]
  ])

def get_ceo_button():
  return InlineKeyboardMarkup(
      [[InlineKeyboardButton("💬 Contact CEO", url="https://t.me/ARSHAK74")]]
  )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  if user:
    users_set.add(user.id)

  welcome_text = (
      "Welcome to **AR Downloader Bot**! 🚀\n\n"
      "You can download videos, audio, and media files seamlessly from YouTube, Instagram, "
      "Facebook, Apple Music, and other supported platforms.\n\n"
      "• Our Founder Arshak K.V.: (Visually Impaired, Political Science graduate, "
      "currently pursuing a Master’s degree in the discipline, and founder of 'Political Malayali').\n\n"
      "We kindly request everyone to share and make the most of this bot! If you encounter any issues, "
      "wish to share your valuable feedback, or want to suggest new features, please feel free to click the **Contact CEO** button below.\n\n"
      "Simply paste the **link** of the media you want to download into this chat and watch the magic happen! ✨"
  )
  await update.message.reply_text(
      welcome_text, reply_markup=get_start_buttons(), parse_mode="Markdown"
  )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  total_users = len(users_set)
  await update.message.reply_text(
      f"📊 **Bot Statistics**\n\n👥 Total Unique Users: {total_users}",
      parse_mode="Markdown",
      reply_markup=get_ceo_button()
  )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not context.args:
    await update.message.reply_text("⚠️ Please provide a message to broadcast. Usage: /broadcast Your message here")
    return
  
  message_text = " ".join(context.args)
  success_count = 0
  fail_count = 0

  status_msg = await update.message.reply_text("📢 Broadcasting message to users...")

  for uid in users_set:
    try:
      await context.bot.send_message(chat_id=uid, text=message_text)
      success_count += 1
    except Exception:
      fail_count += 1

  await status_msg.edit_text(
      f"✅ **Broadcast Completed!**\n\n"
      f"📤 Successful: {success_count}\n"
      f"❌ Failed: {fail_count}"
  )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  if user:
    users_set.add(user.id)

  text = update.message.text

  if 'http://' in text or 'https://' in text:
    context.user_data['url'] = text
    keyboard = [
        [
            InlineKeyboardButton("🎵 MP3 (Low)", callback_data='mp3_low'),
            InlineKeyboardButton("🎵 MP3 (Medium)", callback_data='mp3_med'),
            InlineKeyboardButton("🎵 MP3 (High/HD)", callback_data='mp3_high'),
        ],
        [
            InlineKeyboardButton("🎧 M4A (Low)", callback_data='m4a_low'),
            InlineKeyboardButton("🎧 M4A (Medium)", callback_data='m4a_med'),
            InlineKeyboardButton("🎧 M4A (High/HD)", callback_data='m4a_high'),
        ],
        [
            InlineKeyboardButton("📱 MP4 (Low)", callback_data='mp4_low'),
            InlineKeyboardButton("💻 MP4 (Medium)", callback_data='mp4_med'),
            InlineKeyboardButton("🖥️ MP4 (High/HD)", callback_data='mp4_high'),
        ],
        [InlineKeyboardButton("💬 Contact CEO", url="https://t.me/ARSHAK74")],
    ]
    await update.message.reply_text(
        "Please select your preferred format and quality (Optimized for Malayalam Thumbnail & Documentary processing):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
  else:
    try:
      response = gemini_model.generate_content(text)
      reply_text = response.text
      await update.message.reply_text(reply_text, reply_markup=get_ceo_button())
    except Exception as e:
      await update.message.reply_text(
          "Please send a valid media link (YouTube, Instagram, etc.) to download.",
          reply_markup=get_ceo_button()
      )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  choice = query.data

  if choice == 'privacy_policy':
    privacy_text = (
        "🔒 **Privacy Policy & DPDP Act Compliance**\n\n"
        "In accordance with the Digital Personal Data Protection (DPDP) Act "
        "and IT Act guidelines, we respect your privacy. We do not store "
        "your personal chats, downloaded media links, or personal data. "
        "All temporary files are automatically deleted after processing.\n\n"
        "For queries, contact our CEO."
    )
    await query.message.reply_text(
        privacy_text, reply_markup=get_ceo_button(), parse_mode="Markdown"
    )
    return

  url = context.user_data.get('url')
  if not url:
    await query.edit_message_text("⚠️ Error: Link not found. Please send the link again.")
    return

  await query.edit_message_text('📥 Downloading media (Optimized for Documentary/Malayalam processing)... Please wait.')

  is_audio = False
  ydl_opts = {
      'socket_timeout': 60,
      'retries': 20,
      'fragment_retries': 20,
      'noplaylist': True,
      'ignoreerrors': True,
      'no_warnings': True,
  }

  if os.path.exists('cookies.txt'):
    ydl_opts['cookiefile'] = 'cookies.txt'

  if choice.startswith('mp3'):
    is_audio = True
    quality = '64' if 'low' in choice else ('128' if 'med' in choice else '192')
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
    })
  elif choice.startswith('m4a'):
    is_audio = True
    quality = '64' if 'low' in choice else ('128' if 'med' in choice else '192')
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': quality,
        }],
    })
  elif choice == 'mp4_low':
    ydl_opts.update({
        'format': 'worst[ext=mp4]/worst',
        'outtmpl': 'downloaded_video.%(ext)s',
    })
  elif choice == 'mp4_med':
    ydl_opts.update({
        'format': 'best[height<=480][ext=mp4]/best[height<=480]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
    })
  elif choice == 'mp4_high':
    ydl_opts.update({
        'format': 'best[filesize<50M]/bestvideo[height<=480]+bestaudio/best[height<=480]',
        'outtmpl': 'downloaded_video.%(ext)s',
    })

  filename = None
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      if info:
        if 'entries' in info:
          info = info['entries'][0]

        filename = ydl.prepare_filename(info)
        media_title = info.get('title', 'Downloaded Media')

        if is_audio:
          base_name, _ = os.path.splitext(filename)
          filename = base_name + ('.mp3' if 'mp3' in choice else '.m4a')

    if filename and os.path.exists(filename):
      await query.edit_message_text('🚀 Uploading to Telegram... Please wait.')
      if is_audio:
        with open(filename, 'rb') as audio_file:
          await query.message.reply_audio(
              audio=audio_file,
              title=media_title,
              performer='Unknown',
              reply_markup=get_ceo_button(),
          )
      else:
        with open(filename, 'rb') as video_file:
          await query.message.reply_video(
              video=video_file, reply_markup=get_ceo_button()
          )
      try:
        await query.message.delete()
      except Exception:
        pass
    else:
      await query.edit_message_text(
          'Error: Could not download the media. Please check the link or try another format.',
          reply_markup=get_ceo_button(),
      )

  except Exception as e:
    try:
      await query.edit_message_text(
          f'Error: {str(e)}', reply_markup=get_ceo_button()
      )
    except Exception:
      pass

  finally:
    if filename and os.path.exists(filename):
      try:
        os.remove(filename)
      except Exception:
        pass

def check_internet():
  try:
    requests.get('https://www.google.com', timeout=5)
    return True
  except (requests.ConnectionError, requests.Timeout):
    return False

if __name__ == '__main__':
  if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

  print('ഇന്റർനെറ്റ് കണക്ഷനായി കാത്തിരിക്കുന്നു...')
  while not check_internet():
    time.sleep(5)

  print('ഇന്റർനെറ്റ് കണക്ട ആയി! ബോട്ട് സ്റ്റാർട്ട് ചെയ്യുന്നു...')

  request = HTTPXRequest(connect_timeout=120.0, read_timeout=120.0)
  app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

  app.add_handler(CommandHandler('start', start))
  app.add_handler(CommandHandler('stats', stats_command))
  app.add_handler(CommandHandler('broadcast', broadcast_command))
  app.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
  )
  app.add_handler(CallbackQueryHandler(button_click))
 
  app.run_polling()
