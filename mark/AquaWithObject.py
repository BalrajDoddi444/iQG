from bs4 import BeautifulSoup as bs  
import urllib.request as url 
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string
import random
import re
import pickle
import heapq
import json
from difflib import SequenceMatcher
from textblob import TextBlob
import os
# import myfile as mf
# aqua = mf.Aqua("Artificial_intelligence")


class Aqua:
    """This is just a simple docstring. It is the first string and has a brief description about the class.
        It is not mandatory but recommended."""
    
    sample_text = ""
    
    def __init__(self,topic):
        scraped_data = url.urlopen('https://en.wikipedia.org/wiki/'+topic)  
        article = scraped_data.read()

        parsed_article = bs(article,'lxml')

        paragraphs = parsed_article.find_all('p')

        for p in paragraphs:  
            self.sample_text += p.text
            
    def getSentences(self):
        self.sample_text = re.sub(r'\[[0-9]*\]', ' ', self.sample_text)
        self.sample_text = re.sub(r'\s+', ' ', self.sample_text)
        
        self.sample_text = re.sub(r'\[[a-z]*\]', ' ', self.sample_text)
        self.sample_text = re.sub(r'\s+', ' ', self.sample_text)
        
        self.sample_text = re.sub(r".*?\{(.*?)\}", ' ', self.sample_text)
        self.sample_text = re.sub(r'\s+', ' ', self.sample_text)
        
        punc = set(string.punctuation)
#         print(punc)
#         punc.remove('.')
        sentences = []
        stop_words = stopwords.words("english")
        lemmatizer = WordNetLemmatizer()
        for sentence in sent_tokenize(self.sample_text):
            sentences.append(' '.join(word.strip() for word in word_tokenize(sentence) if not word in stop_words and word not in punc and not word.isdigit()))
#         print(sentences)
        word_frequency = {}
        for sentence in sentences:
            for word in word_tokenize(sentence):
                if word not in word_frequency.keys():
                    word_frequency[word] = 1
                else:
                    word_frequency[word] += 1
    #     print(word_frequency)
        max_frequency = max(word_frequency.values())
    #     print(max_frequency)
        for word in word_frequency.keys():
            word_frequency[word] = (word_frequency[word] / max_frequency)
#         print(word_frequency)
        sentence_score = {}
        for sentence in sent_tokenize(self.sample_text):
            for word in word_tokenize(sentence):
                if word in word_frequency.keys():
                    if len(sentence.split()) < 50:
                        if sentence not in sentence_score.keys():
                            sentence_score[sentence] = word_frequency[word]
                        else:
                            sentence_score[sentence] += word_frequency[word]
    #     print(len(sentence_score))
        
        selected_sentences = heapq.nlargest(10, sentence_score, key=sentence_score.get)
    #     print(selected_sentences)
        return selected_sentences
    def getOptions(self,word):
        # SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        # txtfile = os.path.join(SITE_ROOT, "static/extra", "nounPhrases.txt")
        # npList = pickle.load(txtfile)

        with open("nounPhrases.txt","rb") as fp:
            npList = pickle.load(fp)
    
        sim_ratio = []
        for w in npList:
            seq = SequenceMatcher(None,w,word)
            d=seq.ratio()*100
            if d not in sim_ratio:
                sim_ratio.append(d)
        sim_ratio_copy = sim_ratio.copy()
        sim_ratio_copy.sort()
        top4=sim_ratio_copy[-3:]
        options=[]
        for i in range(0,3):
            options.append(npList[sim_ratio.index(top4[i])])
        options.append(word)
        return options
            
    def getQuestion(self,s,word):
        pattern = re.compile(word,re.IGNORECASE)
        return pattern.sub("___________", s)
#         return s.replace(word, "__________")
    
    def selectWord(self,s,bucket):
#         words = None
#         if 'NNP' in bucket:
#             words = bucket['NNP']
#         elif 'NN' in bucket:
#             words = bucket['NN']
#         elif 'JJ' in bucket:
#             words = bucket['JJ']
#         else:
#             words = None
        d={
            "quiz" : []
        }
        if(len(bucket)>0):
            word = random.choice(bucket)
    #         print(word)
            options = self.getOptions(word)
            d["quiz"].append({"Question" : self.getQuestion(s, word), "Answers" : options})
#             print("Sentence: ",s,"\n")
#             print("Question: ",self.getQuestion(s, word),"\n")
#             print("Answer: ",word,"\n")
#             print("Distractors: ",options)
            y = json.dumps(d)
            print(y)
            print("-"*100,"\n")
            
    
    def processSentences(self,selected_sentences):
#         for s in selected_sentences:
#             words = nltk.word_tokenize(s)
#             tagged = nltk.pos_tag(words)
#             print("Tagged: ",tagged,"\n")
#             bucket = {}
#             for i,j in enumerate(tagged):
#                 if j[1] == 'NNP' or j[1] == 'NN' or j[1] == 'JJ':
#                     if j[1] not in bucket:
#                         bucket[j[1]] = []
#                     bucket[j[1]].append(j[0])
#             print("Bucket: ",bucket,"\n")
#             self.selectWord(s,bucket)
        d={
            "quiz" : []
        }
        for s in selected_sentences:
            blob = TextBlob(s)
#             print("Bucket of Noun Phrases: ",blob.noun_phrases,"\n")
            bucket = blob.noun_phrases
            if(len(bucket)>0):
                word = random.choice(bucket)
        #         print(word)
                options = self.getOptions(word)
                d["quiz"].append({"Question" : self.getQuestion(s, word), "Options" : options, "Answer": word})
        y = json.dumps(d)
#         print(y)
#         print("-"*100,"\n")
#         x = json.loads(y)
#         print(x)
        return y
#             self.selectWord(s,blob.noun_phrases)
            
    def finalQuestions(self):
        selected_sentences = self.getSentences()
        y=self.processSentences(selected_sentences)
        return y





