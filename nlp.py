import heapq
import os
import nltk
import re
import spacy
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob

# Load SpaCy model once
nlp = spacy.load("en_core_web_sm")

# Ensure you have the necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")


def tokenization(text):
    sentences = sent_tokenize(text)
    words = [word_tokenize(sentence) for sentence in sentences]

    stop_words = set(stopwords.words("english"))
    # Add additional custom filters
    custom_filters = {"'s"}

    words_filtered = [
        [
            word
            for word in word_list
            if word.isalpha()  # Check if the word is alphabetic
            and word.lower() not in stop_words
            and word.lower() not in custom_filters
        ]
        for word_list in words
    ]

    flat_words = [word for sublist in words_filtered for word in sublist]
    word_freq = Counter(flat_words)
    common_topics = word_freq.most_common(10)

    return sentences, word_freq, common_topics


def topic_extraction(text):
    vectorizer = CountVectorizer(stop_words="english")
    X = vectorizer.fit_transform(text)

    lda = LatentDirichletAllocation(n_components=5, random_state=0)
    lda.fit(X)

    def display_topics(model, feature_names, no_top_words):
        topics = []
        for topic_idx, topic in enumerate(model.components_):
            topic_keywords = " ".join(
                [feature_names[i] for i in topic.argsort()[: -no_top_words - 1 : -1]]
            )
            topics.append(topic_keywords)
        return topics

    topics = display_topics(lda, vectorizer.get_feature_names_out(), 4)
    return topics


def sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # -1 to 1 (negative to positive)
    return sentiment


def named_entity_recognition(text):
    # Load SpaCy's English language model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    entities = Counter((ent.text.strip(), ent.label_) for ent in doc.ents)

    # Sort entities by frequency
    sorted_entities = [
        {"text": ent[0], "type": ent[1], "count": count}
        for ent, count in entities.items()
    ]
    sorted_entities.sort(key=lambda x: x["count"], reverse=True)

    return sorted_entities


def summarization(text, num_sentences=5):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Check if the number of sentences in the text is less than the summary length
    if len(sentences) < num_sentences:
        return text

    # Tokenize and clean words in each sentence
    stop_words = set(stopwords.words("english"))
    word_frequencies = defaultdict(int)
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word not in stop_words and word not in string.punctuation:
                word_frequencies[word] += 1

    # Rank sentences based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] += word_frequencies[word]

    # Select top n sentences for the summary
    summary_sentences = heapq.nlargest(
        num_sentences, sentence_scores, key=sentence_scores.get
    )
    summary = " ".join(summary_sentences)

    return summary


def question_detection(text):
    # Split the text into lines assuming each line is a separate statement
    lines = text.split("\n")
    questions = []

    for line in lines:
        # Check if the line contains a question
        if "?" in line:
            # Clean up line breaks, carriage returns, and extra spaces
            clean_line = line.replace("\r", "").replace("\n", "").strip()
            questions.append(clean_line)

    return questions


def NLP_processing(text):
    sentences, word_freq, common_topics = tokenization(text)
    #
    topics = topic_extraction(sentences)
    sentiment = sentiment_analysis(text)
    named_entities = named_entity_recognition(text)
    summary = summarization(text)
    questions = question_detection(text)

    return (
        sentences,
        word_freq,
        common_topics,
        topics,
        sentiment,
        named_entities,
        summary,
        questions,
    )
