import speech_recognition as sr
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk

import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import datetime
import wikipedia #pip install wikipedia
import webbrowser
import os
import smtplib
import pyjokes
import tkinter


# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Create a Tkinter window
window = tk.Tk()
window.title("Voice Assistant")

# Load the Siri-like bubble GIF frames
gif_frames = []
gif_image = Image.open("sirilike.gif")
try:
    while True:
        gif_frames.append(ImageTk.PhotoImage(gif_image))
        gif_image.seek(len(gif_frames))
except EOFError:
    pass

# Create a label for the bubble GIF
gif_label = tk.Label(window)
gif_label.pack(pady=20)


# Function to update the GIF label with the next frame
def update_gif_label(frame_index=0):
    frame = gif_frames[frame_index]
    gif_label.configure(image=frame)
    window.after(50, update_gif_label, (frame_index + 1) % len(gif_frames))

# Create a label to display the assistant's responses
response_label = tk.Label(window, text="", font=("Helvetica", 16))
response_label.pack(pady=20)

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to process voice commands
def takecommand(command):
    command = command.lower()
    if 'hello' in command:
        response_label.config(text="Hello! How can I help you?")
        speak("Hello! How can I help you?")
    elif 'goodbye' in command:
        response_label.config(text="Goodbye! Have a nice day!")
        speak("Goodbye! Have a nice day!")
        window.destroy()
    if 'wikipedia' in query:
        speak('Searching Wikipedia...')
        query = query.replace("wikipedia","")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        print(results)
        speak(results)

    elif 'open youtube' in query:
        webbrowser.open("youtube.com")

    elif 'open google' in query:
        webbrowser.open("google.com")

    elif 'open Whatsapp' in query:
        webbrowser.open("web.whatsapp.com")

    elif'open mail' in query:
        webbrowser.open("mail.google.com/mail/u/0/?tab=rm#inbox")

    elif'i want to talk to my son' in query:
        webbrowser.open("meet.google.com")

    elif'i want to talk to my friend' in query:
        webbrowser.open("meet.google.com")    

    elif'i want to talk to my family' in query:
        webbrowser.open("meet.google.com")
    
    elif'who are you' in query:
        speak("I am TNSA !æksa! made by TNSA devlopers. I am a AI voice assistant")

    elif'what is your name' in query:
        speak("my name is !æksa!")

    elif 'i am bored' in query:
        speak("how can it be possible! when i am here !can I tell you some funny jokes ?")
        joke=pyjokes.get_joke(language='en', category= 'all')
    


        print(joke)
        speak(joke)

    elif 'tell me jokes' in query:
        speak("okay")
        joke=pyjokes.get_joke(language='en', category= 'all')
    


        print(joke)
        speak(joke)



    elif'i want to eat something' in query:
        webbrowser.open("www.google.com/maps/search/Restaurants")

    elif 'recipe of' in query:
        speak('collecting best recipes...')
        query = query.replace("recipe", "")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Web results")
        print(results)
        speak(results)
    
    elif 'what is the meaning of' in query:
        speak('collecting best results')
        query = query.replace("what is the meaning of", "")
        results = wikipedia.summary(query, sentences=2)
        speak("the meaning of")
        print(results)
        speak(results)

    elif 'what is' in query:
        speak('collecting best results')
        query = query.replace("what is", "")
        results = wikipedia.summary(query, sentences=2)
        speak("it is a")
        print(results)
        speak(results)

    elif 'why is' in query:
        speak('collecting best results')
        query = query.replace("why is", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'why was' in query:
        speak('collecting best results')
        query = query.replace("why was", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'when was' in query:
        speak('collecting best results')
        query = query.replace("when was", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'how is' in query:
        speak('collecting best results')
        query = query.replace("how is", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'how was' in query:
        speak('collecting best results')
        query = query.replace("how was", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'why are' in query:
        speak('collecting best results')
        query = query.replace("why are", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'when is' in query:
        speak('collecting best results')
        query = query.replace("when is", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'when are' in query:
        speak('collecting best results')
        query = query.replace("when are", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'how are' in query:
        speak('collecting best results')
        query = query.replace("how are", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'where' in query:
        speak('collecting best results')
        query = query.replace("", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)

    
    elif 'who' in query:
        speak('collecting best results')
        query = query.replace("", "")
        results = wikipedia.summary(query, sentences=2)
        print(results)
        speak(results)
    

    elif 'play music' in query:
        speak("playing music")
        webbrowser.open("https://music.youtube.com/watch?v=UfcAVejslrU&list=RDCLAK5uy_mwJztsnautpobBg-95AVJ_xd5Gnb5DV-w")

    elif'play party music' in query:
        webbrowser.open("https://open.spotify.com/playlist/1d4wPjgVkLg2R30IAVKvHY?si=bb5827fe6ad646e6")

    elif 'the time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")    
        speak(f"the time is {strTime}")

    elif 'can I change your name' in query:
        speak("nope! becaues i am already named as !æksa!")

    elif'hey listen' in query:
        speak("yes,how can i help you?")

    elif'good morning' in query:
        speak("good morning")

    elif'good afternoon' in query:
        speak("good afternoon")

    elif'good evening' in query:
        speak("good evening")

  

# Function to handle button click event
def button_click():
    response_label.config(text="Listening...")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        response_label.config(text="Recognizing...")
        command = recognizer.recognize_google(audio)
        response_label.config(text="Command: " + command)
        takecommand(command)
    except sr.UnknownValueError:
        response_label.config(text="Sorry, I could not understand audio.")
    except sr.RequestError as e:
        response_label.config(text="Could not request results from Google Speech Recognition service.")

# Create a button for voice input
button = tk.Button(window, text="Speak", font=("Helvetica", 14), command=button_click)
button.pack(pady=10)

# Run the Tkinter event loop and start the GIF animation
update_gif_label()
window.mainloop()
