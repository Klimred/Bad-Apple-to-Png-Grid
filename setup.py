import cv2
from pytube import YouTube
from moviepy.editor import VideoFileClip


def download_video_and_audio():
    bad_apple = YouTube("https://www.youtube.com/watch?v=FtutLA63Cp8")
    video_stream = bad_apple.streams.get_highest_resolution()
    video_stream.download("./Video with frames/", filename="Bad Apple.mp4")

    print("Video downloaded")

    audio_clip = VideoFileClip("C:/Users/fedor/PycharmProjects/Bad apple/Video with frames/Bad Apple.mp4").audio
    audio_clip.write_audiofile("C:/Users/fedor/PycharmProjects/Bad apple/Video with frames/audio.mp3")


def split_video():
    capture = cv2.VideoCapture('C:/Users/fedor/PycharmProjects/Bad apple/Video with frames/Bad Apple.mp4')
    frame_nr = 0

    while True:
        success, frame = capture.read()
        if success:
            cv2.imwrite(f'C:/Users/fedor/PycharmProjects/Bad apple/Video with frames/Frames/frame_{frame_nr}.jpg',
                        frame)
        else:
            break
        frame_nr += 1
    capture.release()
    print("i am done")


def setup():
    download_video_and_audio()
    split_video()
