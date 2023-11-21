import gradio as gr
import os
import whisper
from moviepy.editor import VideoFileClip
import openai
import json
import requests
import io
import codecs 


# Reading api keys from file
api_key = open('api_key.txt', 'r').read().strip('\n')
api_key
openai.api_key = api_key
conversation_history = []


def video_identity(video):
    return video


def text_to_audio(text_input, file_name):
    """This function uses the tts-1 model from OPENAI to convert input str to audio and 
    save under test,

    Args:
        text_input (str): _description_
    """
    response = requests.post(
    'https://api.openai.com/v1/audio/speech',
    headers={
        "Authorization":f"Bearer {api_key}"
    },
    json = {
        'model':'tts-1',
        'input': text_input, #todo: change this to a variable
        'voice':'nova', #check https://platform.openai.com/docs/guides/text-to-speech for voice samples
    },
    )
    if response.status_code != 200:
        print("Request failed !!")
        print(response.status_code)

    audio_byte_io = io.BytesIO()
    for chunk in response.iter_content(chunk_size=1024*1024):
        audio_byte_io.write(chunk)
        
    audio_byte_io.seek(0)

    with open(f'{file_name}.wav', 'wb') as tmpFile:
        for chunk in response.iter_content(chunk_size=1024*1024):
            tmpFile.write(chunk)
        audio_file_name = tmpFile.name
    return audio_file_name, audio_byte_io



#Extract the audio from video
def extract_video_audio_moviepy(video_file, suffix="wav"):
    """Extract the audio from video ans save to .wav file 

    Args:
        video_file (str): video file path
        suffix (str, optional): _description_. Defaults to "wav".
    """
    filename, ext = os.path.splitext(video_file)
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{suffix}")


# Use Whisper, audio to text
def whisper_to_text(audio_file_path):
    """Use the Whisper model from 

    Args:
        audio_file_path (str): Convert audio to text

    Returns:
        _type_: _description_
    """
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


def main():

    # prompt msg for the chat GPT
    prompt_msg = 'modify my input text in the same language, but without changing the meaning and keep the similar length. If you understand, say OK.'
    prompt = [{"role": "user", "content": prompt_msg},
            {"role": "assistant", "content": f"OK"}]
    
    # todo: get a sample video file, replace line 124-127
    # todo: UI
    video_file = ""
    
    with codecs.open('movie_descip.json', 'r', 'utf-8') as file:
        data = json.load(file)
    text = data['实验']

    
    file_name, _ = text_to_audio(text, 'orgin_text')
    text_modified = build_chat(text, prompt, role='user')
    # todo: save the text and modified text. Check the different
    temp_dic = {}
    temp_dic['origin'] = text
    temp_dic['modify'] = text_modified
    with codecs.open('temp_dic.json', 'w', encoding='utf-8') as f:
        json.dump(temp_dic, f, ensure_ascii=False)
    file_name, io_stream = text_to_audio(text_modified, 'text_modified')


    
if __name__ == "__main__":
    # steps 1. upload the video to gradio ui. 
    # 2. Extract the audio from the video. 
    # 3. Use whisper to generate text from audio. 
    # 4. Modify the text using chat gpt. 
    # 5. Text from 4, to audio
    # 6. Extract video
    # 7. stitch the 6, 5 a
    # 8. ouput the final video
    
    main()
    print('DOne')