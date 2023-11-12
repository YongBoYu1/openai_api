import gradio as gr
import os
import whisper
from moviepy.editor import VideoFileClip
import openai
import json

conversation_history = []
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

# Use Whisper, audio to text
def whisper_to_text(audio_file_path):
    model = whisper.load_model('small')
    result = model.transcribe(audio_file_path)
    return result['text']

# Modify text from chatgpt
def build_chat(input, prompt, role='user'):
    """This function takes the user input string, return the reply from the GPT model, and save the input 
    and reply to the conversation history

    Args:
        input (str): The user input str, a question, or a request.
        role (str, optional): _description_. Defaults to 'user'.

    Returns:
        str: The gpt reply content
    """
    global conversation_history 

    # Build intial prompt
    for msg in prompt:
        conversation_history.append(msg)

    conversation_history.append({"role": role, "content": input})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  #GPT Model
        messages = conversation_history
        )
    
    reply_str = completion['choices'][0]['message']['content']
    conversation_history.append({"role": 'assistant', "content": reply_str})
    return reply_str

    
if __name__ == "__main__":
    # steps 1. upload the video to gradio ui. 
    # 2. Extract the audio from the video. 
    # 3. Use whisper to generate text from audio. 
    # 4. Modify the text using chat gpt. 
    # 5. Text from 4, to audio
    # 6. Extract video
    # 7. stitch the 6, 5 a
    # 8. ouput
    demo.launch()