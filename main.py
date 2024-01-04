import os
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip

from video_splitting import *


# define grid size and the resolution of the end video. I choose 1440*1080 as it is the biggest resolution that I
# can display in 4:3 on my 1920*1080 screen
grid = (48, 36)
canvas_size = (1440, 1080)
# sets a maximum size for the images, so that only one image doesn't take up the whole screen
maximum_size = int(grid[1]/4)

# sets the size of the smallest possible picture, depending on grid size and canvas size
image_size = int(canvas_size[0] / grid[0])

# open the two images to be used for the video
pattern1 = Image.open("./images/pattern 1.png")
pattern2 = Image.open("./images/pattern 2.png")


# a function that receives a frame from Bad Apple and return an array that contains the information whether the dominant
# color of the grid is white or black  1 for w and 0 for b. also has sets the second element in the 3rd dimension to 1
# that is required later
def get_dominant_color(image):
    # Open the image
    img = Image.open(image)

    # Resize the image to fit the grid
    img = img.resize(grid)

    # Convert the image to a NumPy array where [y,x,rgb]
    img_array = np.array(img)

    # transpose to [x,y,rgb]
    img_array = np.transpose(img_array, (1, 0, 2))

    dominant_colors = np.empty((grid[0], grid[1], 2))
    average_colors = np.empty(grid)
    for i in range(grid[0]):
        for j in range(grid[1]):
            average_colors[i, j] = np.mean(img_array[i, j])
            if average_colors[i, j] > 128:
                dominant_colors[i, j, 0] = 1
            else:
                dominant_colors[i, j, 0] = 0
            dominant_colors[i, j, 1] = 1
    return dominant_colors


# from the make_frame function, where it is called, it gets a position for x and y and a copy of dominant_colors
# the way it works is as follows: starting from size 1 it checks whether the grids of the next biggest square are all
# the same color and if dominant_colors[posY,posY, 1] is one, otherwise it would mean, this grid has already been drawn
# over. Grids checked in the last iteration of the while loop are not checked again
def find_max_size(i, j, dominant_colors):
    this_pixel = dominant_colors[i, j, 0]
    size = 1

    while size + i < dominant_colors.shape[0] and size + j < dominant_colors.shape[1] and size < maximum_size:
        # Create slices for the horizontal and vertical regions to check
        horizontal_slice = dominant_colors[i:i + size, j + size]
        vertical_slice = dominant_colors[i + size, j:j + size]

        # Check if all values in the horizontal slice are equal to this_pixel
        if not np.all(horizontal_slice[:, 0] == this_pixel):
            break

        # Check if all values in the vertical slice are equal to this_pixel
        if not np.all(vertical_slice[:, 0] == this_pixel):
            break

        # Check if any pixel in the slices has already been painted over
        if np.any(horizontal_slice[:, 1] == 0) or np.any(vertical_slice[:, 1] == 0):
            break

        size += 1

    return size


def make_frame(n):
    image_path = f"./Video with frames/Frames/frame_{n}.jpg"

    dominant_colors = get_dominant_color(image_path)

    print("doing image: " + str(n))
    canvas = Image.new("RGB", canvas_size, "white")

    for i in range(grid[0]):
        for j in range(grid[1]):
            if dominant_colors[i, j, 1] == 1:
                size_factor = find_max_size(i, j, dominant_colors)
                # make so that painted grids can't be painted over again
                for k in range(size_factor):
                    for l in range(size_factor):
                        dominant_colors[i + k, j + l, 1] = 0
                actual_image_size = image_size * size_factor
                if dominant_colors[i, j, 0] == 1:
                    canvas.paste(pattern1.resize((actual_image_size, actual_image_size)),
                                 (image_size * i, image_size * j))
                else:
                    canvas.paste(pattern2.resize((actual_image_size, actual_image_size)),
                                 (image_size * i, image_size * j))
    canvas.save(
        f"./out/done_frames/frame_"
        f"{str(n).zfill(4)}.jpg")
    # plt.imshow(dominant_colors.transpose(1, 0, 2)[:, :, 0], cmap="gray")
    # plt.show()


def make_frames_parallel():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(make_frame, n) for n in range(6572)]
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)


def make_frames_one_after_another():
    for n in range(100):
        make_frame(n)


def make_video():
    out = cv2.VideoWriter('./out/soundless Bad Apple.mp4',
                          cv2.VideoWriter_fourcc(*'mp4v'), 30, (1440, 1080))

    for n in range(6572):
        filename = f"./out/done_frames/frame_"\
                   f"{str(n).zfill(4)}.png"
        img = cv2.imread(filename)
        out.write(img)
        print("writing frame: " + str(n))

    out.release()
    print("video done, starting audio")

    video_clip = VideoFileClip("./out/soundless Bad Apple.mp4")
    audio_clip = AudioFileClip("./out/audio.mp3")
    video_clip = video_clip.set_audio(audio_clip)

    video_clip.write_videofile("./out/Bad Apple.mp4", codec="libx264",
                               audio_codec="aac")


# needs to be like this for multiprocessing to work
if __name__ == "__main__":
    user_input = input("frames or video or all?:\n> ")

    if user_input in ["frames", "f"]:
        make_frames_parallel()
    elif user_input in ["video", "v"]:
        make_video()
    elif user_input in ["all"]:
        make_frames_parallel()
        make_video()
