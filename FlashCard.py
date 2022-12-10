from tkinter import *
import pandas as pd
from playsound import playsound
import requests

session = requests.Session()

BACKGROUND_COLOR = "#393E46"
FONT_Title = "Times"
FONT_English = "Comic Sans MS"
FONT_Translation = "Helvetica"
data = pd.read_csv('data/Flash Cards.csv')
new_word = None
pronunciation_link = None
app_id = "Your app_id"
app_key = "Your app_key"
source_lang = "en"
target_lang = "de"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
           "Accept-Encoding": "*",
           "Connection": "keep-alive", "Content-Type": "application/json", "Accept": "application/json",
           "app_id": app_id, "app_key": app_key}


# ---------------------------- Change Card ------------------------------- #
def next_card():
    global new_word
    new_word = data[data.Tick == data.Tick.min()].sample().iloc[0]
    original_card()
    right_button.config(state=DISABLED)
    wrong_button.config(state=DISABLED)
    canvas.itemconfig(next_button, state=HIDDEN)
    canvas.itemconfig(previous_button, state=HIDDEN)
    window.update()
    translations = get_translations()
    new_word['Translations'] = translations
    sentence = get_sentence()
    new_word['Sentence'] = sentence
    get_pronunciation()
    play_sound()
    window.after(3000, func=sentence_card)


# ---------------------------- Original Card ------------------------------- #
def original_card():
    canvas.itemconfig(title, text="English", fill='black')
    canvas.itemconfig(word, text=new_word.English, fill='black', font=(FONT_English, 26, 'bold'))
    canvas.itemconfig(bg_image, image=card_front)
    canvas.itemconfig(previous_button, state=HIDDEN)


# ---------------------------- Sentence Card ------------------------------- #
def sentence_card():
    canvas.itemconfig(title, text="Sentence")
    sentence_text = new_word.Sentence
    canvas.itemconfig(word, text=sentence_text, font=(FONT_English, 14, 'bold'))
    canvas.itemconfig(bg_image, image=card_back)
    right_button.config(state=NORMAL)
    wrong_button.config(state=NORMAL)
    canvas.itemconfig(next_button, state=NORMAL)
    canvas.itemconfig(previous_button, state=NORMAL)


# ---------------------------- Meaning Card ------------------------------- #
def meaning_card():
    canvas.itemconfig(title, text="Translation", fill='black')
    canvas.itemconfig(word, text=new_word.Translations, fill='black', font=(FONT_Translation, 26, 'bold'))
    canvas.itemconfig(bg_image, image=card_front)

    canvas.itemconfig(next_button, state=HIDDEN)


# ---------------------------- Tick the Known Card ------------------------------- #
def is_known():
    data.loc[data.English == new_word.English, "Tick"] += 1
    data.to_csv("data/Flash Cards.csv", index=False)
    next_card()


# ---------------------------- play pronunciation ------------------------------- #
def play_sound():
    try:
        playsound(pronunciation_link)
    except:
        pass


# ---------------------------- Get Translations ------------------------------- #
def get_translations():
    try:
        url = f"https://od-api.oxforddictionaries.com/api/v2/translations/" \
              f"{source_lang}/{target_lang}/{new_word.English.lower()}"
        translation_r = session.get(url, headers=headers)
        translation_r.raise_for_status()
        translation_data = translation_r.json()
        translations = translation_data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['translations']
        translations = [translation['text'] for translation in translations]
        translations = " - ".join(translations)
        return translations
    except:
        return "There is no translation"


# ---------------------------- Get Sentence ------------------------------- #
def get_sentence():
    try:
        url = f"https://od-api.oxforddictionaries.com/api/v2/sentences/{source_lang}/{new_word.English.lower()}"
        sentence_r = session.get(url, headers=headers)
        sentence_r.raise_for_status()
        sentence_data = sentence_r.json()
        sentence = sentence_data['results'][0]['lexicalEntries'][0]['sentences'][0]['text']
        return sentence
    except:
        return "There is no sentence"


# ---------------------------- Get Pronunciation ------------------------------- #
def get_pronunciation():
    try:
        global pronunciation_link
        url = f"https://od-api.oxforddictionaries.com/api/v2/entries/" \
              f"{source_lang}/{new_word.English.lower()}?fields=pronunciations&strictMatch=false"
        pronunciation_r = session.get(url, headers=headers)
        pronunciation_r.raise_for_status()
        pronunciation_data = pronunciation_r.json()
        pronunciation_link = pronunciation_data['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0][
            'audioFile']
    except:
        pronunciation_link = None


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Flash Card")
window.config(bg=BACKGROUND_COLOR, padx=55, pady=50)
window.minsize(width=600, height=500)
window.maxsize(width=600, height=500)
window.after(3000, func=sentence_card)

canvas = Canvas(width=500, height=329, highlightthickness=0, bg=BACKGROUND_COLOR)
card_front = PhotoImage(file="images/card_front.png")
card_back = PhotoImage(file="images/card_back.png")
bg_image = canvas.create_image(250, 165, image=card_front)
title = canvas.create_text(250, 50, text="", font=(FONT_Title, 18, 'italic', 'bold'))
word = canvas.create_text(250, 175, text="", justify="center", width=360)
next_button_img = PhotoImage(file="images/next.png")
next_button = canvas.create_image(460, 175, image=next_button_img)
canvas.tag_bind(next_button, "<Button-1>",
                lambda event: meaning_card() if canvas.itemcget(title, 'text') == "Sentence" else sentence_card())
previous_button_img = PhotoImage(file="images/previous.png")
previous_button = canvas.create_image(30, 175, image=previous_button_img)
canvas.tag_bind(previous_button, "<Button-1>",
                lambda event: original_card() if canvas.itemcget(title, 'text') == "Sentence" else sentence_card())
canvas.grid(row=0, column=0, columnspan=3)

wrong_img = PhotoImage(file="images/Wrong.png")
wrong_button = Button(image=wrong_img, bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                      command=next_card, borderwidth=0, highlightthickness=0)
wrong_button.grid(row=1, column=0)

sound_img = PhotoImage(file="images/sound.png")
sound_button = Button(image=sound_img, bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                      command=play_sound, borderwidth=0, highlightthickness=0)
sound_button.grid(row=1, column=1)

right_img = PhotoImage(file="images/Right.png")
right_button = Button(image=right_img, bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                      command=is_known, borderwidth=0, highlightthickness=0)
right_button.grid(row=1, column=2)

next_card()
window.mainloop()
