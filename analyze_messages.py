from bs4 import BeautifulSoup as bs #parse html into messages
from datetime import datetime as dt #organizing messages by date
from spellchecker import SpellChecker
from collections import Counter
from matplotlib import pyplot as plt
from nltk.corpus import stopwords as sw
import re, os, string, contractions
import pandas as pd
import wordcloud

allMessages = bs(open(os.getcwd() + "/message.html"), "html.parser").find("div",{"class": "_4t5n"}) #extract message section of html

stopwords = [word.strip(' ') for word in pd.read_csv('stop-word-list.csv', delimiter=',')] #create the stopwords list from the csv file
stopwords.extend([word for word in sw.words('english') if word not in stopwords])#then extend by stop words from nltk

infoDict = {}
spell = SpellChecker() #load frequency word list

for message in allMessages.children: #run through all the messages
    messageInfo = []
    messageParser(message)
    
    try:
        user, currMessage, monthYear = messageInfo #grab which person sent the message
    except:
        #otherwise we hit the weird hyperlink errors
        if len(messageInfo) > 2:
            del messageInfo[1:len(messageInfo)-1] #we know that the first and last item will always be wanted
            messageInfo.insert(1, '')
        else:
            messageInfo.insert(1, '')

        user, currMessage, monthYear = messageInfo #grab which person sent the message
        
    year = dt.strftime(dt.strptime(monthYear,'%b %d, %Y %H:%M%p'),'%Y')
    currMessage = removeNonWords(currMessage)

    if user not in infoDict: #if the current user is not already part of the dictionary
        infoDict[str(user)] = [word for word in currMessage] #add the user key with a list of words
    else:
        infoDict[str(user)].extend(currMessage) #extend the list of words with those of the current message
    

#plot into a word cloud
createWordcloud(" ".join(infoDict['Tommy Botch']))
createWordcloud(" ".join(infoDict['Natalie Blair']))
        

def messageParser(currMessage):
    for message in currMessage.children: #call recursively until string is reached
        if message.div is None: #then we have reached the string
            if message.string is not None:
                #checking if string in list to avoid facebooks preview window of links
                messageInfo.append(str(message.string))
            else:
                pass
        else:
            messageParser(message)

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

def createWordcloud(wordlist):
    cloud = WordCloud(normalize_plurals=True).generate(wordlist)
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis('off')
    
    