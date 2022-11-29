import json
import requests
import threading
import pandas as pd
import numpy as np
from time import sleep

thread_local = threading.local()


def get_session():
    """
    This function will create a thread_local session. It will check if the thread_local has the
    attribute session. If yes, won't do anything otherwise create it.
    :return:
    """
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.session()
    return thread_local.session


def locationiq_api(address_: str) -> list:
    address_ = address_.replace('(', '')
    address_ = address_.replace(')', '')
    address_ = address_ + ',Portugal'
    url = "https://eu1.locationiq.com/v1/search?key=TOKEN-GOES-HERE&q=" + address_ + "&format=json"
    session = get_session()
    with session.get(url) as response:
        data = json.loads(response.text)
    sleep(0.55)
    # lat = data[0]['lat']
    # long = data[0]['lon']

    try:
        coordinate = [data[0]['lat'], data[0]['lon']]
    except (KeyError, TypeError):
        coordinate = [np.nan, np.nan]
    # print(lat, long)
    return coordinate


def positionstack_api(address_: str) -> list:
    """
    Function to receive city, or address and return geo coordinates
    :param address_: string with address or city
    :return: list with geo coordinates
    """
    address_ = address_.replace('(', '')
    address_ = address_.replace(')', '')
    key = '?access_key=' + 'YOUR-TOKEN-GOES-HERE'
    base_url = 'http://api.positionstack.com/v1/forward'
    query = '&query=' + address_ + ', Portugal'
    full = base_url + key + query
    session = get_session()
    with session.get(full) as response:
        data = json.loads(response.text)

    try:
        coordinate = [data['data'][0]['latitude'], data['data'][0]['longitude']]
    except (KeyError, TypeError):
        coordinate = [np.nan, np.nan]

    return coordinate


if __name__ == '__main__':

    dataframe = pd.read_csv('imovirtual_df_no_outliers.csv')
    dataframe = dataframe.head(20)
    # print(dataframe['Address'])

    for address in dataframe['Address']:
        # print(positionstack_api(address))
        print(locationiq_api(address), address)

    #  Águas Santas, Maia, Porto
    #print(locationiq_api('Águas Santas, Maia, Porto'))
    #print(locationiq_api(dataframe['Address'][10]))
    """
    locationiq_api('rua santa cruz (Albergaria-a-Velha) Portugal')
    """
