import subprocess
import notify2
import requests
import os
from nltk.stem import WordNetLemmatizer
from constants import SUGGESTIONS_MESSAGE


def normalize_word(word: str):
    word = word.lower().strip()
    if word.find(' ') == -1:
        lemmatizer = WordNetLemmatizer()
        # Finding lemma is only for verbs, another parts of speech
        # will be lemmatized in retrieve_lemma_from_url function
        word = lemmatizer.lemmatize(word, pos='v')
    return word


def retrieve_lemma_from_url(url: str):
    left_index = url.rfind('/')
    query_string_pos = url.find('?')
    right_index = query_string_pos if query_string_pos != -1 else len(url)
    return url[left_index + 1:right_index]


def make_request(url: str):
    proxies = {
        'http': os.getenv('PROXY'),
        'https': os.getenv('PROXY')
    }
    user_agent = os.getenv('USER_AGENT')
    headers = {'User-Agent': user_agent}
    if os.getenv('USE_PROXY') != "False":
        return requests.get(url, allow_redirects=True, headers=headers, proxies=proxies)
    else:
        return requests.get(url, allow_redirects=True, headers=headers)


def get_selected_text():
    # Run xlip to retrieve selected text
    result = subprocess.run(['xclip', '-o', '-selection', 'primary'], capture_output=True, text=True)
    return result.stdout


def send_notification(title: str, message: str):
    notify2.init("Notification")
    n = notify2.Notification(title, message)
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.show()


def create_notification(data: list, type: str = 'definitions'):
    message = '' if type != 'suggestions' else SUGGESTIONS_MESSAGE
    for element in data:
        if 'translations' in element:
            translations = element['translations']
            translations_joined = ', '.join(translations)
        if type == 'definitions':
            definition = element['definition']
            message += f'<b style="color:blue">{translations_joined}</b>\n{definition}\n'
        elif type == 'examples':
            examples = element['examples']
            examples_joined = '\n'.join(examples)
            message += f'<b>{translations_joined}</b>\n{examples_joined}\n'
        elif type == 'entities':
            text, url = element
            message += f'{text} <a href="{url}">🡽</a> | '
        elif type == 'suggestions':
            message += element + '\n'
    return message
