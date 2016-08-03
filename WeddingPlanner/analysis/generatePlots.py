"""

A simple script to visualise simple metrics for the WeddingPlanner project.


Requirements
------------

:requires: pandas
:requires: matplotlib
:requires: seaborn


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 1-Aug-2016
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_context("poster")


def getTableFromStore(table, storename='store.h5', verbose=False):
    df = pd.read_hdf(storename, table)

    if verbose:
        print(df.info())
        print(df.describe())

    return df


def plotSocialMedia(df):
    df = df.apply(pd.to_numeric, errors='ignore')
    print(df.info())

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.corrplot(df, ax=ax)
    plt.savefig('socialNetworkCorrelations.png', tight_layout=True)
    plt.close()

    # mean session duration
    df.sort_values("avgSessionDuration", ascending=False, inplace=True)
    g = sns.barplot(y='socialNetwork', x='avgSessionDuration', hue='userType', data=df)
    g.set(xlabel='Average Session Duration', ylabel='')
    plt.subplots_adjust(left=.17)
    sns.despine(left=True, bottom=True)
    plt.savefig('socialNetworkAvgDuration.png')
    plt.close()

    # bounceRate
    df.sort_values("bounceRate", inplace=True)
    g = sns.barplot(y='socialNetwork', x='bounceRate', hue='userType', data=df)
    g.set(xlabel='Bounce Rate', ylabel='')
    plt.subplots_adjust(left=.17)
    sns.despine(left=True, bottom=True)
    plt.savefig('socialNetworkBounceRate.png')
    plt.close()

    # avgTimeOnPage
    df.sort_values("avgTimeOnPage", ascending=False, inplace=True)
    g = sns.barplot(y='socialNetwork', x='avgTimeOnPage', hue='userType', data=df)
    g.set(xlabel='Average Time on Page', ylabel='')
    plt.subplots_adjust(left=.17)
    sns.despine(left=True, bottom=True)
    plt.savefig('socialNetworkavgTimeOnPage.png')
    plt.close()

    # goals completed
    df.sort_values("goalCompletionsAll", ascending=False, inplace=True)
    g = sns.barplot(y='socialNetwork', x='goalCompletionsAll', hue='userType', data=df)
    g.set(xlabel='Goal Completions', ylabel='', xscale='log')
    plt.subplots_adjust(left=.17)
    sns.despine(left=True, bottom=True)
    plt.savefig('socialNetworkgoalCompletionsAll.png')
    plt.close()


def plotSessions(df):
    cols = ['sessions', 'bounces', 'sessionDuration', 'bounceRate', 'avgSessionDuration']
    # convert to date time
    df['datetime'] = pd.to_datetime(df['date'], yearfirst=True, format='%Y%m%d')
    df['daysSince'] = (df.datetime - df.datetime.min()).astype('timedelta64[D]')
    # conver to numeric
    for tmp in cols:
        df[tmp] = df[tmp].astype(np.float64)

    since = df.datetime.min().strftime("%B %d, %Y")
    print(since)

    for y in cols:
        rm = pd.rolling_mean(df[y], 30)

        fig, ax = plt.subplots(figsize=(14, 14))
        ax.plot_date(df['datetime'], df[y], 'bo', ms=6, alpha=0.3)
        ax.plot_date(df['datetime'], rm, '-', lw=4, color='green')
        ax.set_ylabel(y)
        plt.setp(ax.get_xticklabels(), rotation=45, fontsize=20)
        plt.savefig('timeseries%s.png' % y)
        plt.close()

        fig, ax = plt.subplots(figsize=(14, 14))
        lm = sns.lmplot(x="daysSince", y=y, data=df, lowess=True, size=10, ci=95, line_kws={'color': 'green'})
        lm.set(xlabel=('Days Since %s' % since))
        lm.set(xlim=(0, df['daysSince'].max()*1.01))
        lm.set(ylim=(0, df[y].max()*1.01))
        plt.savefig('timeseriesFit%s.png' % y)
        plt.close()

    # plot correlations
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.corrplot(df[cols], ax=ax)
    plt.savefig('sessionCorrelations.png', tight_layout=True)
    plt.close()

    # only since '2014-08-01'
    msk = df['datetime'] > '2014-08-01'
    df = df.loc[msk]
    df['daysSince'] = (df.datetime - df.datetime.min()).astype('timedelta64[D]')
    since = df.datetime.min().strftime("%B %d, %Y")


    for y in cols:
        rm = pd.rolling_mean(df[y], 30)

        fig, ax = plt.subplots(figsize=(14, 14))
        ax.plot_date(df['datetime'], df[y], 'bo', ms=6, alpha=0.3)
        ax.plot_date(df['datetime'], rm, '-', lw=4, color='green')
        ax.set_ylabel(y)
        plt.setp(ax.get_xticklabels(), rotation=45, fontsize=20)
        plt.savefig('timeseriesRecent%s.png' % y)
        plt.close()

        fig, ax = plt.subplots(figsize=(14, 14))
        lm = sns.lmplot(x="daysSince", y=y, data=df, lowess=True, size=10, ci=95, line_kws={'color': 'green'})
        lm.set(xlabel=('Days Since %s' % since))
        lm.set(xlim=(0, df['daysSince'].max() * 1.01))
        lm.set(ylim=(0, df[y].max() * 1.01))
        plt.savefig('timeseriesRecentFit%s.png' % y)
        plt.close()


def plotBrowsers(df):
    df = df.apply(pd.to_numeric, errors='ignore')
    print(df.info())

    df = df.sort_values("bounceRate")
    g = sns.barplot(y="browser", x="bounceRate", data=df)
    g.set(xlabel=('Bounce Rate'))
    plt.subplots_adjust(left=.3)
    sns.despine(left=True, bottom=True)
    plt.savefig('browsers2.png')
    plt.close()

    df = df.sort_values("avgSessionDuration", ascending=False)
    g = sns.barplot(y="browser", x="avgSessionDuration", data=df)
    g.set(xlabel=('Average Session Duration [s]'))
    plt.subplots_adjust(left=.3)
    sns.despine(left=True, bottom=True)
    plt.savefig('browsers3.png')
    plt.close()


def weekdayNumbering(row, column='DayofWeekName'):
    days = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}
    for key in days:
        if row[column] == key:
            return days[key]


def plotWeekdayData(file='weekdayData.txt'):
    data = pd.read_csv(file, sep='\t', thousands=',')
    data['daynumb'] = data.apply(lambda row: weekdayNumbering(row), axis=1)
    data.sort_values(by='daynumb', inplace=True)

    #normalise the session values
    data['Sessions'] /= data['Sessions'].max()

    g = sns.barplot(x='DayofWeekName', y='Sessions', data=data)
    g.set(ylabel='Normalised Number of Sessions', xlabel='')
    plt.savefig('weekdaySessions.png')
    plt.close()

    g = sns.barplot(x='DayofWeekName', y='AvgSessionDuration', data=data)
    g.set(ylabel='Average Session Duration [s]', xlabel='')
    plt.savefig('weekdayDurations.png')
    plt.close()


if __name__ == '__main__':
    # sessions = getTableFromStore('sessions')
    # plotSessions(sessions)
    #
    # browsers = getTableFromStore('browser')
    # plotBrowsers(browsers)
    #
    # socialm = getTableFromStore('socialmedia')
    # plotSocialMedia(socialm)

    plotWeekdayData()