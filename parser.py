from utils import make_request, retrieve_lemma_from_url
from bs4 import BeautifulSoup
from bs4.element import Tag
from constants import HOMEPAGE, NO_ENTITIES_MESSAGE


class Parser:

    MAX_PAGES_COUNT = 5

    def __init__(self, lemma: str):
        self.lemma = lemma
        self.html = None

    def get_html(self):
        return self.html

    def get_lemma(self):
        return self.lemma

    def set_html(self, html: str):
        self.html = html

    def set_lemma(self, lemma: str):
        self.lemma = lemma

    def save_html(self, url: str):
        response = make_request(url)
        self.set_html(response.text)
        self.set_lemma(retrieve_lemma_from_url(response.url))

        f = open('storage/html', 'w+')
        f.write(self.get_html())
        f.close()
        return response

    def make_block(self, parent_tag: Tag):
        # Get translations in the meaning block
        translation_tag = parent_tag.find('span', class_='trans dtrans dtrans-se')
        translations = []
        if (translation_tag is not None):
            translation_text = translation_tag.text.strip()
            translations = translation_text.split(', ')

        # Get definition in the meaning block
        definition_tag = parent_tag.find('div', class_='def ddef_d db')
        definition = definition_tag.text.strip()

        # Get examples in the meaning block
        example_tags = parent_tag.find_all('span', class_='deg')
        examples = list(map(lambda tag: tag.text.strip(), example_tags))

        # Create new block
        return {
            'translations': translations,
            'definition': definition,
            'examples': examples
        }

    def parse_translations_html(self):
        soup = BeautifulSoup(self.get_html(), 'html.parser')

        # Get parent tags with meaning blocks of the word
        parent_tags = soup.find_all('div', class_='sense-body dsense_b')
        blocks = []
        for parent_tag in parent_tags:
            blocks.append(self.make_block(parent_tag))

        # Get mp3 pronunciations (UK, US)
        parent_tag_uk = soup.find('span', class_='uk dpron-i')
        uk_audio_url = HOMEPAGE + parent_tag_uk.find('source').get('src')
        parent_tag_us = soup.find('span', class_='us dpron-i')
        us_audio_url = HOMEPAGE + parent_tag_us.find('source').get('src')

        return {
            'blocks': blocks,
            'uk_audio_url': uk_audio_url,
            'us_audio_url': us_audio_url
        }

    def parse_suggestions_html(self):
        soup = BeautifulSoup(self.get_html(), 'html.parser')

        # Get parent tags with suggestions
        parent_tags = soup.find_all('li', class_='lbt lp-5 lpl-20')
        suggestions = list(map(
            lambda parent_tag: parent_tag.find('a').text.strip(),
            parent_tags
        ))
        return suggestions

    def parse_entities_with_word(self, url: str):
        entities = []
        for page in range(1, self.MAX_PAGES_COUNT + 1):
            url_of_page = url + '&page=' + str(page)
            res = self.save_html(url_of_page)
            # If there are no pages with entities containing the word
            if res.history and res.history[0].status_code == 302:
                return [[NO_ENTITIES_MESSAGE, res.url]]

            soup = BeautifulSoup(self.get_html(), 'html.parser')
            parent_tags = soup.find_all('li', class_='lbt lp-5 lpl-20 hax')
            # If there are no entities containing the word on a page
            if len(parent_tags) == 0:
                break

            for parent_tag in parent_tags:
                text = parent_tag.find('span', class_='base').text
                entity_url = parent_tag.find('a')['href']
                entities.append([text, entity_url])

        return entities
