"""
Survey Analysis
===============

A simple script to do some analysis on survey data.


Dependencies
------------

:requires: pandas
:requires: numpy
:requires: matplotlib
:requires: nltk
:requires: wordcloud
:requires: rpy2


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 24-Mar-2016
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import rpy2.robjects as robjects
import string
import itertools
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
#import re
#import nltk
#from nltk.tokenize import TreebankWordTokenizer
#from nltk import word_tokenize
#from nltk.stem.snowball import SnowballStemmer
#from textblob import TextBlob


class WordCloudSMN(WordCloud):
    """
    Add a new method to the wordcloud class to bypass tokenizing.
    """
    def generate_SMN(self, wordlist):
        words = dict(Counter(wordlist).most_common()).items()
        self.generate_from_frequencies(words)
        return self


def _saveRdata2csv(filename="/Users/saminiemi/Projects/OfficeSurvey/Mikayel/surveymonkey.RData",
                   outfolder="/Users/saminiemi/Projects/OfficeSurvey/data/"):
    """
    Simple function to convert RData file to csv file(s).

    :param filename: name of the RData file
    :param outfolder: location of the output

    :return: None
    """
    data = robjects.r['load'](filename)
    for x in data:
        tmp = robjects.r[x]
        try:
            print(x)
            tmp.to_csvfile(outfolder + str(x) + '.csv')
        except:
            pass


def loadData(filename, folder="/Users/saminiemi/Projects/OfficeSurvey/data/"):
    """
    Load data from a csv file.

    :param filename: name of the csv file to load
    :param folder: location of the data

    :return: data frame
    """
    df = pd.read_csv(folder+filename)
    return df


def getWords(df, column='Response.Text', verbose=True):
    """
    Collect the words from a pandas data frame / series.
    Perform tokenizing and various manipulations.

    :param df: input data frame / series
    :param column: name of the column to stores the information
    :param verbose: whether or not to output some extra information

    :return: words
    :rtype: list
    """
    # get data and convert the series to a single string by replacing ; and & with ,
    # responses = df[column]
    # responses = ', '.join(e.lower().strip().replace(';', ',').replace('&', ',').replace('.', ',') for e in responses.tolist())
    # print(responses)
    #
    #
    # # tokenize to words
    # words = responses.split(',')
    # #words = word_tokenize(responses)
    # #words = nltk.tokenize.wordpunct_tokenize(responses)
    # #tokenizer = nltk.tokenize.mwe.MWETokenizer()
    # #words = tokenizer(responses)

    responses = df[column]
    words = []
    for response in responses:
        response = response.strip().replace('.', ',').replace('&', ',').replace(';', ',').replace('!', '').lower()

        # split based on commas
        tmp = response.split(',')

        # if length < 2, no commas, then split on "and"
        if len(tmp) < 2:
            tmp = response.split('and')

        # remove extra spaces
        tmp = [i.strip() for i in tmp]

        # remove if length less than 2
        tmp = [i for i in tmp if len(i) > 2]

        # split based on and and :
        #tmp = [i.split(';') for i in tmp]
        #tmp = list(itertools.chain(*tmp))
        #tmp = [i.split('and') for i in tmp]
        #tmp = list(itertools.chain(*tmp))

        # if length less than 2 then split using space
        #if len(tmp) < 2:
        #    tmp = response.split(' ')

        words.append(tmp)

    # convert nested lists to a single list
    words = list(itertools.chain(*words))

    # remove punctuation
    punctuations = list(string.punctuation)
    words = [i.lower() for i in words if i not in punctuations]

    # remove stop words
    stop = stopwords.words('english')
    stop.append(['looking', 'looks', 'office', 'and', 'some', 'for', 'are'])
    words = [i.strip() for i in words if i not in stop]

    # remove prefixes and numerals
    words = [i.replace(' a ', ' ').strip() for i in words]
    words = [i.replace(' an ', '').strip() for i in words]
    words = [i.replace(' the ', '').strip() for i in words]
    words = [i.replace(' one ', '').strip() for i in words]
    words = [i.replace(' two ', '').strip() for i in words]
    words = [i.replace(' it ', '').strip() for i in words]
    #words = [i.replace(' for ', '').strip() for i in words]
    words = [i.replace('plenty of', '').strip() for i in words]
    words = [i.replace('like ', '').strip() for i in words]

    # brackets
    words = [i.replace('(', '').strip() for i in words]
    words = [i.replace(')', '').strip() for i in words]

    # remove adjectives and please
    words = [i.replace('good ', '').strip() for i in words]
    words = [i.replace('decent ', '').strip() for i in words]
    words = [i.replace('nice ', '').strip() for i in words]
    words = [i.replace('big ', '').strip() for i in words]
    words = [i.replace('very ', '').strip() for i in words]
    words = [i.replace('please', '').strip() for i in words]

    # remove acronyms and extras
    words = [i.replace('def ', '').strip() for i in words]
    words = [i.replace('some ', '').strip() for i in words]

    # convert too few to lack of
    words = [i.replace('too few ', 'lack of ') for i in words]
    words = [i.replace('no ', 'lack of ') for i in words]
    words = [i.replace('a lot of ', '') for i in words]
    words = [i.replace('too much ', '') for i in words]

    # convert comfortable to comfy - these are the same
    words = [i.replace('comfortable', 'comfy') for i in words]
    words = [i.replace('bicycle', 'bike') for i in words]

    # change coffee to coffee machine
    words = [i.replace('machine', '').strip() for i in words]
    words = [i.replace('coffee', 'coffee machine').strip() for i in words]

    # change shower to showers
    words = [i.replace('showers', 'shower') for i in words]
    words = [i.replace('shower', 'showers') for i in words]

    # change wordings
    words = [i.replace('lighting', 'lights') for i in words]

    # remove if length less than 2
    words = [i for i in words if len(i) > 2]

    #stemming
    #stemmer = SnowballStemmer('english')
    #for i, word in enumerate(words):
    #    words[i] = stemmer.stem(word)

    if verbose:
        print(words)

    return words


def generateStatistics(words, outfile, title, mostcommon=12, verbose=True):
    """

    :param words: words in a list
    :param outfile: name of the output file
    :param title: title of the figure
    :param mostcommon: how many of the most common to output

    :return: None
    """
    word_counts = Counter(words)

    # save to a file
    with open(outfile.replace('.pdf', '.csv'), 'w') as f:
        for k,v in  word_counts.most_common():
            f.write("{},{}\n".format(k, v))

    if verbose:
        print("Most common words:")
        for item in word_counts.most_common(mostcommon):
            print(item)

    wc = word_counts.most_common(mostcommon)
    words = []
    counts = []
    for w, c in wc:
        words.append(w)
        counts.append(c)

    y_pos = np.arange(len(words))

    # plot statistics
    plt.figure(figsize=(12, 12))
    plt.subplots_adjust(left=0.3)
    plt.barh(y_pos[::-1], counts, align='center', alpha=0.4)
    plt.yticks(y_pos[::-1], words)
    plt.ylim(y_pos[0] - 1, y_pos[-1] + 1)
    plt.xlabel('Number of Times')
    plt.title(title)
    plt.savefig(outfile)
    plt.close()


def generateWordcloud(wordlist, outfile, title, nwords=100):
    """

    :param wordlist: words in a list
    :param outfile: name of the output file to which to store the figure
    :param title: title of the figure
    :param nwords: maximum number of words to plot

    :return: None
    """
    # generate word cloud
    wc = WordCloudSMN(background_color="white", max_words=nwords,
                      width=800, height=400,
                      stopwords=STOPWORDS.add("looking"),
                      max_font_size=80, random_state=42)
    wc.generate_SMN(wordlist)

    # generate the figure
    plt.figure(figsize=(16, 16))
    plt.title(title)
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig(outfile)
    plt.close()


def processTextFile(filename='q1.csv', title='Q1'):
    """

    :param filename: name of the data file
    :param title: title for the figures

    :return: None
    """
    data = loadData(filename=filename)
    words = getWords(data)
    generateWordcloud(words, filename.replace('.csv', 'Wordcloud.pdf'), title)
    generateStatistics(words, filename.replace('.csv', 'Histogram.pdf'), title)


def processNumericFileQ6(filename='q6.csv', title='Q6'):
    """

    :param filename: name of the input file
    :param title: title of the plot

    :return: None
    """
    data = loadData(filename=filename)
    data['sum'] = data['One'] + data['Two'] + data['Three'] + data['Four'] + data['Five']
    #data.sort(columns=['One', 'Two', 'Three', 'Four', 'Five'], ascending=False, inplace=True)
    data.sort_values(by=['sum', 'One'], ascending=False, inplace=True)
    print(data)

    x_pos = np.arange(len(data['Answer.Options'].values))

    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    plt.subplots_adjust(bottom=0.5)
    p1 = ax.bar(x_pos, data['One'], align='center',
                alpha=0.4, color='m')
    p2 = ax.bar(x_pos, data['Two'], bottom=data['One'],
                align='center', alpha=0.4, color='b')
    p3 = ax.bar(x_pos, data['Three'], bottom=(data['One'] + data['Two']), align='center',
                alpha=0.4, color='r')
    p4 = ax.bar(x_pos, data['Four'], bottom=(data['One'] + data['Two'] + data['Three']),
                align='center', alpha=0.4, color='green')
    p5 = ax.bar(x_pos, data['Five'], bottom=(data['One'] + data['Two'] + data['Three'] + data['Four']),
                align='center', alpha=0.4, color='yellow')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(data['Answer.Options'], rotation=90, ha='center')
    ax.set_title(title)
    ax.set_yticks([])
    ax.xaxis.set_ticks_position('none')
    ax.set_xlim(x_pos[0] - 1, x_pos[-1] + 1)
    plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0]), ('One', 'Two', 'Three', 'Four', 'Five'))
    plt.savefig(filename.replace('.csv', '.pdf'))
    plt.close()


def processNumericFileQ7(filename='q7.csv', title='Q7'):
    """

    :param filename: name of the input file
    :param title: title of the plot

    :return: None
    """
    data = loadData(filename=filename)
    data['sum'] = data['One'] + data['Two'] + data['Three'] + data['Four']
    data.sort_values(by=['sum', 'One'], ascending=False, inplace=True)
    print(data)

    x_pos = np.arange(len(data['Answer.Options'].values))

    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    plt.subplots_adjust(bottom=0.4)
    p1 = ax.bar(x_pos, data['One'], align='center',
                alpha=0.4, color='m')
    p2 = ax.bar(x_pos, data['Two'], bottom=data['One'],
                align='center', alpha=0.4, color='b')
    p3 = ax.bar(x_pos, data['Three'], bottom=(data['One'] + data['Two']), align='center',
                alpha=0.4, color='r')
    p4 = ax.bar(x_pos, data['Four'], bottom=(data['One'] + data['Two'] + data['Three']),
                align='center', alpha=0.4, color='green')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(data['Answer.Options'], rotation=90, ha='center')
    ax.set_title(title)
    ax.set_yticks([])
    ax.xaxis.set_ticks_position('none')
    ax.set_xlim(x_pos[0] - 1, x_pos[-1] + 1)
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('One', 'Two', 'Three', 'Four'))
    plt.savefig(filename.replace('.csv', '.pdf'))
    plt.close()


def processNumericFileQ8(filename='q8.csv', otherfile='q8_other.csv', title='Q8'):
    """

    :param filename: name of the input file
    :param title: title of the plot

    :return: None
    """
    # response data
    data = loadData(filename=filename)
    data.sort_values(by=['Response.Count'], ascending=False, inplace=True)

    # other answers
    otherdata = loadData(filename=otherfile)
    others = otherdata['If.other..please.specify.'].values

    x_pos = np.arange(len(data['Answer.Options'].values))

    # generate figure
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    plt.subplots_adjust(bottom=0.35)
    ax.bar(x_pos, data['Response.Count'], align='center', alpha=0.4, color='m')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(data['Answer.Options'], rotation=90, ha='center')
    ax.set_title(title)
    ax.set_yticks([])
    ax.xaxis.set_ticks_position('none')
    ax.set_xlim(x_pos[0] - 1, x_pos[-1] + 1)
    for i, text in enumerate(others):
        ax.annotate('Other: ' + text, xy=(20, (10 + 15*i)), xycoords='figure points')
    plt.savefig(filename.replace('.csv', '.pdf'))
    plt.close()


if __name__ == "__main__":
    _saveRdata2csv()

    processTextFile(filename='q1.csv', title='Q1 - How would you describe the office we should be designing?')
    processTextFile(filename='q2.csv', title='Q2 - Please give elements that would make you happy about coming into the office')
    processTextFile(filename='q3.csv', title='Q3 - Please give elements that would help you produce your best work at the office')
    processTextFile(filename='q4.csv', title='Q4 - Please list anything that may hinder your productivity')

    processNumericFileQ6()
    processNumericFileQ7()
    processNumericFileQ8()
