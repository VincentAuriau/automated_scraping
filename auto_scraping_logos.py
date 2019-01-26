from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request


def download_image(url, name):
    urllib.request.urlretrieve(url, name)

df_url = pd.read_csv('input.csv')
# print(df_url)
for i in range(len(df_url)):
    logo_to_download = ''
    url = df_url['website'][i]
    uen = df_url['uen'][i]

    print('URL : ', url)
    try:
        _HTTP_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36 OPR/31.0.1889.174"
        }
        request = requests.get(url, headers=_HTTP_HEADERS)
        # print('URL requested')
        soup = BeautifulSoup(request.content, 'html.parser')

        classes = []
        for element in soup.find_all(class_=True):
            list_class = element.get("class")
            classe = ""
            for elt in list_class:
                classe += elt + " "
            classe = classe[: -1]
            classes.append(classe)
        ids = []
        for element in soup.find_all(id=True):
            # print('ELEMENT ID', element)
            list_id = element.get("id")
            id = ""
            for elt in list_id:
                id += (elt + " ")
            id = id[: -1]
            ids.append(id)
        if len(ids) > 0:
            # print('IDS :', ids)
            pass

        logo_list = []
        for elt in classes:
            if 'logo' in elt:
                # print(elt)
                logo_list.append(elt)
        print(logo_list)
        print(classes)
        wrapper = ''
        for elt in logo_list:
            if 'wrap' in elt:
                wrapper = elt
        if len(logo_list) == 1:
            my_soup = soup.find_all(class_=logo_list[0])
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    print('elem2 :', elem.text)
        elif 'logo' in logo_list:
            my_soup = soup.find_all(class_='logo')
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    try:
                        print('elem :', elem['src'])
                        logo_to_download = elem.find('img')['src']
                    except:
                        print('elem2 :', elem.text)
        elif 'header-logo' in logo_list:
            my_soup = soup.find_all(class_='header-logo')
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    print('elem2 :', elem.text)
        elif 'logo-main' in logo_list:
            my_soup = soup.find_all(class_='logo-main')
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    print('elem2 :', elem.text)
        elif wrapper != '':
            my_soup = soup.find_all(class_=wrapper)
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    print('elem2 :', elem.text)
        elif len(logo_list) > 0:
            print('dans le truc')
            # for elt_log in logo_list:
            #     my_soup = soup.find_all(class_=elt_log)
            #     for elem in my_soup:
            #         try:
            #             print('elem :', elem.find('img')['src'])
            #             logo_to_download = elem.find('img')['src']
            #         except:
            #             pass
            my_soup = soup.find_all(class_=logo_list[0])
            for elem in my_soup:
                try:
                    print('elem :', elem.find('img')['src'])
                    logo_to_download = elem.find('img')['src']
                except:
                    pass
        else:
            images = []
            for img in soup.findAll('img'):
                image = img.get('src')
                try:
                    if 'logo' in image or 'Logo' in image:
                        print(image)
                        logo_to_download = image
                except TypeError:
                    pass
            # print('LINK SRC', images)
    except requests.exceptions.ConnectionError:
        pass
    print('-------------------------------------')
    if logo_to_download != '':
        if 'http' not in logo_to_download:
            domain = url.replace('http://', '')
            domain = domain.replace('https://', '')
            ndx = domain.find('/')
            domain = domain[: ndx]

            logo_to_download = url + logo_to_download
            # logo_to_download = "http://" + domain + logo_to_download

        try:
            download_image(logo_to_download, uen + '.jpeg')

        except urllib.error.HTTPError:
            print('IMPOSSIBLE TO DL :', logo_to_download)