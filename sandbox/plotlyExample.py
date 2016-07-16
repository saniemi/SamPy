import plotly.offline as py
import cufflinks as cf
from SamPy.myNHS.analysis import hipReplacements as nhs

def hipReplacements():
    sql = '''select
    a.OrganisationName, a.Latitude, a.Longitude,
    b.value,
    c.metricName
    from
    organisation as a,
    indicator as b,
    metric as c
    where
    a.organisationID = b.organisationID and
    b.metricID = c.metricID and
    b.metricID = 9225 and
    b.isCurrent = 1'''

    data = nhs.QueryDB(sql)

    return data


cf.go_offline()

df = hipReplacements()
df.head(3)

series = df['OrganisationName'].value_counts()[:20]
series.head(3)

series.iplot(kind='bar', yTitle='Number of Complaints', title='Hip Replacements',
             filename='cufflinks/categorical-bar-chart')

