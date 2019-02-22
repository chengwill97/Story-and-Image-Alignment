import os
import re
import csv
import pandas as pd
import numpy as np
from numpy import array
from math import sqrt
import nltk
nltk.download('punkt')

from app import app

class GloveVectors:

    DIMENSION = int(app.config.get('DIMENSION'))
    GLOVE_DEFAULT_MODEL = app.config.get('GLOVE_DEFAULT_MODEL')

    def __init__(self, model):
        self.model = model

    @staticmethod
    def load_resources():
        """Loads in the glove vectors
        """
        model      = dict()
        glove_path = GloveVectors.GLOVE_DEFAULT_MODEL

        if os.path.exists(glove_path):
            with open(glove_path, 'r') as glove_file:
                for line in glove_file:
                    word_vector = line.split()
                    word = word_vector.pop(0)
                    vector = np.array([float(val) for val in word_vector])
                    model[word] = vector

        return model

    def cosine(self, A, B):
        """Computes the cosine similarity of vectors A and B

        Args:
            A (np.array): array 1
            B (np.array): array 2

        Returns:
            float : Cosine similarity of vectors A and B
        """

        dot_prod = sum(A * B)
        mag_A    = sqrt(sum(A * A))
        mag_B    = sqrt(sum(B * B))

        return dot_prod / (mag_A * mag_B)

    def sentence_to_vec(self, sentence):
        """Creates word vector from tokens

        Args:
            sentence (str): sentence to get vector from

        Returns:
            np.array: vector representation of sentence
        """

        tokens = nltk.word_tokenize(sentence)

        return self.tokens_to_vec(tokens)

    def tokens_to_vec(self, tokens):
        """Creates word vector from tokens

        Args:
            tokens (list(str)): list of tokens

        Returns:
            np.array: vector representation of tokens
        """
        if len(tokens) == 0:
            return None

        # step 1: lower all words
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        """
        step 2-3: look up word vectors for each token,
        compute the component-wise sum of the
        word vectors , and divide by num words
        """
        vec = np.zeros(GloveVectors.DIMENSION)
        for token in tokens:
            try:
                vec += self.model[token]
            except KeyError:
                pass

        vec /= len(tokens)

        return vec

    def cosFromWord(self, df, word):
        """Compute cosine similarities of words in df to word

        Args:
            df (pandas.DataFrame): DataFrame of words and their vectors
            word (str): word to find similarity of

        Returns:
            pandas.DataFrame: words in df and their cosine similarity to word
        """
        myvec     = array(df.loc[word])
        words     = df.index
        cos_words = list()
        for i in range(len(df)):
            # acquire the vector representation of the word
            vec = array(df.iloc[i])
            # calculate the cosine similarity
            cos_sim = self.cosine(myvec, vec)
            # append the cosine similarity of the word and the word siteself to the list
            cos_words.append([cos_sim, words[i]])

        # Transform the sorted_cos_words list to put it in the dataframe
        sorted_cos_words = sorted(cos_words)
        sorted_cos_words.reverse()
        sorted_cos_words = np.array(sorted_cos_words)
        sorted_cos_words = np.transpose(sorted_cos_words)

        # Create the dataframe
        cos_words_df = pd.DataFrame({
            'Cosine Similarity' : sorted_cos_words[0],
            'Word'              : sorted_cos_words[1]
        })

        return cos_words_df

    def cosFromVec(self, df, myvec):
        """Finds cosine similarity of words in df to myvec

        Args:
            df (pandas.DataFrame): DataFrame of words and their vectors
            myvec (np.array): vector to find similarity of

        Returns:
            pandas.DataFrame: words in df and their cosine similarity to myvec
        """
        words = df.index
        cos_words = list()
        for i in range(len(df)):
            # acquire the vector representation of the word
            vec = array(df.iloc[i])
            # calculate the cosine similarity
            cos_sim = self.cosine(myvec, vec)
            # append the cosine similarity of the word and the word siteself to the list
            cos_words.append([cos_sim, words[i]])

        # Transform the sorted_cos_words list to put it in the dataframe
        sorted_cos_words = sorted(cos_words)
        sorted_cos_words.reverse()
        sorted_cos_words = np.array(sorted_cos_words)
        sorted_cos_words = np.transpose(sorted_cos_words)
        # Create the dataframe
        cos_words_df = pd.DataFrame({
            'Cosine Similarity' :sorted_cos_words[0],
            'Word'              :sorted_cos_words[1]
        })

        return cos_words_df