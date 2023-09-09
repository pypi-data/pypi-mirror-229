import pandas as pd
import re
from unidecode import unidecode
import treetaggerwrapper
import pkg_resources

class NLP:
    def __init__(self):
        # Initialisation de la classe NLP 
        # On charge les stopwords
        spacy_fr = pkg_resources.resource_stream(__name__, 'data/stopWords_spacy_fr.csv')
        self.stopwords_fr = pd.read_csv(spacy_fr, sep =';', encoding='latin-1')
        self.stopwords_fr = list(self.stopwords_fr['word'])
        spacy_en = pkg_resources.resource_stream(__name__, 'data/stopWords_spacy_en.csv')
        self.stopwords_en = pd.read_csv(spacy_en, sep =';', encoding='latin-1')
        self.stopwords_en = list(self.stopwords_en['word'])

    def cleanStopWord(self, text, langue = '', add_stopwords=[], remove_stopwords=[]):
        if langue == 'fr' :             
            stopwords = [
                word for word in self.stopwords_fr if word not in remove_stopwords]
        elif langue == 'en' : 
            stopwords = [
                word for word in self.stopwords_en if word not in remove_stopwords]
        else : 
            raise ValueError("Invalid langue for text.")
        stopwords.extend(add_stopwords)
        tokens = text.split(' ')
        return ' '.join([token for token in tokens if token.lower() not in stopwords])

    def lowercaseText(self, text):
        # Cette méthode permet de mettre un texte en minuscule
        return text.lower()

    def cleanText(self, text, keep_numbers=True, exception=''):
        # Cette méthode permet de nettoyer un texte en supprimant tous les caractères spéciaux, sauf ceux spécifiés dans l'argument exception
        if keep_numbers and exception:
            pattern = re.compile('[^A-Za-z0-9\xe0-\xff '+exception+']')
        elif keep_numbers:
            pattern = re.compile('[^A-Za-z0-9\xe0-\xff]')
        elif exception:
            pattern = re.compile('[^A-Za-z\xe0-\xff '+exception+']')
        else:
            pattern = re.compile('[^A-Za-z\xe0-\xff]')

        cleaned_text = pattern.sub(' ', text)
        return cleaned_text

    def cleanAccent(self, text):
        # Cette méthode permet de supprimer les accents d'un texte en les remplaçant par les lettres correspondantes sans accent
        cleaned_text = unidecode(text)
        return cleaned_text

    def lemmatisation(self, text, lemma_exclu, langue= '', keep_numbers=True, exlu_type_word=[]):
        if langue == 'fr' : 
            tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR='C:\TreeTagger')
        elif langue == 'en' : 
            tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR='C:\TreeTagger')
        else : 
            raise ValueError("Invalid langue for text.")
        tokenisation_majuscule = list()
        majuscule_tokenised = ''
        tags = tagger.tag_text(str(text), nosgmlsplit=True)
        for tag in tags:
            word, mottag, lemma = tag.split()
            if len(lemma.split('|')) > 1:
                lemma = lemma.split('|')[0]
            if word in lemma_exclu.keys():
                lemma = lemma_exclu[word]
            if keep_numbers:
                if mottag == 'NUM':
                    lemma = word
            pos = mottag.split(':')[0]
            if pos not in exlu_type_word:
                majuscule_tokenised = majuscule_tokenised + ' ' + lemma

        tokenisation_majuscule.append(majuscule_tokenised)
        return (' '.join(tokenisation_majuscule))