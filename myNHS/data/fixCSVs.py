import io


def fixConsultant(filename='/Users/saminiemi/Projects/myNHS/data/csv/Consultant.csv'):
    """
    If line does not have the same number of columns as the first line, then assume
    that unwanted line break has taken place and join with the previous line.

    .. Warning:: may not be a perfect fix.

    :param filename: name of the input file

    :return: None
    """
    out = open(filename.replace('.csv', 'FIXED.csv'), 'w')
    file = io.open(filename, 'r', encoding='utf-16')

    f = file.readline()
    first = f.strip().split('|')
    out.write(f)
    ncols = len(first)

    data = []
    t = []
    for line in file.readlines():
        tmp = line.strip().split('|')
        if len(tmp) != ncols:
            t += tmp
        else:
            if len(t) == ncols:
                print(t)
                data.append(t)

            data.append(line)
            t = []

    for line in data:
        out.write(line)
    out.close()


def fixIndicator(filename='/Users/saminiemi/Projects/myNHS/data/csv/Indicator.csv'):
    """
    Same fix as for the consultant table, see the function above.

    :param filename:
    :return:
    """
    out = open(filename.replace('.csv', 'FIXED.csv'), 'w')
    file = io.open(filename, 'r', encoding='utf-16')

    f = file.readline()
    first = f.strip().split('|')
    out.write(f)
    ncols = len(first)

    data = []
    t = []
    for line in file.readlines():
        tmp = line.strip().split('|')
        if len(tmp) != ncols:
            t += tmp
        else:
            if len(t) == ncols:
                print(t)
                data.append(t)

            data.append(line)
            t = []

    for line in data:
        out.write(line)
    out.close()


def fixOrganisation(filename='/Users/saminiemi/Projects/myNHS/data/csv/Organisation.csv'):
    """
    Same fix as for the consultant table, see the function above.

    :param filename:
    :return:
    """
    out = open(filename.replace('.csv', 'FIXED.csv'), 'w')
    file = io.open(filename, 'r', encoding='utf-16')

    f = file.readline()
    first = f.strip().split('|')
    out.write(f)
    ncols = len(first)

    data = []
    t = []
    for line in file.readlines():
        tmp = line.strip().split('|')
        if len(tmp) != ncols:
            t += tmp
        else:
            if len(t) == ncols:
                print(t)
                data.append(t)

            data.append(line)
            t = []

    for line in data:
        out.write(line)
    out.close()


if __name__ == "__main__":
    #fixConsultant()
    #fixIndicator()
    fixOrganisation()