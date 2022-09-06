import os
import glob
import time
import ffmpy as ff
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import any_of
from gtts import gTTS

import undetected_chromedriver as uc

from moviepy.editor import *

def initBot():
    #### INIT FOR DRIVER ###
    ## EDIT USERDATA_PATH AND PROFILE IF CUSTOM CHROME PROFILE

    
    USERDATA_PATH = r"C:\Users\dillo\Desktop\2022\Twitch Downloaded\chromedriver\UserData"
    PROFILE = 'Profile 1'

    ## UNDETECTED CHROMEDRIVER ##
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument(f'--user-data-dir={USERDATA_PATH}')
    options.add_argument(f'--profile-directory={PROFILE}')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-popup-blocking')
    options.add_argument("--force-device-scale-factor=2")
    options.add_argument("--high-dpi-support=2")
    # options.add_argument("--start-maximized")
    bot = webdriver.Chrome(options=options, executable_path=r"D:\chromedriver\chromedriver_win32\chromedriver.exe")
    

    return bot

def tts(text, name):
    tts = gTTS(text, slow=False)
    tts.save(r'C:\Users\dillo\Desktop\2022\reddit to tiktok\working\gtts-' + name + ".mp3")

def speedup(file, output):
    body_speed_up = ff.FFmpeg(executable=r"C:\Users\dillo\Desktop\2022\reddit to tiktok\ffmpeg\bin\ffmpeg.exe",inputs={file : None}, outputs={output: ["-filter:a", "atempo=1.2"]})
    body_speed_up.run()

def clearFolder(path):
    for f in glob.glob(os.path.join(path, "*")):
        print(f)
        os.remove(f)

if __name__ == '__main__':
    URL = "https://www.reddit.com/r/MaliciousCompliance/comments/x65xdv/smiling_all_the_way_home/"

    bot = initBot()
    time.sleep(.5)
    bot.get(URL)
    
    counter = 0

# find elements
    post = bot.find_element(By.XPATH, "//div[@data-test-id='post-content']")
    title = bot.find_element(By.XPATH, "//div[@data-test-id='post-content']/descendant::h1")
    pgs = bot.find_elements(By.XPATH, "//div[@data-test-id='post-content']/descendant::p")

#tts processes and screenshots
    processes = []

    p1 = multiprocessing.Process(target=tts(title.text, 'title'))
    p1.start()
    processes.append(p1)

    title.screenshot("working/title.png")

    count = 0
    for pg in pgs:
        temp = multiprocessing.Process(target=tts(pg.text, 'body' + str(count)))
        temp.start()
        bot.execute_script('arguments[0].scrollIntoView()', pg)
        pg.screenshot(f"working/body{count}.png")
        count+=1
        processes.append(temp)

    bot.close()

    for p in processes:
        p.join()

# EDITING
    #speed up tts

    p2 = multiprocessing.Process(target=speedup(f"working/gtts-title.mp3", f"working/tts-title.mp3"))
    p2.start()
    processes.append(p2)

    processes = []
    for i in range(0,count):
        p = multiprocessing.Process(target=speedup(f"working/gtts-body{i}.mp3", f"working/tts-body{i}.mp3"))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    # title tts

    tts_title = (AudioFileClip("working/tts-title.mp3")
                        .set_start(0))

    #body tts amd images

    prev = tts_title.duration+1

    body_tts_list = []
    body_clip_list = []

    for i in range(0,count):
        
        tts_body = (AudioFileClip(f"working/tts-body{i}.mp3")
                            .set_start(prev))
        

        body_clip = (ImageClip(f"working/body{i}.png")
                    .set_duration(tts_body.duration)
                    .set_pos("center", "top")
                    .set_start(prev)
                    .resize(2.25))

        prev += tts_body.duration

        body_clip_list.append(body_clip)
        body_tts_list.append(tts_body)

    title_clip = (ImageClip("working/title.png")
                    .set_duration(tts_title.duration)
                    .set_pos("center", "top")
                    .set_start(0)
                    .resize(2))

    clip = VideoFileClip("rl background.mp4").set_duration(tts_title.duration + prev + 3)

    videos = [clip, title_clip] + body_clip_list
    final_video = CompositeVideoClip(videos)
    
    audios = [tts_title] + body_tts_list
    final_audio = CompositeAudioClip(audios)
    final_video.audio = final_audio

    final_video.write_videofile("final.mp4", threads=8, fps=24, audio_codec='aac')
        
    clearFolder("working")