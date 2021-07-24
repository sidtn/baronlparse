import time
import requests
from bs4 import BeautifulSoup



def get_lists():

    list_subselection_names = []
    list_subselection_adv_count = []
    list_subselection_links = []
    dict_selection = {}

    url = 'https://baraholka.onliner.by/'
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
              }

    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, features='html5lib')


    data = soup.find_all('ul', class_='b-cm-list')
    for name in data:
        names_and_links = name.find_all('li')
        for names in names_and_links:
            subselection_names = names.find('a').text.strip()
            list_subselection_names.append(subselection_names)
            try:
                subselection_adv_count = names.find('sup').text.strip()
                list_subselection_adv_count.append(int(subselection_adv_count))
                subselection_links = names.find('a').get('href')
                list_subselection_links.append(f'https://baraholka.onliner.by{subselection_links.strip(".")}&sk=up&start=')
            except:
                pass

    list_subselection_names.remove('Легковые автомобили')

    data1 = soup.find_all('div', class_='cm-onecat')
    for omnecat in data1:
        selection = omnecat.find('h3').text.strip()
        bcmlist = omnecat.find_all('ul', class_='b-cm-list')
        for li in bcmlist:
            lan = li.find_all('a')
            list_1 = []
            for i in lan:
                if i.text.strip() == 'Легковые автомобили' or i.text.strip() == 'Мотоциклы':
                    continue
                else:
                    list_1.append(i.text.strip())
            dict_selection[selection] = list_1

    return list_subselection_names, list_subselection_links, list_subselection_adv_count, dict_selection

























