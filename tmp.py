import os
import subprocess
import argparse


def merge_audio_video(video_file, audio_file, output_file):
    """
    Uses ffmpeg to merge the video and audio file into a WebM file.
    Re-encodes video to VP9 and audio to Opus.
    """
    cmd = [
        "ffmpeg",
        "-y",                # Overwrite output if it exists.
        "-i", video_file,    # Input video file.
        "-i", audio_file,    # Input audio file.
        "-c:v", "libvpx-vp9",  # Re-encode video using VP9.
        "-b:v", "2M",          # Set a video bitrate; adjust as needed.
        "-c:a", "libopus",     # Re-encode audio using Opus.
        "-b:a", "128k",        # Set an audio bitrate.
        "-map", "0:v:0",       # Use video from the first input.
        "-map", "1:a:0",       # Use audio from the second input.
        output_file
    ]
    subprocess.run(cmd, check=True)


def main(inp_aud_dir, inp_vid_dir, out_vid_dir):
    """
    Walks through each subdirectory in the input audio directory.
    For each .wav file, finds the corresponding .mp4 file in the video
    directory (assuming same base file name), and merges them.
    The output WebM video is stored in out_vid_dir preserving the subdirectory structure.
    """
    # Iterate over subdirectories in the audio directory.
    for subfolder in os.listdir(inp_aud_dir):
        audio_subfolder = os.path.join(inp_aud_dir, subfolder)
        if not os.path.isdir(audio_subfolder):
            continue

        video_subfolder = os.path.join(inp_vid_dir, subfolder)
        output_subfolder = os.path.join(out_vid_dir, subfolder)
        os.makedirs(output_subfolder, exist_ok=True)

        if not os.path.exists(video_subfolder):
            print(f"Warning: Video folder '{video_subfolder}' not found. Skipping folder '{subfolder}'.")
            continue

        # Process each WAV file in this subfolder.
        for file in os.listdir(audio_subfolder):
            if file.lower().endswith(".wav"):
                base_name = os.path.splitext(file)[0]  # e.g., "00007"
                audio_file = os.path.join(audio_subfolder, file)
                video_file = os.path.join(video_subfolder, base_name + ".mp4")

                if not os.path.exists(video_file):
                    print(f"Warning: Corresponding video file '{video_file}' not found for audio '{audio_file}'. Skipping file.")
                    continue

                # Create the output filename with .webm extension.
                output_file = os.path.join(output_subfolder, base_name + ".webm")
                print(f"Merging audio '{audio_file}' with video '{video_file}' into '{output_file}'.")

                try:
                    merge_audio_video(video_file, audio_file, output_file)
                except subprocess.CalledProcessError as e:
                    print(f"Error during merging: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge audio from WAV files with corresponding video files and output as WebM using ffmpeg."
    )
    parser.add_argument("inp_aud_dir", help="Path to the input audio directory")
    parser.add_argument("inp_vid_dir", help="Path to the input video directory")
    parser.add_argument("out_vid_dir", help="Path to the output video directory")
    args = parser.parse_args()

    main(args.inp_aud_dir, args.inp_vid_dir, args.out_vid_dir)
