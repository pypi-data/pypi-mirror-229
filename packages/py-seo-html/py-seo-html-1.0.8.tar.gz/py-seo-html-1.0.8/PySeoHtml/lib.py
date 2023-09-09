from bs4 import BeautifulSoup
import re
import random

from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import nltk

nltk.download('punkt')

stemmer_languages = [
    "arabic",
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "hungarian",
    "italian",
    "norwegian",
    "porter",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
]


class PySeoHtml:
    def __init__(self, html_text, keywords,
                 density=500,
                 random_links=False,
                 stemming=True,
                 language="english",
                 valid_tags=["p", "h1", "h2", "h3", "h4", "h5", "h6"],
                 ):
        """
        Initialize the PySeoHtml class.

        Args:
            html_text (str): The HTML text to process.
            keywords (list): A list of keywords and links to replace them with.
            density (int): The desired link density (default is 500 characters per link).
            random_links (bool): Whether to place links randomly (default is False).
            stemming (bool): Whether to stem the keywords (default is False).
            language (str): The language to use for stemming (default is "english").
        """

        self.stemmer = None

        # Make sure the language is supported
        if stemming:
            if language not in stemmer_languages:
                raise ValueError(
                    f"Language must be one of {stemmer_languages}")
            self.stemmer = SnowballStemmer(language)

        # Make sure the keywords are in the correct format
        keywords_groups = []
        for keyword, link in keywords:
            keyword = keyword.lower().strip()
            keyword_words = keyword.split(" ")
            for word in keyword_words:
                if len(word) > 3:
                    if stemming:
                        word = self.stemmer.stem(word)
                    keywords_groups.append([word, link])

        # print("keywords_groups", keywords_groups)

        self.keywords_groups = keywords_groups
        self.language = language
        self.valid_tags = valid_tags
        self.html_text = html_text
        self.density = density
        seed = None if random_links else 42
        self.random_generator = random.Random(seed)

    def make(self):
        try:
            return self._process_text()
        except Exception as e:
            raise f"Error processing text: {e}"

    def _process_text(self):
        """
        Process the HTML text and replace keywords with links.

        Returns:
            str: The processed HTML text with keywords replaced by links.
        """
        # Parse the HTML text using BeautifulSoup
        soup = BeautifulSoup(self.html_text, 'html.parser')

        # Find all text nodes in HTML
        text_nodes = soup.find_all(string=True)

        sentences = []

        for text_node in text_nodes:

            if text_node.parent.name not in self.valid_tags:
                continue

            # Tokenize the text into words
            words = word_tokenize(text_node)

            idx = 0
            while idx < len(words):
                word = words[idx]

                for keywords, link in self.keywords_groups:

                    found = False
                    for keyword in keywords:
                        if word.lower().startswith(keyword):
                            found = True
                            break

                    if found:
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

        return self._pretty_html(self.html_text)

    def _pretty_html(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        pretty_html = soup.prettify()
        return pretty_html


if "__main__" == __name__:

    html_text = """
    <h1>Enhance Your SEO with PySeoHtml</h1>
    <p>PySeoHtml is a powerful Python library that can help boost your website's SEO performance. By intelligently linking specific keywords within your content, you can improve search engine rankings and increase organic traffic.</p>
    <p>Here are some examples of keywords you can link:</p>
    <ul>
        <li>Search Engine Optimization</li>
        <li>Keyword Research</li>
        <li>On-Page SEO</li>
        <li>Link Building</li>
    </ul>
    """

    keywords = [
        ["Search Engine Optimization", "https://example.com/seo"],
        ["Keyword Research", "https://example.com/keyword-research"],
        ["On-Page SEO", "https://example.com/on-page-seo"],
        ["Link Building", "https://example.com/link-building"],
        # Add more keyword-link pairs as needed
    ]

    # Initialize PySeoHtml
    seo_html = PySeoHtml(
        html_text=html_text,
        keywords=keywords,
        density=500,
        random_links=False,
        stemming=True,
        language="english",
        valid_tags=["p", "h1", "h2", "h3", "h4", "h5", "h6"],
    )

    # Generate the processed HTML content
    processed_html = seo_html.make()

    print(processed_html)
