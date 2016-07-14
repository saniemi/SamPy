"""

A simple script to create a new database based on the CSV dumps
and the SQLite conversions. To former is used for data while the
latter is used for the schema.


Requirements
------------

:requires:


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 13-Jul-2016
"""
import sqlite3, io
import glob as g


def findFiles(location):
    """

    :param location:
    :return:
    """
    files = g.glob(location + '*.csv')
    return files


def populateTable(filename, outdb='/Users/saminiemi/Projects/myNHS/data/myNHS.db',
                  debugging=True):
    """

    :param filename:
    :param outdb:
    :param debugging:
    :return:
    """
    # infer table name
    table = filename.split('/')[-1].replace('.csv', '')
    print('\nCreating Table %s' % table)

    # find schema
    con = sqlite3.connect('/Users/saminiemi/Projects/myNHS/data/schema/NHSchoices.db')
    cur = con.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE tbl_name='%s' COLLATE NOCASE;" % table)
    schema = cur.fetchone()
    if schema is None:
        con = sqlite3.connect('/Users/saminiemi/Projects/myNHS/data/schema/NHSindicators.db')
        cur = con.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE tbl_name='%s' COLLATE NOCASE;" % table)
        schema = cur.fetchone()
    con.commit()
    con.close()

    #print(schema)

    # open connection to the new database
    con = sqlite3.connect(outdb)
    cur = con.cursor()
    cur.execute(schema[0])

    #  get the number of columns
    columnsQuery = "PRAGMA table_info(%s)" % table
    cur.execute(columnsQuery)
    tmp = cur.fetchall()
    numberOfColumns = len(tmp)

    # read in the CSV data
    try:
        file = io.open(filename, 'r', encoding='utf-16')
        data = [line.strip().split('|') for line in file.readlines()]
    except:
        file = io.open(filename, 'r', encoding='utf-8')
        data = [line.strip().split('|') for line in file.readlines()]

    print('inserting CSV data...')
    cols = '(' + ('?,' * numberOfColumns)[:-1] + ')'
    sqlstring = "INSERT INTO %s VALUES" % table + cols
    #print(sqlstring)

    if debugging:
        verbose = True
        for line in data:
            if len(line) == numberOfColumns:
                con.execute(sqlstring, line)
            else:
                if verbose:
                    print('Cannot Insert:', line)
                verbose = False
    else:
        con.executemany(sqlstring, data)

    con.commit()
    con.close()
    print('Done')


if __name__ == "__main__":
    csvs = findFiles('/Users/saminiemi/Projects/myNHS/data/csv/')

    for file in csvs:
        populateTable(file)

