import pyttsx3
import requests
import json
import whisper
import sounddevice as sd
import numpy as np

# Function to get predefined response from a text file
def get_predefined_response(question, file_path='responses.txt'):
    print("Checking for predefined response for:", question)
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    q, a = line.strip().split(':', 1)
                    if q.lower().strip() == question.lower().strip():
                        return a
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return None

# Function to get response from OpenAI Chatbot
def generate_chatbot_response(text):
    openai_api_key = 'Enter your Openai api key here'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are Ai ham operator Your name is Paul and callsign VE9VW. Respond to all input in 25 words or less. and say over the end of the response"},
            {"role": "user", "content": text}
        ]
    }    

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        data=json.dumps(data)
    )

    response_data = json.loads(response.text)
    if response.status_code == 200 and 'choices' in response_data and response_data['choices']:
        return response_data['choices'][0]['message']['content']
    else:
        print("Error or unexpected response structure:", response.status_code, response.text)
        return None

# Function to convert text to speech
def speak(text, rate=125):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)  # Set speech rate
    engine.say(text)
    engine.runAndWait()
   

# Function to record audio from microphone
def record_audio_from_mic(duration=5, sample_rate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio

# Function to recognize speech using Whisper
def recognize_speech_from_mic():
    model = whisper.load_model("base")
    audio_data = record_audio_from_mic()
    audio_np = np.array(audio_data).flatten()
    result = model.transcribe(audio_np)
    print("You said: " + result['text'])
    return result['text']

# Function to save text to a file
def save_text_to_file(text, file_path='chat_history.txt'):
    with open(file_path, 'a') as file:
        file.write(text + "\n")

# Main function to run the chatbot
def run_chatbot():
    print("Chatbot is ready to talk! Say 'stop' to end the conversation.")
    while True:
        input_text = recognize_speech_from_mic()

        if not input_text or input_text.lower() == 'stop':
            print("Exiting chatbot...")
            break

        save_text_to_file("HamOp: " + input_text)  # Save user input

        response_text = get_predefined_response(input_text)
        if not response_text:
            response_text = generate_chatbot_response(input_text)

        if response_text:
            print("Chatbot:", response_text)
            speak(response_text)
            save_text_to_file("Ve9vw-AI: " + response_text)  # Save chatbot response

run_chatbot()
