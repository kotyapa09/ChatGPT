import tkinter
import customtkinter
import time
import config
import openai
import keyboard
import speech_recognition as sr
import sounddevice as sd
import torch
from PIL import ImageTk, Image

language = "ru"
model_id = "ru_v3"
sample_rate = 48000
speaker = "aidar"  # aidar, baya, kseniya, xenia, random
put_accent = True
put_yo = True
device = torch.device('cpu')
mode = 1

r = sr.Recognizer()

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id
                          )  # MODEL
model.to(device)

audio = model.apply_tts(text="Готов к работе",
                        speaker=speaker,
                        sample_rate=sample_rate,
                        put_accent=put_accent,
                        put_yo=put_yo
                        )
audio = model.apply_tts(text="Готов к работе",
                        speaker=speaker,
                        sample_rate=sample_rate,
                        put_accent=put_accent,
                        put_yo=put_yo
                        )


def speak(text, speaker):
    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo
                            )

    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop()


def choice_voice(spk):
    global speaker
    speaker = spk


def main():
    customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    app = customtkinter.CTk()  # create CTk window like you do with the Tk window
    app.geometry("600x630")
    app.resizable(False, False)
    app.title("ChatGPT")

    global bg_color
    bg_color = "grey17"

    voice = customtkinter.CTkOptionMenu(master=app, values=["aidar", "baya", "kseniya", "xenia"], command=choice_voice)
    voice.place(x=75, y=575)

    centerFrame = customtkinter.CTkFrame(master=app, width=550, height=500, fg_color="grey13")
    centerFrame.place(x=25, y=15)

    label = customtkinter.CTkLabel(master=app, bg_color="grey13", text="", wraplength=530)
    label.place(x=30, y=25)

    entry_text = tkinter.StringVar(app)

    entry = customtkinter.CTkEntry(master=app, width=550, fg_color="grey13", textvariable=entry_text)
    entry.place(x=25, y=525)

    def butt():
        label.configure(text=entry_text.get())
        openai.api_key = config.API_KEY

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": entry_text.get()}
            ]
        )
        entry_text.set("")

        label.configure(text=label.cget("text") + "\n\n" + completion.choices[0].message.content)
        speak(completion.choices[0].message.content, speaker)

    butt_enter = customtkinter.CTkButton(master=app, width=30, text=">", corner_radius=5, command=butt)
    butt_enter.place(x=545, y=525)

    def microphone():
        with sr.Microphone(device_index=0) as source:
            try:
                audio = r.listen(source, phrase_time_limit=5, timeout=7)
                query = r.recognize_google(audio, language='ru-RU')
                label.configure(text=query)

                openai.api_key = config.API_KEY

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": query}
                    ]
                )

                label.configure(text=label.cget("text") + "\n\n" + completion.choices[0].message.content)
                speak(completion.choices[0].message.content, speaker)

            except(sr.WaitTimeoutError, sr.UnknownValueError):
                label.configure(text="ERROR")

    image = ImageTk.PhotoImage(file="image.png")
    button_microphone = customtkinter.CTkButton(master=app, width=20, height=50, text="", corner_radius=25, command=microphone, image=image)
    button_microphone.place(x=257, y=565)

    keyboard.add_hotkey("enter", lambda: butt() if entry_text.get() else False)

    app.mainloop()


if __name__ == "__main__":
    main()
