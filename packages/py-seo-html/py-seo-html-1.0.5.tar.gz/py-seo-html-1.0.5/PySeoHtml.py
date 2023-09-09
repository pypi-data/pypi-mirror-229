from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import re
import random


class PySeoHtml:
    def __init__(self, html_text, keywords, density=500, random_links=False):
        """
        Initialize the PySeoHtml class.

        Args:
            html_text (str): The HTML text to process.
            keywords (dict): A dictionary of keywords and their corresponding links.
            density (int): The desired link density (default is 500 characters per link).
            random_links (bool): Whether to place links randomly (default is False).
        """
        self.html_text = html_text
        self.keywords = {keyword.lower(): link for keyword,
                         link in keywords.items()}
        self.density = density
        seed = None if random_links else 42
        self.random_generator = random.Random(seed)

    def process_text(self):
        """
        Process the HTML text and replace keywords with links.

        Returns:
            str: The processed HTML text with keywords replaced by links.
        """
        # Parse the HTML text using BeautifulSoup
        soup = BeautifulSoup(self.html_text, 'html.parser')

        # Find all text nodes in HTML
        text_nodes = soup.find_all(text=True)

        sentences = []

        for text_node in text_nodes:
            # Tokenize the text into words
            words = word_tokenize(text_node)

            idx = 0
            while idx < len(words):
                word = words[idx]

                for keyword, link in self.keywords.items():

                    if word.lower().startswith(keyword):
                        sentence_string = word

                        # Add neighboring words on the left (up to 3 or until punctuation) to the link
                        left_limit = max(0, idx - 3)
                        left_idx = idx - 1
                        while left_idx >= left_limit:
                            if re.match(r'\W', words[left_idx]):
                                break
                            sentence_string = words[left_idx] + \
                                " " + sentence_string
                            left_idx -= 1

                        # Add neighboring words on the right (up to 3 or until punctuation) to the link
                        right_limit = min(len(words), idx + 4)
                        right_idx = idx + 1
                        while right_idx < right_limit:
                            if re.match(r'\W', words[right_idx]):
                                break
                            sentence_string += " " + words[right_idx]
                            right_idx += 1

                        sentences.append([sentence_string, link])
                        idx = right_idx
                        break

                if idx < len(words):
                    idx += 1

        # Calculate the maximum allowed number of links in the text (not more than 1 per self.density characters)
        max_links = len(self.html_text) // self.density

        # Create a copy of the sentences list
        sentences_to_replace = sentences.copy()

        # Shuffle the sentences_to_replace list to select sentences randomly
        self.random_generator.shuffle(sentences_to_replace)

        # Initialize the link count
        link_count = 0

        # Replace sentences in html_text with links, considering the maximum allowed number of links
        for sentence in sentences_to_replace:
            if link_count >= max_links:
                break  # Exit the loop if the maximum number of links is reached
            self.html_text = self.html_text.replace(
                sentence[0], f'<a href="{sentence[1]}">{sentence[0]}</a>')
            link_count += 1

        return self.html_text
