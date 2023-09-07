from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
import re
import random


class PySeoHtml:
    def __init__(self, html_text, keywords, max_link_length=500, random_links=False):
        self.html_text = html_text
        self.keywords = {keyword.lower(): link for keyword,
                         link in keywords.items()}
        self.keyword_dict = {}  # Словарь для хранения ключевых слов и их идентификаторов
        self.tokenizer = WordPunctTokenizer()
        self.max_link_length = max_link_length
        seed = None if random_links else 42
        self.random_generator = random.Random(seed)

    def process_text(self):
        # Normalize the HTML
        soup = BeautifulSoup(self.html_text, 'html.parser')
        html_text = soup.prettify()

        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(html_text, 'html.parser')

        paragraphs = soup.find_all('p')  # Находим все абзацы в HTML

        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text()
            tokens = self.tokenizer.tokenize(paragraph_text)

            new_tokens = []

            for token in tokens:
                matched_keyword = None
                for keyword, link in self.keywords.items():
                    if keyword in token.lower():
                        matched_keyword = keyword
                        break

                if matched_keyword:
                    link = self.keywords[matched_keyword]

                    # Генерируем уникальный идентификатор для ключевого слова
                    keyword_id = f'__id{len(self.keyword_dict) + 1}__'

                    # Добавляем ключевое слово и его идентификатор в словарь
                    self.keyword_dict[keyword_id] = (token, link)

                    # Заменяем ключевое слово на его идентификатор
                    token = keyword_id

                new_tokens.append(token)

            # Join tokens back into text and replace the paragraph content
            paragraph_text = ' '.join(new_tokens)
            paragraph.string.replace_with(paragraph_text)

        # Remove HTML escaping
        processed_html = str(soup).replace('&lt;', '<').replace('&gt;', '>')

        # Remove extra spaces before punctuation
        processed_html = re.sub(r'\s+([.!?,:;])', r'\1', processed_html)

        processed_html = self.post_process_text(processed_html)

        # Find all <a> tags in the processed HTML
        all_a_tags = re.findall(r'<a[^>]*>.*?</a>', processed_html)

        # Calculate the number of <a> tags to remove
        tags_to_remove = len(all_a_tags) - \
            len(processed_html) // self.max_link_length

        # Remove extra <a> tags
        if tags_to_remove > 0:
            tags_to_remove_indices = random.sample(
                range(len(all_a_tags)), tags_to_remove)
            for index in sorted(tags_to_remove_indices, reverse=True):
                tag_to_remove = all_a_tags.pop(index)
                tag_contents = re.search(r'>(.*?)</a>', tag_to_remove).group(1)
                processed_html = processed_html.replace(
                    tag_to_remove, tag_contents, 1)

        return processed_html

    def post_process_text(self, processed_html):
        for keyword_id, (keyword, link) in self.keyword_dict.items():

            replace = f'<a href="{link}">{keyword}</a>'
            processed_html = processed_html.replace(keyword_id, replace)

        return processed_html
