import io
import discord
import asyncio
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
import threading
from urllib.request import urlopen
from PIL import Image, ImageTk

# Discordクライアントの設定
client = discord.Client()

# グローバル変数
voice_client = None
current_song = None
queue = []

# Discordに接続する関数
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# ボイスチャンネルに参加する関数
async def join_voice_channel(channel_id):
    global voice_client
    channel = client.get_channel(int(channel_id))
    voice_client = await channel.connect()

# 音楽を再生する関数
async def play_music(file_path):
    global current_song, voice_client
    current_song = file_path
    if voice_client and voice_client.is_connected():
        voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(), client.loop))

# 次の曲を再生する関数
async def play_next():
    global current_song, queue
    if queue:
        next_song = queue.pop(0)
        await play_music(next_song)

# 音楽をスキップする関数
async def skip_music():
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await play_next()

# ボイスチャンネルから退出する関数
async def leave_voice_channel():
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None

# GUIの設定
def create_gui():
    root = tk.Tk()
    root.title("Discord Music Bot")

    # 背景画像の設定
    url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiJ6Gr4w7OR42V3EL_9-Ckvk0ZIUyywBa6tmBk7v1PFT2KpWEiuudFgelae7ZU7Va5jTbSCbn7A7MQLni4szwrQQYPLAd1ntWWDW0If5BUmcyIBaZw9houaK-aiF6VAbBtXLqd_bwMRF2vE/s1600/lain1.jpg"
    image_bytes = urlopen(url).read()
    image = Image.open(io.BytesIO(image_bytes))
    background_image = ImageTk.PhotoImage(image)

    background_label = tk.Label(root, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    channel_label = tk.Label(root, text="Voice Channel ID:", bg="white")
    channel_label.pack()

    channel_entry = tk.Entry(root)
    channel_entry.pack()

    join_button = tk.Button(root, text="Join", command=lambda: asyncio.run_coroutine_threadsafe(join_voice_channel(channel_entry.get()), client.loop))
    join_button.pack()

    file_path = tk.StringVar()

    def open_file():
        filepath = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        file_path.set(filepath)

    file_button = tk.Button(root, text="Open File", command=open_file)
    file_button.pack()

    play_button = tk.Button(root, text="Play", command=lambda: asyncio.run_coroutine_threadsafe(play_music(file_path.get()), client.loop))
    play_button.pack()

    skip_button = tk.Button(root, text="Skip", command=lambda: asyncio.run_coroutine_threadsafe(skip_music(), client.loop))
    skip_button.pack()

    leave_button = tk.Button(root, text="Leave", command=lambda: asyncio.run_coroutine_threadsafe(leave_voice_channel(), client.loop))
    leave_button.pack()

    root.mainloop()

# Discord クライアントを実行する関数
async def run_discord_client():
    await client.start('')

# メイン関数
async def main():
    # Discord クライアントを別スレッドで実行
    discord_thread = threading.Thread(target=lambda: asyncio.run(run_discord_client()))
    discord_thread.start()

    # GUIを実行
    create_gui()

if __name__ == "__main__":
    asyncio.run(main())
