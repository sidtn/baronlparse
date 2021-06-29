import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
import openpyxl


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

def get_data():

    list_names = []
    list_links = []
    list_price = []
    list_seller = []
    list_place = []
    list_path = []

    page_count = 0
    while page_count <= 700:
        r = requests.get(url=f'https://baraholka.onliner.by/viewforum.php?f=286&cat=1&sk=up&start={page_count}', headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")

        # пасрсинг названия и ссылки объявления
        adv = soup.find_all('div', class_="txt-i")
        for link in adv:
            link_adv = link.find('a').get('href').strip('.')
            name_adv = link.find('h2', class_='wraptxt').text
            list_names.append(name_adv)
            list_links.append(f'https://baraholka.onliner.by{link_adv}')

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

        print(f'Объявлений обработано: {50 + page_count}')
        page_count += 50


    #парсим изображений
    print("Парсим изображения...")

    for link in list_links:
        try:
            os.mkdir(f'save_image//{link[45:]}')
            print(f'{list_links.index(link) + 1} объявлений из {len(list_links)} обработано')
        except:
            print('Папка уже существует')
        list_path.append(f'{os.path.abspath(os.curdir)}\save_image\{link[45:]}')
        req = requests.get(url=link, headers=headers)
        soup_i = BeautifulSoup(req.text, "html5lib")
        image_adv = soup_i.find_all(attrs={'class': 'msgpost-img'})

        count_page = 0
        for image_link in image_adv:
            img = image_link.get('src')
            try:
                req = requests.get(img)
                with open(f'save_image//{link[45:]}//{img[60:]}', 'wb') as fd:
                    for chunk in req.iter_content():
                        fd.write(chunk)
            except:
                print('Не удалось спарсить.')

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



def main():
    get_data()

if __name__ == '__main__':
    main()