from nltk.corpus import stopwords as sw
from spellchecker import SpellChecker
from collections import Counter
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import re, os, string, contractions
import pandas as pd

stopwords = [word.strip(' ') for word in pd.read_csv('stop-word-list.csv', delimiter=',')] #create the stopwords list from the csv file
stopwords.extend([word for word in sw.words('english') if word not in stopwords])#then extend by stop words from nltk

spell = SpellChecker() #load frequency word list

def messageParser(currMessage, infoList):
    for message in currMessage.children: #call recursively until string is reached
        if message.div is None: #then we have reached the string
            if message.string is not None:
                #checking if string in list to avoid facebooks preview window of links
                infoList.append(str(message.string))
            else:
                pass
        else:
            messageParser(message, infoList)

def removeNonWords(message):
    #removes emojis, urls, and other regex from message
    
    message = re.sub(r'^https?:\/\/.*[\r\n]*', '', message, flags=re.MULTILINE) #checks for url
    
    message = re.sub(r'\b(?:a*(?:ha)+h?|(?:l+o+)+l+)\b', '', message, flags=re.MULTILINE) #removes laugh patterns
    
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    

    message = emoji_pattern.sub(r'', message)
    
    message = contractions.fix(message) #expand contractions (doesn't seem to catch i'm)
    message = message.replace('i\'m', 'I am') #catch the lowercase version of i'm
    
    puncRemover = str.maketrans('', '', string.punctuation) #punctuation to remove
    numbers = str.maketrans('', '', string.digits) #numbers 0-9

    message = message.translate(puncRemover) #remove all punctuation
    message = message.translate(numbers)
    
    message = message.lower().split(" ") #split the string into separate words
    
    message = list(filter(None, message)) #then filter out empty string and turn into list
    
    message = [word for word in message if word not in stopwords]#remove stopwords 

    message = [spellCheck(word) for word in message] #lastly spell check all the words in the message

    return message

def spellCheck(word):
    repeatedLetters = re.compile(r"(.)\1{2,}") #repeated letters filter
    word = repeatedLetters.sub(r"\1", word) #remove repeated letters
    
    return spell.correction(word)

def createWordcloud(wordlist, person, plotFig, subplot):
   # cloud = WordCloud(normalize_plurals=True).generate_from_frequencies(wordlist)
    cloud = WordCloud(max_font_size=50, 
                      max_words=100, 
                      background_color="white",
                      normalize_plurals=True).generate(wordlist)
    plotFig[subplot].imshow(cloud, interpolation='bilinear')
    plotFig[subplot].set_title(person)
    plotFig[subplot].axis('off')