import cv2
import numpy as np
import os
import sys
import glob
from tqdm.auto import tqdm
import traceback
import math
import argparse
import shutil

cleaned_frame_folder = []


def framing(input_path,  duration_intv_sec=10, max_row_width=4, min_partition=8):
    input_location, input_filename = os.path.split(input_path)
    # print(input_location, input_filename)
    frame_folder = os.path.join(input_location, 'frame')
    global cleaned_frame_folder
    if not os.path.exists(frame_folder):
        os.mkdir(frame_folder)
    elif frame_folder not in cleaned_frame_folder:
        shutil.rmtree(frame_folder)
        os.mkdir(frame_folder)
        cleaned_frame_folder.append(frame_folder)
    imgs = []
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_len = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_shape = None
    duration = frame_len // fps
    partitions = max(int(duration / duration_intv_sec), min_partition)
    interval_in_frame = int(frame_len / partitions)

    # print(duration, duration_intv_sec)
    # print(frame_len, interval_in_frame)

    try:
        start = 0
        while start < frame_len:
            end = start + interval_in_frame if start + \
                interval_in_frame < frame_len else frame_len
            if frame_len - end < interval_in_frame / 2:
                end = frame_len
            current_frame = int((start + end) / 2)
            # print((start, end), end - start, current_frame)
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            cap.grab()
            _, frame_image = cap.retrieve()
            if frame_shape is None:
                frame_shape = frame_image.shape
            if frame_image is not None:
                imgs.append(frame_image)
            start = end
    except Exception as e:
        print(e)
    finally:
        cap.release()

    imgs = np.array(imgs)
    row_concats = []

    s = 0
    for row in range(math.ceil(imgs.shape[0] / max_row_width)):
        e = s + max_row_width if s + \
            max_row_width < imgs.shape[0] else imgs.shape[0]
        curr = imgs[s:e, :, :, :]
        if max_row_width - (e - s) > 0:
            padding = np.zeros(
                shape=(max_row_width - (e - s), *curr.shape[1:]), dtype=np.uint8)
            curr = np.vstack((curr, padding))

        row_concats.append(cv2.hconcat(curr))
        s = e

    grid_img = cv2.vconcat(row_concats)
    frame_file_name = f"{input_filename}.jpg"
    cv2.imwrite(os.path.join(frame_folder, frame_file_name), grid_img)


def FrameCapture(input_path,  duration_intv_sec=600, max_row_width=3, min_partition=8):
    accepted_video_extension = ['.mp4', '.mkv', '.avi', '.ts',
                                '.wmv', '.webm', '.mpeg', 'mpe', 'mpv', '.ogg', '.m4p', '.m4v']
    all_video_extension = [*accepted_video_extension, '.rmvb']
    input_path = os.path.abspath(input_path)
    if os.path.isfile(input_path):
        all_files = [input_path]
    else:
        all_files = []
        for ext in all_video_extension:
            files = []
            files.extend(
                glob.glob(input_path + f'/**/*{ext}', recursive=True))
            files.extend(
                glob.glob(input_path + f'/**/*{ext.upper()}', recursive=True))
            if len(files) > 0:
                if ext in accepted_video_extension:
                    all_files.extend(files)
                else:
                    print(f'Not supported: {files}')

    if len(all_files) > 0:
        for file in tqdm(all_files,  bar_format='{l_bar}{bar:30}{r_bar}{bar:-10b}'):
            try:
                framing(file, duration_intv_sec, max_row_width, min_partition)
            except Exception as e:
                traceback.print_exc()


def run():
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_help()
            sys.exit(2)

    sys.path.append(os.getcwd())

    parser = MyParser()

    parser.add_argument(
        "-i", "--input-path", type=str,
        help="The path of input files or the directory that keeps the inputs.", required=True)

    parser.add_argument(
        "-d", "--duration-interval-second", type=int,
        help="The interval that partition the video.", default=600)

    parser.add_argument(
        "-rw", "--max-row-width", type=int,
        help="The width of each row.", default=3)

    parser.add_argument(
        "-mp", "--min-partition", type=int,
        help="Miniumn partition of the grids.", default=8)

    args = parser.parse_args()

    input_path = args.input_path
    duration_intv_sec = args.duration_interval_second
    max_row_width = args.max_row_width
    min_partition = args.min_partition
    FrameCapture(input_path, duration_intv_sec=duration_intv_sec,
                 max_row_width=max_row_width, min_partition=min_partition)


if __name__ == '__main__':
    run()
