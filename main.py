import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import YoutubeDownloader as yd
import sys
import time

#global
# bot getting command from '#' prefix
bot = commands.Bot(command_prefix='#', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'> Login bot: {bot.user}')

@bot.event
async def catch_command(message):
    if message.author==bot.user:
        return
    if message.content.startswith('#'):
        await bot.process_commands(message)

@bot.command()
async def mp3(message, url):
    key, path = download(url)
    # send mp3 file
    print(f"> sending downloaded audio file \"{key}.mp3\" to the channel ...")
    await message.channel.send(file=discord.File(path))
    print(f"> sent downloaded audio file \"{key}.mp3\" to the channel")

def download(url)->str:
    # download youtube mp3 file
    downloader = yd.YoutubeDownloader(url)
    downloader.download_audio()
    path = os.path.join(downloader.result_folder, downloader.video_key, downloader.video_key + ".mp3")
    return downloader.video_key, path

@bot.command()
async def play(message, url):
    # play audio in voice channel
    author = message.author
    # check if author is in voice channel
    if author.voice is None:
        print(f"> author is not in voice channel")
        await message.channel.send("> author is not in voice channel")
        return
    voice_channel = author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    if voice_client:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
        else:
            print(f"> already connected to voice channel")
            await message.channel.send(f"> already connected to voice channel")
    else:
        voice_client = await voice_channel.connect()
    
    # if audio is already playing
    if voice_client.is_playing():
        print(f"> audio is already playing in voice channel {voice_channel.name}")
        await message.channel.send(f"> audio is already playing in voice channel {voice_channel.name}")
        return
    # play mp3 file on voice channel
    key, path = download(url)
    voice_client.play(FFmpegPCMAudio(path))
    print(f"> playing audio in voice channel {voice_channel.name}")
    await message.channel.send(f"> playing audio in voice channel {voice_channel.name}")

@bot.command()
async def kill(message):
    # disconnect from voice channel
    author = message.author
    voice_channel = author.voice.channel
    if voice_channel is None:
        print(f"> author is not in voice channel")
        await message.channel.send("> author is not in voice channel")
        return
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    await voice_client.disconnect()
    print(f"> disconnected from voice channel {voice_channel.name}")
    await message.channel.send(f"> disconnected from voice channel {voice_channel.name}")
    clean()

@bot.command()
async def stop(message, *args):
    if len(args) > 0:
        if args[0] == 'all':
            for vc in bot.voice_clients:
                await vc.disconnect()
            return
    # stop playing audio in voice channel
    author = message.author
    voice_channel = author.voice.channel
    if voice_channel is None:
        print(f"> author is not in voice channel")
        await message.channel.send("> author is not in voice channel")
        return
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    if voice_client.is_playing():
        voice_client.stop()
        print(f"> stopped playing audio in voice channel {voice_channel.name}")
        await message.channel.send(f"> stopped playing audio in voice channel {voice_channel.name}")
        # remove downloaded mp3 file
        clean()
    else:
        print(f"> no audio is playing in voice channel {voice_channel.name}")
        await message.channel.send(f"> no audio is playing in voice channel {voice_channel.name}")

def main(args):
    # if args is not empty
    if len(args) > 1:
        argparse = argparse.ArgumentParser()
        argparse.add_argument('-t', '--token', help='Discord bot token')
        args = argparse.parse_args()
        token = args.token
    else :
        pwd = os.getcwd()
        default_token = os.path.join(pwd, 'token.txt')
        with open(default_token, 'r') as f:
                token = f.read()
    # Run bot
    bot.run(token)

def clean(*args):
    pwd = os.getcwd()
    result_folder = os.path.join(pwd, 'results')
    if len(args) > 0:
        for key in args:
            # remove {key} folder within results folder
            path = os.path.join(result_folder, key)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    os.remove(os.path.join(path, file))
            os.rmdir(path)
    else:
        # remove downloaded folder
        for folder in os.listdir(result_folder):
            path = os.path.join(result_folder, folder)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    os.remove(os.path.join(path, file))
            os.rmdir(path)

if __name__ == "__main__":
    main(sys.argv)