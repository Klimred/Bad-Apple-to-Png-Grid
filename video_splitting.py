import cv2


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
