import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pandas as pd
import openpyxl
from multiprocessing import Pool, cpu_count
import tqdm
from get_lists import list_subselection_names, list_subselection_links, list_subselection_adv_count

inp = 'Ноутбуки'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


# в этой функции парсим все строчные данные, добавляем в словарь и импортируем в exel
def get_data(url, selection_name, pages_count):

    list_names = []
    list_links = []
    list_price = []
    list_seller = []
    list_place = []
    list_path = []

    page_count = 0
    while page_count <= pages_count:
        r = requests.get(url=f'{url}{page_count}', headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")

        # пасрсинг названия и ссылки объявления
        adv = soup.find_all('div', class_="txt-i")
        for link in adv:
            link_adv = link.find('a').get('href').strip('.')
            name_adv = link.find('h2', class_='wraptxt').text
            list_names.append(name_adv)
            path_to_folser = f'https://baraholka.onliner.by{link_adv}'
            list_links.append(f'https://baraholka.onliner.by{link_adv}')
            list_path.append(f'{os.path.abspath(os.curdir)}\{selection_name}\{path_to_folser[45:]}')

        # парсинг цены
        adv_price = soup.find_all('td', class_='cost')
        for cost in adv_price:
            if cost.find('div', class_="price-primary") is not None:
                adv_cost = cost.find('div', class_="price-primary").text
            else:
                adv_cost = 'Цена не указана'
            list_price.append(adv_cost)

        # парсинг продавца
        adv_seller = soup.find_all('p', class_="ba-signature")
        for sell in adv_seller:
            seller = sell.find('a').get('href')
            place = sell.find('strong').text
            list_seller.append(seller)
            list_place.append(place)

        print(f'Объявлений обработано: {len(list_links)}')
        page_count += 50

    # создание словаря с данными
    dict_adv = {
        'Объявление': list_names,
        'Ссылка': list_links,
        'Цена': list_price,
        'Продавец': list_seller,
        'Город': list_place,
        'Папка с изображениями': list_path
    }

    # экспорт данных в exel
    df = pd.DataFrame(dict_adv)
    df.to_excel('file.xlsx')




def creat_list_links(url, pages_count):
    list_links = []
    page_count = 0
    while page_count <= pages_count:
        r = requests.get(url=f'{url}{page_count}', headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")
        adv = soup.find_all('div', class_="txt-i")
        for link in adv:
            link_adv = link.find('a').get('href').strip('.')
            list_links.append(f'https://baraholka.onliner.by{link_adv}')
        page_count += 50
    return list_links

def get_image(url):
    global inp
    try:
        os.mkdir(f'{inp}//{url[45:]}')
    except:
        pass
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    image_adv = soup.find_all(attrs={'class': 'msgpost-img'})
    for image_link in image_adv:
        img = image_link.get('src')
        try:
            req = requests.get(img)
            with open(f'{inp}//{url[45:]}//{img[60:]}', 'wb') as fd:
                for chunk in req.iter_content():
                    fd.write(chunk)
        except:
            pass


def main():
    global inp
    start = datetime.now()
    if inp in list_subselection_names:
        url = list_subselection_links[list_subselection_names.index(inp)]
        count = list_subselection_adv_count[list_subselection_names.index(inp)]
        get_data(url, inp, count)
        os.mkdir(f'{inp}')
        print("Парсим изображения...")
        p = Pool(processes=(cpu_count()*2))
        for i in tqdm.tqdm(p.imap_unordered(get_image, creat_list_links(url, count)), total=len(creat_list_links(url, count))):
            pass
    else:
        print('Раздел не существует')
        print(f'Раздел обработан за {datetime.now()-start}')



if __name__ == '__main__':
    main()