from moviepy.editor import VideoFileClip, AudioFileClip

def add_audio_to_video(video_path_with_audio, video_path_without_audio, output_path):
    # Load the video with audio and extract audio
    video_with_audio = VideoFileClip(video_path_with_audio)
    audio = video_with_audio.audio

    # Load the video without audio
    video_without_audio = VideoFileClip(video_path_without_audio)

    # Set the audio of the second video to the extracted audio
    video_with_new_audio = video_without_audio.set_audio(audio)

    # Write the result to the output file
    video_with_new_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Paths to your videos
video_path_with_audio = 'data/input/flask_babel.mp4'
video_path_without_audio = 'data/input/without_sound_babel.mp4'
output_path = 'data/output/output_video.mp4'

add_audio_to_video(video_path_with_audio, video_path_without_audio, output_path)
 