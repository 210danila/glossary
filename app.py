import os
from dotenv import load_dotenv
from pynput import keyboard
from playsound import playsound
from database.db_contoller import DBContoller
from parser import Parser
from utils import (
    normalize_word,
    create_notification,
    send_notification,
    get_selected_text
)
from constants import (
    TRANSLATIONS_URL,
    SEARCH_URL,
    NO_MATCHES_TEXT,
    SUGGESTIONS_TEXT,
    NO_MATCHES_MESSAGE
)


def show_word_data(mode: str):
    db = DBContoller('database/glossary.db')
    selected_text = get_selected_text()
    word = normalize_word(selected_text)
    parser = Parser(word)

    parser.save_html(TRANSLATIONS_URL + word)
    lemma = parser.get_lemma()
    sel = db.select('words', 'lemma', lemma)
    print(lemma)
    # If there is no such word in database
    if (len(sel) == 0):
        # If this word has not been found, but similar words have been found
        if SUGGESTIONS_TEXT in parser.get_html():
            suggestions = parser.parse_suggestions_html()
            notification_msg = create_notification(suggestions, 'suggestions')
            send_notification(word, notification_msg)
            return
        # If this word has not been found, and no similar words have been found
        elif NO_MATCHES_TEXT in parser.get_html():
            send_notification(word, NO_MATCHES_MESSAGE)
            return
        # If this word has been found
        else:
            data = parser.parse_translations_html()
            db.insert_word_entity(lemma, data)

    blocks = db.select_blocks(lemma)
    word_data = db.select_word_data(lemma)
    db.close()

    notify_msg = create_notification(blocks, mode)
    send_notification(lemma, notify_msg)
    print(word_data)
    mp3_file = word_data['us_url']
    playsound(mp3_file)
    print("Горячая клавиша нажата!")


def show_entities_containing_word():
    selected_text = get_selected_text()
    lemma = normalize_word(selected_text)
    parser = Parser(lemma)
    entities = parser.parse_entities_with_word(SEARCH_URL + lemma)
    print(entities)
    notify_msg = create_notification(entities, 'entities')
    send_notification('lemma', notify_msg)


if __name__ == "__main__":
    load_dotenv()
    try:
        with keyboard.GlobalHotKeys({
            os.getenv('DEFINITIONS_HOTKEY'): lambda: show_word_data('definitions'),
            os.getenv('EXAMPLES_HOTKEY'): lambda: show_word_data('examples'),
            os.getenv('ENTITIES_HOTKEY'): show_entities_containing_word
        }) as hotkey:
            hotkey.join()
    except BaseException as e:
        f = open('storage/log')
        f.write(e)
        f.close()
