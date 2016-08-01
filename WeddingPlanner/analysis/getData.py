"""

A simple script to query Google Analytics of the WeddingPlanner website.


Requirements
------------

:requires: pandas
:requires:


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 1-Aug-2016
"""
import pandas as pd
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


def get_service(api_name, api_version, scope, key_file_location, service_account_email):
    """Get a service that communicates to a Google API.

    Args:
      api_name: The name of the api to connect to.
      api_version: The api version to connect to.
      scope: A list auth scopes to authorize for the application.
      key_file_location: The path to a valid service account p12 key file.
      service_account_email: The service account email address.

    Returns:
      A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key_file_location, scopes=scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def get_first_profile_id(service):
    """
    Use the Analytics service object to get the first profile id.
    Get a list of all Google Analytics accounts for this user

    :param service:
    :return:
    """
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
            accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def _get_path(service, profile_id):
    """
    Use the Analytics Service Object to query the Core Reporting API
    for the number of sessions within the past seven days.

    :param service:
    :param profile_id:
    :return:
    """
    print('Retrieving navigation path data...')
    return service.data().ga().get(ids='ga:' + profile_id,
                                   start_date='180daysAgo',
                                   end_date='today',
                                   metrics='ga:sessions, ga:bounces',
                                   dimensions='ga:landingpagepath, ga:exitpagepath',
                                   max_results=10000).execute()


def _get_location(service, profile_id):
    """
    Use the Analytics Service Object to query the Core Reporting API
    for the number of sessions within the past seven days.

    :param service:
    :param profile_id:
    :return:
    """
    print('Retrieving location information...')
    return service.data().ga().get(ids='ga:' + profile_id,
                                   start_date='180daysAgo',
                                   end_date='yesterday',
                                   metrics='ga:sessions,ga:bounces,ga:sessionDuration,ga:bounceRate,ga:avgSessionDuration',
                                   dimensions='ga:city, ga:latitude, ga:longitude',
                                   max_results=10000).execute()


def _get_browser(service, profile_id):
    """
    Use the Analytics Service Object to query the Core Reporting API
    for the number of sessions within the past seven days.

    :param service:
    :param profile_id:
    :return:
    """
    print('Retrieving browser information...')
    return service.data().ga().get(ids='ga:' + profile_id,
                                   start_date='180daysAgo',
                                   end_date='yesterday',
                                   metrics='ga:sessions,ga:bounces,ga:sessionDuration,ga:bounceRate,ga:avgSessionDuration',
                                   dimensions='ga:browser',
                                   max_results=10000).execute()


def _get_sessions(service, profile_id):
    """
    Use the Analytics Service Object to query the Core Reporting API
    for the number of sessions within the past seven days.

    :param service:
    :param profile_id:
    :return:
    """
    print('Retrieving session information...')
    return service.data().ga().get(ids='ga:' + profile_id,
                                   start_date='1424daysAgo',
                                   end_date='yesterday',
                                   metrics='ga:sessions,ga:bounces,ga:sessionDuration,ga:bounceRate,ga:avgSessionDuration',
                                   dimensions='ga:date',
                                   max_results=10000).execute()



def _get_OS(service, profile_id):
    """
    Use the Analytics Service Object to query the Core Reporting API
    for the number of sessions within the past seven days.

    :param service:
    :param profile_id:
    :return:
    """
    print('Retrieving OS information...')
    return service.data().ga().get(ids='ga:' + profile_id,
                                   start_date='180daysAgo',
                                   end_date='yesterday',
                                   metrics='ga:sessions,ga:bounces,ga:sessionDuration,ga:bounceRate,ga:avgSessionDuration',
                                   dimensions='ga:operatingSystem',
                                   max_results=10000).execute()


def convertToPandas(data, outputstore, outputname='data'):
    """

    :param data:
    :return:
    """
    d = data['rows']
    cols = [x['name'].replace('ga:', '') for x in data['columnHeaders']]
    #types = [x['dataType'] for x in data['columnHeaders']]
    #types = [x.replace('STRING', 'string').replace('INTEGER', 'int') for x in types]

    # create dataframe
    df = pd.DataFrame(d, columns=cols)

    # convert to numeric
    #df = df.apply(pd.to_numeric, errors='ignore')

    # save to a file
    outputstore[outputname] = df

    return df


def get_data():
    """

    :return:
    """
    #define persistent HDF data store
    store = pd.HDFStore('store.h5')

    # Define the auth scopes to request
    scope = ['https://www.googleapis.com/auth/analytics.readonly']

    # Use the developer console and replace the values with your
    # service account email and relative location of your key file.
    service_account_email = 'weddingplanner@weddingplanner-1469795849595.iam.gserviceaccount.com'
    key_file_location = 'WeddingPlanner-a60a96b14c99.p12'

    # Authenticate and construct service.
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
    profile = get_first_profile_id(service)

    # get data
    path = _get_path(service, profile)
    city = _get_location(service, profile)
    browser = _get_browser(service, profile)
    os = _get_OS(service, profile)
    sessions = _get_sessions(service, profile)

    # convert to pandas and store
    city = convertToPandas(city, store, outputname='location')
    path = convertToPandas(path, store, outputname='path')
    browser = convertToPandas(browser, store, outputname='browser')
    os = convertToPandas(os, store, outputname='os')
    sessions = convertToPandas(sessions, store, outputname='sessions')

    store.close()


if __name__ == '__main__':
    get_data()