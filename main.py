import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pandas as pd
from multiprocessing import Pool, cpu_count
import tqdm
from get_lists import get_lists
import tkinter
from tkinter import ttk

inp = None

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,\
    image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
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
    df.to_excel(f'{selection_name}.xlsx')


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
    try:
        os.mkdir(f'save_image//{url[45:]}')
    except OSError:
        pass
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    image_adv = soup.find_all(attrs={'class': 'msgpost-img'})
    for image_link in image_adv:
        img = image_link.get('src')
        try:
            req = requests.get(img)
            with open(f'save_image//{url[45:]}//{img[60:]}', 'wb') as fd:
                for chunk in req.iter_content():
                    fd.write(chunk)
        except Exception:
            pass


def main():
    start = datetime.now()
    url = get_lists()[1][get_lists()[0].index(inp)]
    count = get_lists()[2][get_lists()[0].index(inp)]
    get_data(url, inp, count)
    os.mkdir('save_image')
    print('Парсим изображения, ожидайте...')
    with Pool(processes=(cpu_count() * 2)) as p:
        for progress in tqdm.tqdm(p.imap_unordered(get_image, creat_list_links(url, count)),
                        total=len(creat_list_links(url, count))):
            pass
    os.rename('save_image', f'{inp}')
    print(f'Раздел обработан за {datetime.now() - start}')


if __name__ == '__main__':
    root = tkinter.Tk()
    root.geometry('260x300+700+300')

    selections = [key for key in get_lists()[3]]

    root.title("Парсер барахолки онлайнера")
    root.iconbitmap('logo.ico')

    ttk.Label(text='Выберите раздел').grid(row=1, column=1, columnspan=2, padx=80, pady=5, sticky='w')
    ttk.Label(text='Выберите подраздел').grid(row=3, column=1, columnspan=2, padx=80, pady=5, sticky='w')

    menu_selections = ttk.Combobox(root, width=37, value=selections)
    menu_selections.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky='w')


    def callback(event):
        abc = event.widget.get()
        selection = menu_selections.get()
        menu_subselections.config(values=get_lists()[3][selection])


    menu_subselections = ttk.Combobox(root, width=37)
    menu_subselections.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky='w')
    menu_subselections.bind('<Button-1>', callback)


    def press(event):
        global inp
        inp = menu_subselections.get()
        main()


    button = ttk.Button(root, text='Парсить')
    button.grid(row=5, column=1, columnspan=2, padx=90, pady=20, sticky='w')
    button.bind('<Button-1>', press)

    root.mainloop()
