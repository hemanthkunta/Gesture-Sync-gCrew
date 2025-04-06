import speech_recognition as sr
import pyttsx3
import pyautogui
import subprocess
import webbrowser

# Setup
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    print(f"🔊 {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎙 Listening...")
        audio = recognizer.listen(source, phrase_time_limit=4)
        try:
            cmd = recognizer.recognize_google(audio).lower()
            print(f"🗣 Command: {cmd}")
            return cmd
        except:
            speak("Didn't catch that.")
            return ""

def execute(cmd):
    if "open notepad" in cmd:
        subprocess.Popen(["notepad.exe"])
        speak("Opening Notepad")

    elif "open calculator" in cmd:
        subprocess.Popen(["calc.exe"])
        speak("Opening Calculator")
    
    elif "close window" in cmd:
        pyautogui.hotkey('alt', 'f4')
        speak("Closing window")

    elif "maximize" in cmd:
        pyautogui.hotkey('win', 'up', 'up')
        speak("Maximizing window")

    elif "minimize" or "minimise" in cmd:
        pyautogui.hotkey('win', 'down', 'down')
        speak("Minimizing window")

    elif "open youtube" in cmd:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
    
    elif "open instagram" in cmd:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram")
    
    elif "open browser" in cmd:
        webbrowser.open("https://www.google.com")
        speak("Opening Browser")
    
    elif "exit" in cmd or "stop" in cmd:
        speak("Goodbye!")
        exit()
        

    else:
        speak("Command not found.")

# Run loop
while True:
    command = listen()
    if command:
        execute(command)