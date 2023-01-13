import urllib.request
import os
import sys
import moviepy.editor as mpe
from pytube import YouTube

class YoutubeDownloader:
    pbar = None
    downloaded = 0
    filesize = 0
    video_url = ""
    video_key = ""
    pwd = os.getcwd()
    result_folder = ""
    
    def __init__(self, url):
        self.video_url = url
        # check if video url is valid
        # if video url not starts with "https://www.youtube.com/watch?v=" or "https://youtu.be/"
        if not (self.video_url.startswith("https://www.youtube.com/watch?v=") or self.video_url.startswith("https://youtu.be/")):
            # if shortend url
            if self.video_url.startswith("https://youtu.be/"):
                self.video_url = "https://www.youtube.com/watch?v=" + self.video_url.split("be/")[1]
            # if url contains "shorts/"
            elif "shorts/" in self.video_url and ("youtube.com" in self.video_url or "youtu.be" in self.video_url):
                self.video_url = "https://www.youtube.com/watch?v=" + self.video_url.split("shorts/")[1]
            else:
                print("> Invalid video url")
                sys.exit(1)
        # if there is unnecessary parameters in url
        if "&" in self.video_url:
            self.video_url = self.video_url.split("&")[0]
        if "t=" in self.video_url:
            self.video_url = self.video_url.split("t=")[0]
        if "list=" in self.video_url:
            self.video_url = self.video_url.split("list=")[0]
        if "index=" in self.video_url:
            self.video_url = self.video_url.split("index=")[0]
        if "feature=" in self.video_url:
            self.video_url = self.video_url.split("feature=")[0]
        # get video key
        self.video_key = self.video_url.split("v=")[1]
        if "?" in self.video_key:
            self.video_key = self.video_key.split("?")[0]
        self.result_folder = os.path.join(self.pwd, "results")
        # check if result folder exists
        if not os.path.exists(self.result_folder):
            os.mkdir(self.result_folder)

    def download_video(self):
        video_url = self.video_url
        video_key = self.video_key
        result_folder = self.result_folder

        # check if file already exists
        if os.path.exists(os.path.join(result_folder, video_key, video_key + ".mp4")):
            print("> Video already exists, skipping download...")
            return
        youtube = YouTube(video_url)
        mp4_file = youtube.streams.filter(adaptive=True, file_extension="mp4").order_by("resolution").desc().first()
        # get filesize of video
        global filesize
        filesize = mp4_file.filesize
        print("> Downloading video...")
        mp4_file.download(os.path.join(result_folder, video_key), filename=video_key+".mp4")
        print("\n> Downloaded video to result as \"" + video_key + ".mp4\"")

    def download_audio(self):
        video_url = self.video_url
        video_key = self.video_key
        result_folder = self.result_folder

        if os.path.exists(os.path.join(result_folder, video_key, video_key + ".mp3")):
            print("> Audio already exists, skipping download...")
            return
        youtube = YouTube(video_url)
        mp3_file = youtube.streams.filter(adaptive=True, only_audio=True).first()
        # get filesize of audio
        global filesize
        filesize = mp3_file.filesize
        print("> Downloading audio...")
        mp3_file.download(os.path.join(result_folder, video_key), filename=video_key+".mp3")
        print("\n> Downloaded audio to result as \"" + video_key + ".mp3\"")

    def combine_video_with_audio(self):
        video_key = self.video_key
        result_folder = self.result_folder
        # check if file already exists
        if os.path.exists(os.path.join(result_folder, video_key, video_key + "_combined.mp4")):
            print("> Combined video already exists, skipping combine...")
            return
        mp4_file = video_key + ".mp4"
        mp3_file = video_key + ".mp3"

        video = mpe.VideoFileClip(os.path.join(result_folder, video_key, mp4_file))
        audio = mpe.AudioFileClip(os.path.join(result_folder, video_key, mp3_file))

        # remove audio from video
        video = video.set_audio(None)
        
        # combine video and audio
        video.audio = audio
        video.write_videofile(os.path.join(result_folder, video_key, video_key + "_combined.mp4"))
        # remove original video and audio
        os.remove(os.path.join(result_folder, video_key, mp4_file))
        os.remove(os.path.join(result_folder, video_key, mp3_file))
        # rename combined video
        os.rename(os.path.join(result_folder, video_key, video_key + "_combined.mp4"), os.path.join(result_folder, video_key, video_key + ".mp4"))
        print("> Combined video and audio as \"" + video_key + ".mp4\"")

    def download_thumbnail(self):
        video_key = self.video_key
        result_folder = self.result_folder
        # check if file already exists
        if os.path.exists(os.path.join(result_folder, video_key, video_key + ".jpg")):
            print("> Thumbnail already exists, skipping download...")
            return
        # get the url of thumbnail as highest quality
        url = "https://img.youtube.com/vi/" + video_key + "/maxresdefault.jpg"
        image = urllib.request.urlopen(url)
        print("> Downloading image...\n")
        with open(os.path.join(result_folder, video_key, video_key + ".jpg"), "wb") as f:
            f.write(image.read())
        print("> Downloaded image as \"" + video_key + ".jpg\"")