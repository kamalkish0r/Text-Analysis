import pandas as pd
from os import listdir
from os.path import isfile, join
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
from nltk.corpus import wordnet
from tqdm import tqdm
import re

import nltk
nltk.download('punkt')
nltk.download('wordnet')


stop_words = set()
negative_words = set()
positive_words = set()


def put_words_in_set(s, file_path, encoding):
    """
    Put words in set.
    params: 
        s : set object
        file_path : path to file in which words are present
        encoding : encoding format to read from file
    """

    with open(file_path, 'r', encoding=encoding) as file:
        words = file.read().split()
        for word in words:
            word.lower()
        s.update(words)

def get_stop_words():
    """Add the stop words to stop_words set"""

    stop_words_dir = "./data/StopWords/"
    onlyfiles = [f for f in listdir(stop_words_dir) if isfile(join(stop_words_dir, f))]
    for file_name in tqdm(onlyfiles):
        file_path = stop_words_dir + file_name
        print(file_path)

        put_words_in_set(s=stop_words, file_path=file_path, encoding='latin-1')
    
    print(f'Total {len(stop_words)} stop words found')

def get_dictionary():
    """create dictionary using positive/negative words"""

    dictionary_path = './data/MasterDictionary/'
    positive_filepath = dictionary_path + 'positive-words.txt'
    negative_filepath = dictionary_path + 'negative-words.txt'

    put_words_in_set(s=positive_words, file_path=positive_filepath, encoding='latin-1')
    put_words_in_set(s=negative_words, file_path=negative_filepath, encoding='latin-1')

    print(f'{len(positive_words)} positive words')
    print(f'{len(negative_words)} negative words')

def count_syllables(word):
    c = 0
    vowels = 'aeiou'
    l = re.findall(f'(?!e$)(?!es$)(?!ed$)[{vowels}]', word, re.I)
    return len(l)

def analyse(article):
    """
    Perform analysis of an article, compute the values of variables : 
    - POSITIVE SCORE
    - NEGATIVE SCORE
    - POLARITY SCORE
    - SUBJECTIVITY SCORE
    - AVG SENTENCE LENGTH
    - PERCENTAGE OF COMPLEX WORDS
    - FOG INDEX
    - AVG NUMBER OF WORDS PER SENTENCE
    - COMPLEX WORD COUNT
    - WORD COUNT
    - SYLLABLE PER WORD
    - PERSONAL PRONOUNS
    - AVG WORD LENGTH

    params:
        article : str text of article to be analysed
    
    returns a dictionary containing values of the variables
    """
    # Tokenize the text into sentences
    sentences = sent_tokenize(article)
    tokenizer = RegexpTokenizer(r'\w+')

    # Remove stop words and reconstruct sentences
    filtered_sentences = []
    filtered_tokens = []
    for sentence in sentences:
        words = tokenizer.tokenize(sentence)
        filtered_tokens.extend([word for word in words if word.lower() not in stop_words])
        reconstructed_sentence = ' '.join(filtered_tokens)
        if reconstructed_sentence:
            filtered_sentences.append(reconstructed_sentence)
    
    total_words = len(filtered_tokens)

    # Extract derived variables
    positive_score, negative_score = 0, 0
    for token in filtered_tokens:
        positive_score += 1 if token.lower() in positive_words else 0
        negative_score -= 1 if token.lower() in negative_words else 0
    
    # multiply the score with -1 so that the score is a positive number.
    negative_score *= -1

    # polarity_score determines if a given text is positive or negative in nature.
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)

    # subjectivity_score determines if a given text is objective or subjective. 
    subjectivity_score = (positive_score + negative_score) / (total_words + 0.000001)



    # Calculate average sentence length
    total_sentences = len(filtered_sentences)
    average_sentence_length = total_words / total_sentences

    # Calculate the complex words
    complex_word_cnt = 0
    for word in filtered_tokens:
        if len(wordnet.synsets(word)) > 0 and len(wordnet.synsets(word)[0].lemma_names()) > 2:
            complex_word_cnt += 1
    
    percentage_complex_words = complex_word_cnt / len(filtered_tokens)

    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)


    # Average Number of Words Per Sentence
    avg_number_of_words_per_sentence = len(filtered_tokens) / len(filtered_sentences)
    
    # syllable count 
    syllable_sum = 0
    for word in filtered_tokens:
        syllable_sum += count_syllables(word)
    
    syllable_count = syllable_sum / len(filtered_tokens)

    # Word Count
    word_count = len(filtered_tokens)


    # Personal Pronouns
    pronoun_count = re.compile(r'\b(I|we|ours|my|mine|(?-i:us))\b', re.I)
    pronouns = pronoun_count.findall(article)
    personal_pronoun_count = len(pronouns)


    # Average Word Length
    total_chars = 0
    for word in filtered_tokens:
        total_chars += len(word)
    
    average_word_length = total_chars / len(filtered_tokens)

    variables = {
        'positive_score': positive_score,
        'negative_score': negative_score,
        'polarity_score': polarity_score,
        'subjectivity_score': subjectivity_score,
        'avg_sentence_length': average_sentence_length,
        'percentage_of_complex_words': percentage_complex_words,
        'fog_index': fog_index,
        'avg_number_of_words_per_sentence': avg_number_of_words_per_sentence,
        'word_count': word_count,
        'syllable_per_word': syllable_count,
        'personal_pronouns': personal_pronoun_count,
        'avg_word_length': average_word_length
    }

    return variables

