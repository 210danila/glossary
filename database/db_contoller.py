import sqlite3
from datetime import datetime


class DBContoller:

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)

    def close(self):
        if self.conn:
            self.conn.close()

    def now(self):
        return str(datetime.now().strftime('%Y-%m-%d'))

    def normalize(self, text: str):
        return text.replace("'", "`").strip()

    def select(self, table: str, column: str, value):
        cursor = self.conn.cursor()
        value = str(value) if not isinstance(value, str) else '\'' + str(value) + '\''
        query = f'SELECT * FROM {table} WHERE {column} = {value}'
        cursor.execute(query)
        return cursor.fetchall()

    def insert(self, table: str, columns: list, values: list):
        cursor = self.conn.cursor()
        values = map(lambda value: "'" + str(value) + "'", values)
        columns_str = ', '.join([*list(map(str, columns)), 'created_at'])
        values_str = ', '.join([*values, "'" + str(self.now()) + "'"])
        query = f'INSERT INTO {table} ({columns_str}) VALUES ({values_str})'
        cursor.execute(query)
        self.conn.commit()
        return cursor.lastrowid

    def update(self, table: str, new_data: tuple, where: tuple):
        """
        Params:
        new_data (list): Column and value to update [column, value]
        where_clause (list): The record to be updated [column, value]
        """
        cursor = self.conn.cursor()
        data_column, data_value = list(map(str, new_data))
        where_column, where_value = list(map(str, where))
        query = f"UPDATE {table} SET {data_column} = {data_value} WHERE {where_column} = {where_value}"
        cursor.execute(query)
        self.conn.commit()

    def insert_word_entity(self, lemma: str, data: dict):
        # Create new word entity
        columns = ['lemma', 'uk_url', 'us_url']
        values = [lemma, data['uk_audio_url'], data['us_audio_url']]
        word_id = self.insert('words', columns, values)
        # Create new score
        columns = ['word_id', 'checks_count']
        values = [word_id, 0]
        self.insert('word_scores', columns, values)

        for block in data['blocks']:
            word_id = self.select('words', 'lemma', lemma)[0][0]
            # Create new block
            block_id = self.insert('meaning_blocks', ['word_id'], [word_id])
            # Create translations
            for translation in block['translations']:
                values = [word_id, block_id, self.normalize(translation)]
                self.insert('translations', ['word_id', 'block_id', 'translation'], values)
            # Create examples
            for example in block['examples']:
                values = [word_id, block_id, self.normalize(example)]
                self.insert('examples', ['word_id', 'block_id', 'example'], values)
            # Create definition
            values = [word_id, block_id, self.normalize(block['definition'])]
            self.insert('definitions', ['word_id', 'block_id', 'definition'], values)

    def select_block_data(self, block_record: str):
        block_id = str(block_record[0])
        translations = self.select('translations', 'block_id', block_id)
        definition_record = self.select('definitions', 'block_id', block_id)
        definition = definition_record[0] if len(definition_record) > 0 else ''
        examples = self.select('examples', 'block_id', block_id)
        return {
            'translations': list(map(lambda translation: translation[3], translations)),
            'definition': definition[3],
            'examples': list(map(lambda example: example[3], examples))
        }

    def select_blocks(self, lemma: str):
        words_records = self.select('words', 'lemma', lemma)
        if len(words_records) == 0:
            return []
        word_id = str(words_records[0][0])
        blocks = self.select('meaning_blocks', 'word_id', word_id)
        blocks_data = list(map(self.select_block_data, blocks))
        return blocks_data

    def select_word_data(self, lemma: str):
        data = self.select('words', 'lemma', lemma)[0]
        print(data)
        return {
            'uk_url': data[2],
            'us_url': data[3]
        }

    def increase_checks_count(self, column: str, value: int | str):
        checks_count_record = self.select('word_scores', column, str(value))
        if len(checks_count_record) == 0:
            raise Exception('No such checks_count record where %s = %s.' % (column, str(value)))
        checks_count = checks_count_record[0][2]
        self.update('word_scores', ('checks_count', checks_count + 1), (column, value))
