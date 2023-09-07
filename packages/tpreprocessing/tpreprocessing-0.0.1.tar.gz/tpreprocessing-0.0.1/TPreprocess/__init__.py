import nltk
import string
import re
from nltk.tokenize import RegexpTokenizer
from nltk import WordNetLemmatize

nltk.download('wordnet') 
nltk.download('stopwords')


# function to convert the text to lower case
def convert_to_lowercase(text):
    return text.str.lower()

# function to remove punctuations from the text
def remove_punctuations(text):
    eng_punctuation = string.punctuation
    translator = str.maketrans('','', eng_punctuation)
    return str(text).translate(translator)

# function to remove stopwords from the text
def remove_stopwords(text):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('english'))
    return " ".join([word for word in str(text).split() if word not in stopwords])

# function to remove repeating characters
def remove_repeating_characters(text):
    return re.sub(r'(.)1+', r'1', text)

# function to remove numeric text
def remove_numeric(text):
    return re.sub('[0-9]+', '', text)

# Tokenizing the text
def tokenize_text(text):
    tokenizer = RegexpTokenizer('\w+')
    text = text.apply(tokenizer.tokenize)
    return text

# lemmatizing the text. Converting some of the words to their root form.
def text_lematization(text):
    lm = WordNetLemmatizer()
    text = [lm.lemmatize(word) for word in text]
    return text


def preprocess(text):
    text = convert_to_lowercase(text)
    text = text.apply(lambda x : remove_punctuations(x))
    text = text.apply(lambda x : remove_stopwords(x))
    text = text.apply(lambda x : remove_repeating_characters(x))
    text = text.apply(lambda x : remove_numeric(x))
    text = tokenize_text(text)
    text = text.apply(lambda x : text_lematization(x))
    text = text.apply(lambda x: " ".join(x))
    return text