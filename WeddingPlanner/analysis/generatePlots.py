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

    ax = sns.barplot(y="browser", x="sessionDuration", data=df)
    plt.savefig('test1.png')
    plt.close()

    ax = sns.barplot(y="browser", x="bounceRate", data=df)
    plt.savefig('test2.png')
    plt.close()

    ax = sns.barplot(y="browser", x="avgSessionDuration", data=df)
    plt.savefig('test3.png')
    plt.close()


    # # plot correlations
    # fig, ax = plt.subplots(figsize=(10, 10))
    # sns.corrplot(df, ax=ax)
    # plt.savefig('test3.png', tight_layout=True)
    # plt.close()
    #
    # # filter browsers
    # df = df.loc[df.browser.isin(['Amazon Silk', 'Android Browser', 'Chrome', 'Edge', 'Firefox',
    #                              'Internet Explorer', 'Opera', 'Opera Mini', 'Safari', 'UC Browser',
    #                              'YE', 'YaBrowser'])]
    #
    # g = sns.FacetGrid(df, col="browser", margin_titles=True, col_wrap=4, size=4)
    # g.map(sns.distplot, "bounceRate", hist=False, rug=False, color='green')
    # plt.savefig('test1.png')
    # plt.close()
    #
    #
    # g = sns.FacetGrid(df, col="browser", margin_titles=True, col_wrap=4, size=4)
    # g.map(sns.distplot, "avgSessionDuration", hist=False, rug=False, color='green')
    # plt.savefig('test2.png')
    # plt.close()



if __name__ == '__main__':
    #browsers = getTableFromStore('browser')
    #plotBrowsers(browsers)

    sessions = getTableFromStore('sessions')
    plotSessions(sessions)