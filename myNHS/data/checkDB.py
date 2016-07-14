"""

A simple script to check the content of the SQLite databases against
the CSV file dumps from the MS SQL database.


Requirements
------------

:requires: pandas
:requires: NumPy


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 13-Jul-2016
"""
import pandas as pd
import numpy as np
import sqlite3, io
import glob as g


def queryDB(location, sql):
    """

    :param location:
    :param sql:
    :return:
    """
    con = sqlite3.connect(location)
    cur = con.cursor()

    cur.execute(sql)
    data = np.asarray(cur.fetchall())

    con.close()

    return data


def readFile(filename):
    """

    :param filename:
    :return:
    """
    #df = pd.read_csv(filename, sep='|', encoding='utf-16', header=None)
    # slow but more secure...
    file = io.open(filename, 'r', encoding='utf-16')
    data = np.asarray([line.strip().split('|') for line in file.readlines()])


    return data


def findAllCSVFiles(location):
    """

    :param location:
    :return:
    """
    files = g.glob(location + '*.csv')
    return files


if __name__ == "__main__":
    csvs = findAllCSVFiles('/Users/saminiemi/Projects/myNHS/data/csv/')

    for file in csvs:
        print('\n\nChecking file %s...' % file)
        print('\t\tReading in the CSV')
        CSVdata = readFile(file)

        tmp = file.split('/')[-1].replace('.csv', '')
        print('\t\tQuerying the SQLite DB table %s' % tmp)
        sql = 'select * from %s' % tmp
        try:
            DBdata = queryDB('/Users/saminiemi/Projects/myNHS/data/schema/NHSchoices.db', sql)
        except:
            try:
                DBdata = queryDB('/Users/saminiemi/Projects/myNHS/data/schema/NHSindicators.db', sql)
            except:
                print('Cannot find or read the table')
                continue

        print('\t\tTesting that the same number of rows and columns...')
        try:
            np.testing.assert_array_equal(CSVdata.shape, DBdata.shape)
        except:
            print('!!!ERROR!!')

        #print('\t\tComparing the two datasets:')
        #np.testing.assert_almost_equal(CSVdata, DBdata)