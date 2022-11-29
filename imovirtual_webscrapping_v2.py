# Import Libraries necessary

import concurrent.futures
import threading
import pandas as pd
from bs4 import BeautifulSoup
import requests
import external_functions
from older.imovirtual_webscraping import house_dictionary
import re

# thread instance to manage thread_local data. We'll have several IO tasks simultaneously.
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


def url_list() -> list:
    """
    Function to fetch the number of pages in the website and create a list of urls based on that number.
    :return list_urls: list with "create" urls according to the number of pages
    """
    url_main = 'https://www.imovirtual.com/arrendar/apartamento/'
    req1 = requests.get(url_main)
    imo1 = BeautifulSoup(req1.text, 'html.parser')
    # getting the number of pages
    number_pages = int(
        imo1.find_all('div', {'class': 'listing'})[0].find_all('ul', {'class': 'pager'})[0].find_all('li')[-2].string)

    # temporary reduce the number of pages (delete!!!!)
    # number_pages = 4

    list_urls = []
    # general structure of website url
    url_page = 'https://www.imovirtual.com/arrendar/apartamento/?page='  # + number of the page
    for page in range(2, number_pages):
        url = url_page + str(page)
        list_urls.append(url)

    return list_urls


def imovirtual_scrap(url) -> list:
    """
    This function is responsible to get the html structure of the website.
    find_all we'll return a list
    :param url: each url from the
    :return: the content of the div - class 'listing' from each website page.
    """
    # find listing tags for each page
    session = get_session()
    with session.get(url) as response:
        content = BeautifulSoup(response.content, 'html.parser')
        listing = content.find_all('div', {'class': 'listing'})
    # print(len(listing))
    return listing


