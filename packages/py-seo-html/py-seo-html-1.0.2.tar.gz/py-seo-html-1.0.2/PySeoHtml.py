from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
import re
import random


class PySeoHtml:
    def __init__(self, html_text, keywords, max_link_length=500, random_links=False):
        # Initialize the PySeoHtml with HTML text and keywords to link to

        self.html_text = html_text
        self.keywords = {keyword.lower(): link for keyword,
                         link in keywords.items()}
        self.tokenizer = WordPunctTokenizer()
        self.punctuation = r'[.!?,:;]'

        # Maximum length of a linked text snippet
        self.max_link_length = max_link_length

        seed = None if random_links else 42
        self.random_generator = random.Random(seed)

    def process_text(self):

        # Normalize the HTML
        soup = BeautifulSoup(self.html_text, 'html.parser')
        html_text = soup.prettify()

        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(html_text, 'html.parser')

        paragraphs = soup.find_all('p')  # Find all paragraphs in the HTML

        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text()
            tokens = self.tokenizer.tokenize(paragraph_text)

            new_tokens = []

            i = 0
            while i < len(tokens):
                token = tokens[i]

                matched_keyword = None
                for keyword, link in self.keywords.items():
                    if keyword in token.lower():
                        matched_keyword = keyword
                        break

                if matched_keyword:
                    link = self.keywords[matched_keyword]

                    neighbor_tokens = [token]
                    left_count = 0
                    right_count = 0

                    j = i - 1
                    while j >= 0:
                        if re.match(self.punctuation, tokens[j]):
                            break
                        left_count += 1
                        neighbor_tokens.insert(0, tokens[j])
                        j -= 1
                        if left_count >= 2:
                            break

                    j = i + 1
                    while j < len(tokens):
                        if re.match(self.punctuation, tokens[j]):
                            break
                        right_count += 1
                        neighbor_tokens.append(tokens[j])
                        j += 1
                        if right_count >= 2:
                            break

                    if left_count <= 2 and right_count <= 2:
                        neighbor_text = ' '.join(neighbor_tokens)
                        if neighbor_text.endswith(('.', '!', '?', ',')):
                            neighbor_text = neighbor_text[:-
                                                          1] + f'</a>{neighbor_text[-1]}'
                        else:
                            neighbor_text += '</a>'
                        new_tokens.append(
                            f'<a href="{link}">{neighbor_text}')
                        i += left_count + right_count
                    else:
                        new_tokens.append(f'<a href="{link}">{token}')

                else:
                    new_tokens.append(token)

                i += 1

            # Join tokens back into text and replace the paragraph content
            paragraph_text = ' '.join(new_tokens)
            paragraph.string.replace_with(paragraph_text)

        # Remove HTML escaping
        processed_html = str(soup).replace('&lt;', '<').replace('&gt;', '>')

        # Remove extra spaces before punctuation
        processed_html = re.sub(r'\s+([.!?,:;])', r'\1', processed_html)

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