def get_article(url_id, url):
    """Scrapes the text of article and saves to url_id.txt file"""

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the title and content
    title = None
    try:
        title = soup.find('h1', {'class': 'entry-title'}).text.strip()
    except Exception as e:
        print(f'Error while fetching the title for {url} : {e}')
    
    if title is None:
        try:
            title = soup.find('h1', {'class': 'tdb-title-text'}).text.strip()
        except Exception as e:
            print(f'Error while fetching the title for {url} : {e}')
            title = 'No Title'

    content = None
    try:
        content = soup.find('div', {'class': 'td-post-content tagdiv-type'}).text
    except Exception as e:
        print(f'Error while fetching content for {url} : {e}')
    
    if content is None:
        try:
            # encountered on 14th url
            content = soup.find_all('div', {'class': 'tdb-block-inner td-fix-index'})[14].text
        except Exception as e:
            print(f'Error while fetching content for {url} : {e}')
            content = ""

    # write to file
    file_path = './data/extracted_text/' + url_id + '.txt'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\n\n")
        file.write(f"Content:\n{content}")
    
    print(f'Saved article {file_path}')

def get_all_articles():
    """Iterate on each url present in Input.xlsx and saves text of each article to txt file"""

    input_urls = pd.read_excel('./data/Input.xlsx')

    print('Fetching articles...')
    for index, row in tqdm(input_urls.iterrows()):
        get_article(url_id=row['URL_ID'], url=row['URL'])

def analyse_articles():
    """Iterates on articles, analyse them, computer values of variables and saves them to Output Data Structure.xlsx"""

    output_structure = pd.read_excel('./data/Output Data Structure.xlsx')
    for index, row in tqdm(output_structure.iterrows()):
        file_path = './data/extracted_text/' + row['URL_ID'] + '.txt'
        with open(file_path, 'r', encoding='utf-8') as file:
            article = file.read()
        
        print(f'Analysing : {row["URL_ID"]}....')
        variables = analyse(article)

        # Insert values into DataFrame 
        for col_name, value in variables.items():
            actual_col_name = col_name.upper().replace('_', ' ')
            if actual_col_name in output_structure.columns:
                output_structure.at[index, actual_col_name] = value
            else:
                print(f'unable to save to output structure : {e}')
    
    # Save the modified DataFrame back to Excel
    output_structure.to_excel('./data/Output Data Structure.xlsx', index=False)
    print(f'Saved results to `Output Data Structure.xlsx`')

if __name__ == '__main__':
    get_stop_words()
    get_dictionary()

    # step 2: get all the articles
    get_all_articles()

    print('\n\nfetched all articles\n\n')

    # step 3: analyse each article and compute the variables
    analyse_articles()

    print('Finished analysing articles.')