def imovirtual(urls: list, max_worker: int) -> list:
    """
    This function is responsible for making a pool of threads execute call asynchronously.
    :param urls: list with several urls
    :param max_worker: number of threads to be created
    :return: a list of with the content.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker) as executor:
        listing_list = list(executor.map(imovirtual_scrap, urls))
    return listing_list


def coordinates(address: list, max_worker: int) -> list:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker) as executor:
        # list_coordinates = list(executor.map(external_functions.positionstack_api, address))
        list_coordinates = list(executor.map(external_functions.locationiq_api, address))
    # print(list_coordinates)
    return list_coordinates


def imovirtual_articles(listings) -> list:
    """
    Receive a list with all the elements withing the several lists in the website
    :param listings:
    :return: articles: list with all the articles (houses) from the website
    """
    articles = []
    for list_ in listings:
        articles.extend(list_[0].find_all('article'))
    # len(listing[1].find_all('article'))
    # len(articles)
    return articles


def house_dictionary(articles: list) -> dict:
    """
    Function to read each column from each article and associate the information to each dictionary key and append
        each value to a list
    :param articles:
    :return: house_dict
    """
    house_dict = {'title': [], 'area': [], 'typology': [], 'price': [],
                  'Energy Efficiency': [], 'address': [],
                  'Bathrooms': [], 'website': [], 'Latitude': [], 'Longitude': []}
    count = 0
    for article in articles:
        title = article.find('span', {'class': 'offer-item-title'}).string
        area = article.find(class_='offer-item-area').string
        price = str(article.find('li', class_='offer-item-price').string).replace(' ', '').replace('\n', '')
        typology = article.find(class_='offer-item-rooms').string

        # bathroom
        for lis_ in article.find_all('li'):
            if re.search('^Casas', lis_.text):
                bathroom = re.findall('[0-9]', lis_.text)[0]
            else:
                bathroom = 'nan'
        house_dict['Bathrooms'].append(bathroom)

        # energy
        try:
            energy = article.find('div', {'class': 'energy-certify -c'}).string
        except:
            energy = 'nan'
        if len(energy.split()) == 0:
            house_dict['Energy Efficiency'].append('nan')
        else:
            house_dict['Energy Efficiency'].append(energy)

        # address
        address_ = article.find('p', {'class': 'text-nowrap'})
        count = 0
        for address in address_.stripped_strings:
            if count > 0:
                address_f = address
            count += 1
        if len(address.split()) == 0:
            house_dict['address'].append('nan')
        else:
            house_dict['address'].append(address_f)
        """
        # coordinates
        if len(address.split()) == 0:
            house_dict['coordinates'].append([0,0])
        else:
            try:
                coordinates = external_functions.positionstack_api(address_f)
                house_dict['coordinates'].append(coordinates)
            except:
                house_dict['coordinates'].append([0, 0])
        """
        # typology
        if len(typology.split()) == 0:
            house_dict['typology'].append('nan')
        else:
            house_dict['typology'].append(typology)
        # Title
        if len(title.split()) == 0:
            house_dict['title'].append('nan')
        else:
            house_dict['title'].append(title)
        # area
        if len(area.split()) == 0:
            house_dict['area'].append('nan')
        else:
            house_dict['area'].append(area)
        # price
        if len(price.split()) == 0:
            house_dict['price'].append('nan')
        else:
            house_dict['price'].append(price)

        house_dict['website'].append(article['data-url'])
    return house_dict


def verify_structure(dataframe, col: str, structure: str):
    """
        This function will receive a dataframe, a column name and a structure to
        verify.
        If any row doesn't match that structure a 'nan' is added to that specific
        line of the columns being analyzed
        :return dataframe
    """
    for idx in dataframe.index:
        check = dataframe[col].iloc[idx]
        x = re.search(structure, check)
        if not x:
            dataframe[col].iloc[idx] = 'nan'
    return dataframe


def typology_check_(dataframe):
    typology_check = []

    for idx in dataframe.index:
        text = dataframe['title'].iloc[idx]
        x = re.findall('T[0-9]', text)
        if len(x) != 0:
            typology_check.append(x[0])
        else:
            typology_check.append('nan')

    # change the order of the columns
    new_cols_order = ['title', 'area', 'price', 'typology', 'Bathrooms', 'typology_check',
                      'Energy Efficiency', 'address', 'Latitude', 'Longitude', 'website']
    # add the list above to a new column
    dataframe['typology_check'] = typology_check
    dataframe = dataframe[new_cols_order]

    return dataframe


def check_different_values_and_correct(dataframe, col1: str, col2: str, col_priority: str):
    """
      This function, receives a dataframe, and two strings with the names
      of the columns to compare.
      It check 'line' by 'line' if the values of the two columns match.
      If yes don't do anything. If they are different, they are corrected.
      col_priority - > states the correct column, or the one that takes
      preference when it comes be more valuable and is the only that is going
      to still remain on the dataframe, the other one will be removed.
      So condition col_pritority == col1 or col_priority == col2, otherwise error

      return: dataframe (corrected)
    """
    if col1 == col_priority or col2 == col_priority:
        col_stay = col_priority
        if col1 == col_priority:
            col_remove = col2
        elif col2 == col_priority:
            col_remove = col1

        list1 = list(dataframe[col1].values)
        list2 = list(dataframe[col2].values)

        no_match_idx = []
        if len(list1) != len(list2):
            print('Length of the lists doesn\'t match')
        else:
            for idx in range(len(list1)):
                if list1[idx] != list2[idx]:
                    no_match_idx.append(idx)

        for idx in no_match_idx:
            if dataframe[col_stay].iloc[idx] == 'nan' and dataframe[col_remove].iloc[idx] != 'nan':
                dataframe[col_stay].iloc[idx] = dataframe[col_remove].iloc[idx]

        dataframe.drop(col_remove, axis=1, inplace=True)

        return dataframe
    else:
        print('Error: no matching columns')


# Preprocessing data
# 1 - Price column
def convert_price_to_float(dataframe):
    # ------------- 1 step ---------------------------------
    # ------------- convert Area ---------------------------
    # step to remove the m²
    dataframe['Area (m²)'] = dataframe['Area (m²)'].str.replace('m²', '')
    # in order to be able to convert string to float, we have to change the ',' with '.'
    dataframe['Area (m²)'] = dataframe['Area (m²)'].str.replace(',', '.')
    dataframe['Area (m²)'] = dataframe['Area (m²)'].str.replace(' ', '')
    # convert to float
    dataframe['Area (m²)'] = dataframe['Area (m²)'].astype('float')

    # ------------- convert Price ---------------------------
    # step to remove €/mês
    dataframe['Price (€/month)'] = dataframe['Price (€/month)'].str.replace('€/mês', '')
    # convert to float
    dataframe['Price (€/month)'] = dataframe['Price (€/month)'].astype('float')

    # ------------- convert Bathrooms ---------------------------
    dataframe['Bathrooms'] = dataframe['Bathrooms'].str.replace(' ', '')
    dataframe['Bathrooms'] = dataframe['Bathrooms'].astype('int', errors='ignore')

    # imovirtual_df
    return dataframe


# 2 - split address and create a new colum city
def split_address_to_city(dataframe):
    # we'll create a series, where each row will be a list from the split operation
    addresses = dataframe['Address'].str.split(',')
    # after we'll add the city element to a new dictionary with key 'City' with a list
    city = {'City': []}
    for address in addresses:
        city['City'].append(address[-1])

    city_df = pd.DataFrame.from_dict(city)

    # now we'll add this dict to the existing dataframe - imovirtual_df
    dataframe = pd.concat([dataframe, city_df], axis=1)
    del city_df
    return dataframe


def outlier_iqr(dataframe, col: str):
    """
    Function to detect outliers in the dataframe according to the column selected
    :param dataframe:
    :param col:
    :return:
    """
    Q1 = dataframe[col].quantile(0.25)
    Q3 = dataframe[col].quantile(0.75)
    #IQR = Q3 - Q1
    IQR = Q3 - Q1
    #print(Q1, Q3, IQR)
    #outlier = dataframe.loc[(dataframe[col]<(Q1 - 1.5*IQR) or dataframe[col] > (Q3 + 1.5*IQR))]
    #print(f'Below: {(Q1 - 1.5*IQR)} \nAbove: {(Q3 + 1.5*IQR)}')
    outliers = dataframe[((dataframe[col] < (Q1 - 1.5*IQR)) | (dataframe[col] > (Q3 + 1.5*IQR)))]

    return outliers


def main() -> pd:
    """
    Main function to define the overall sequence to retrieve, CRUD, etc
    :return: pandas DataFrame
    """

    urls = url_list()
    listings = imovirtual(urls, 10)
    articles = imovirtual_articles(listings)
    house_dict = house_dictionary(articles)

    coordinates_list = coordinates(house_dict['address'], 1)

    house_dict['Latitude'] = [coord[0] for coord in coordinates_list]
    house_dict['Longitude'] = [coord[1] for coord in coordinates_list]
    #for key in house_dict.keys():
    #    print(f'{key} - length: {len(house_dict[key])}')

    imovirtual_df = pd.DataFrame.from_dict(house_dict)

    # verify data structure
    # price column
    imovirtual_df = verify_structure(imovirtual_df, 'price', '€/mês')
    # typology column
    imovirtual_df = verify_structure(imovirtual_df, 'typology', 'T[0-9]')
    # energy efficiency column
    imovirtual_df = verify_structure(imovirtual_df, 'Energy Efficiency', '[A-G]')
    # typology check in the description
    imovirtual_df = typology_check_(imovirtual_df)
    # typology check in the description
    imovirtual_df = check_different_values_and_correct(imovirtual_df, 'typology',
                                                       'typology_check',
                                                       'typology_check')

    imovirtual_df.rename(columns={'title': 'Description', 'area': 'Area (m²)',
                                  'price': 'Price (€/month)',
                                  'typology_check': 'Typology',
                                  'address': 'Address', 'website': 'Link'}, inplace=True)

    # preprocessing steps
    imovirtual_df = convert_price_to_float(imovirtual_df)
    imovirtual_df = split_address_to_city(imovirtual_df)

    imovirtual_df.drop_duplicates(inplace=True)
    # remove outliers price and area
    imovirtual_df.drop(outlier_iqr(imovirtual_df, 'Price (€/month)').index, inplace=True)
    imovirtual_df.drop(outlier_iqr(imovirtual_df, 'Area (m²)').index, inplace=True)

    #imovirtual_df = pd.read_csv('imovirtual_df_no_outliers.csv')

    threshold = 0.40
    for column in imovirtual_df.columns:
        nulls = imovirtual_df[column].isna().sum()
        if nulls / imovirtual_df.shape[0] > threshold:
            imovirtual_df.drop(column, axis=1, inplace=True)

    imovirtual_df.dropna(inplace=True)

    return imovirtual_df


if __name__ == '__main__':
    print(main())
