from bs4 import BeautifulSoup as bs #parse html into messages
from datetime import datetime as dt #organizing messages by date
from collections import Counter
from matplotlib import pyplot as plt
import os
import analyzer_functions as af #functions list of the analyzer

#very memory heavy at the moment

allMessages = bs(open(os.getcwd() + "/message.html"), "html.parser").find("div",{"class": "_4t5n"}) #extract message section of html

infoDict = {}

for message in allMessages.children:
    messageInfo = []
    af.messageParser(message, messageInfo)
    
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
    currMessage = af.removeNonWords(currMessage)

    if user not in infoDict: #if the current user is not already part of the dictionary
        infoDict[str(user)] = [word for word in currMessage] #add the user key with a list of words
    else:
        infoDict[str(user)].extend(currMessage) #extend the list of words with those of the current message
    
people = list(infoDict.keys()) #which people were in the message chain
fig, axarr = plt.subplots(1, len(people), sharey='row')
plotCount = 0

for person in people: 
    af.createWordcloud(" ".join(infoDict[person]), person, axarr, plotCount)
    plotCount += 1