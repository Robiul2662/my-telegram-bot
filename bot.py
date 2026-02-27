import telebot
from telebot import types
from yt_dlp import YoutubeDL
import os

# আপনার দেওয়া টোকেনটি এখানে বসানো হয়েছে
API_TOKEN = '8220959784:AAFbfibRrWSNctMokpgUAzXUnEuIMoeEPA0'
bot = telebot.TeleBot(API_TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 হ্যালো! আমি আপনার ভিডিও ও অডিও ডাউনলোডার বট। যেকোনো লিংক পাঠান, আমি ডাউনলোড করে দেব।")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if "http" in message.text:
        user_data[message.chat.id] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎥 Video (MP4)", callback_data="v"),
                   types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="a"))
        bot.send_message(message.chat.id, "আপনি কী ডাউনলোড করতে চান?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "দয়া করে একটি সঠিক ভিডিও লিংক পাঠান।")

@bot.callback_query_handler(func=lambda call: True)
def dl(call):
    url = user_data.get(call.message.chat.id)
    if not url: 
        bot.send_message(call.message.chat.id, "লিংকটি খুঁজে পাচ্ছি না। আবার লিংকটি পাঠান।")
        return
    
    bot.send_message(call.message.chat.id, "⏳ ডাউনলোড শুরু হচ্ছে, দয়া করে অপেক্ষা করুন...")
    
    ext = 'mp4' if call.data == 'v' else 'mp3'
    fname = f"file.{ext}"
    
    # yt-dlp options
    if call.data == 'v':
        opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': fname}
    else:
        opts = {'format': 'bestaudio/best', 'outtmpl': 'file', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
    
    try:
        with YoutubeDL(opts) as ydl: 
            ydl.download([url])
        
        with open(fname, 'rb') as f:
            if ext == 'mp4': 
                bot.send_video(call.message.chat.id, f)
            else: 
                bot.send_audio(call.message.chat.id, f)
        
        # ফাইলটি ডিলিট করে দেওয়া (সার্ভার পরিষ্কার রাখার জন্য)
        if os.path.exists(fname): os.remove(fname)
        if os.path.exists('file'): os.remove('file') # অডিওর জন্য
        
    except Exception as e:
        bot.send_message(call.message.chat.id, f"দুঃখিত, কোনো সমস্যার কারণে ডাউনলোড করা যাচ্ছে না। \nভুলটি হলো: {str(e)}")

bot.infinity_polling()
