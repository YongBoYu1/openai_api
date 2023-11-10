import gradio as gr
import os
import whisper
from moviepy.editor import VideoFileClip

def video_identity(video):
    return video

#UI todo: audio to text.
demo = gr.Interface(video_identity, 
                    gr.Video(), 
                    "playable_video"
                    )


#Extract the audio from video
def convert_video_to_audio_moviepy(video_file, suffix="wav"):
    """Converts video to audio using MoviePy library
    that uses `ffmpeg` under the hood"""
    filename, ext = os.path.splitext(video_file)
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{suffix}")

# Use Whisper to load audio to text
def whisper_to_text(audio_file_path):
    model = whisper.load_model('small')
    result = model.transcribe(audio_file_path)
    return result['text']


    
if __name__ == "__main__":
    demo.launch()