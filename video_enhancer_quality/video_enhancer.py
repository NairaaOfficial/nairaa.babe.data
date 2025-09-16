import os
import cv2
import numpy as np
import logging
import shutil
from moviepy import *
from BSRGAN.bsrgan_quality_gpu import enhance_frame_bsrgan

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Video Related Parameters
video_folder_path = 'private/videos'
enhanced_video_folder_path = 'public/videos'
# Text/csv related parameters
counter_file = 'counter.txt'

def get_reel_number():
    """Read the current counter value from the file, or initialize it."""
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as file:
            return int(file.read())
    return 0

def get_input_video(reel_number):
    ## Loop over the video folder and get the input video path
    for filename in os.listdir(video_folder_path):
        if filename.startswith("Video") and filename.endswith(f"_{reel_number}.mp4"):
            input_video_path = os.path.join(video_folder_path, filename) 
            logging.info(f'Processing {filename} as video_{reel_number}')

    return input_video_path

def detect_video_area(frame):
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    return (0, 0, frame_width, frame_height)

# Function to enhance the sharpness of the image
def sharpen_image(frame):
    logging.debug("Applying sharpening filter.")
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(frame, -1, kernel)

# Function to adjust the contrast of the image
def adjust_contrast(frame, alpha=1.2, beta=0):
    logging.debug("Adjusting contrast and brightness.")
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

# Function to enhance color
def enhance_color(frame):
    logging.debug("Enhancing color by converting to HSV and adjusting saturation.")
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = cv2.addWeighted(hsv[:, :, 1], 1.3, hsv[:, :, 1], 0, 0)  # Increase saturation by 30%
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
def clean_up_files(*files):
    """Delete intermediate video files after the final video is created."""
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        else:
            logging.warning(f"File not found, skipping deletion: {file_path}")
            
def process_video(input_video_path, reel_number):
    cropped_video_path = os.path.join(enhanced_video_folder_path, f'cropped_video_no_audio_{reel_number}.mp4')
    cropped_video_with_audio_path = os.path.join(enhanced_video_folder_path, f'cropped_video_{reel_number}.mp4')
    enhanced_output_path = os.path.join(enhanced_video_folder_path, f'Video_{reel_number}.mp4')

    def add_audio_to_video(input_path, output_path):
        with VideoFileClip(input_video_path) as original_clip, VideoFileClip(input_path) as cropped_clip:
            final_clip = cropped_clip.with_audio(original_clip.audio)
            fps = original_clip.fps  # Detect the FPS of the enhanced video
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                bitrate="5000k",
                audio_bitrate="256k",
                fps=fps,  # Use detected FPS
                ffmpeg_params=[
                    "-crf", "18",
                    "-preset", "veryslow",
                    "-pix_fmt", "yuv420p",
                    "-g", str(int(fps * 2)),       # GOP: 2 seconds
                    "-sc_threshold", "0",
                    "-movflags", "+faststart"
                ]
            )
    
    def add_audio_to_video_2k(input_path, output_path):
        with VideoFileClip(input_video_path) as original_clip, VideoFileClip(input_path) as cropped_clip:
            fps = original_clip.fps
            final_clip = cropped_clip.with_audio(original_clip.audio)

            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                audio_bitrate="256k",
                bitrate="10M",  # Constrained high bitrate for Instagram compatibility
                fps=fps,
                ffmpeg_params=[
                    "-crf", "14",  # Near visually lossless, but not overly large
                    "-preset", "veryslow",  # Balanced compression speed vs. quality
                    "-pix_fmt", "yuv420p",  # Required by Instagram
                    "-g", str(int(fps * 2)),  # GOP length = 2 seconds
                    "-sc_threshold", "0",     # Ensures consistent keyframes
                    "-movflags", "+faststart",  # Enables progressive playback on Instagram
                    "-vf", "scale=1440:2560:force_original_aspect_ratio=decrease,pad=1440:2560:(ow-iw)/2:(oh-ih)/2"
                ]
            )

    def enhance_video():
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {input_video_path}")
            return
        video_area = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if video_area is None:
                video_area = detect_video_area(frame)
                if video_area:
                    x, y, w, h = video_area
                    detected_x, detected_y, detected_w, detected_h = x, y, w, h
                    logging.info(f"Detected video area: {video_area}")
                    
        cap.release()
        
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {input_video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        x, y, w, h = detected_x, detected_y, detected_w, detected_h
        out = cv2.VideoWriter(cropped_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames to process: {total_frames}")
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Crop the frame using the detected area
            enhanced_frame = frame[y:y + h, x:x + w]
            # Apply enhancements: sharpening, contrast, and color enhancement
            enhanced_frame = sharpen_image(enhanced_frame)
            enhanced_frame = adjust_contrast(enhanced_frame)
            enhanced_frame = enhance_color(enhanced_frame)
            enhanced_frame = enhance_frame_bsrgan(enhanced_frame, False)
            print(f"Processing frame {count}")
            # Write the enhanced, cropped frame
            out.write(enhanced_frame)
            count += 1
            print(f"Processing frame {count}/{total_frames}")

        cap.release()
        if out:
            out.release()
            add_audio_to_video_2k(cropped_video_path, cropped_video_with_audio_path)
    
    # Step 1 - Crop the Video Out
    enhance_video()
    # Step 5 - Clean up some files
    shutil.copy(cropped_video_with_audio_path, enhanced_output_path)
    clean_up_files(cropped_video_path, cropped_video_with_audio_path)

def main():
    # Getting the reel number from counter file.
    reel_number = get_reel_number()
    print(f"Reel Number : {reel_number}")
    
    # Get the input video from video folder.
    input_video_path = get_input_video(reel_number)
    
    # Process the input video
    process_video(input_video_path, reel_number)

if __name__ == "__main__":
    main()
