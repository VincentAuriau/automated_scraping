"""

Input : CSV file with two columns : UEN, URL
URL is a url of the website of the company which uen is UEN and with a high probability of having project(s) on this
webpage

Output : Depending the cases, the script returns two lists:
-One with Webpages that describe each only ONE PROJECT
-One with Webpages with a list of several projects (& we cannot click on these projects/get more info about them)
Plus it gives the uen of the company associated

Summary:

Basically the idea is that we can split projects webpages into two categories :
-One with pages with only one project on it
In this case we now that all the information we can get on the webpage is related to this project and thus it is possible
to create a scritp that will get this information automatically
-One with pages that have a list of projects (and this list cannot lead to pages of the forst category)
In this case we now that the information is a list or a table and thus when we treat the information automatically
we have to take car of how everything is related in order not to mix the different projects information

This script uses the way webpages urls are written and html classes to provide these two lists


"""

import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import tqdm
import requests
from collections import Counter
import copy


url_to_check_manually = []

# Class names that contain unuseful information
list_html_classes_removed = ["top_bar", "navbar", "menu", "footer_top", "footer", "nav_holder", "bottom",
                             "banner", "header", "headroom"]


def urls_in_url(url):
    """Return all URLs available on a webpage when given an URL"""
    global url_to_check_manually
    try:
        """Return all URLs when given an url"""
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read(), "lxml")
        list_url = []
        for link in bsObj.find_all('a'):
            sublink = link.get('href')
            try:
                list_url.append(str(sublink))
            except:
                pass
        return list_url
    except:
        print('Impossible to open URL :', url)
        url_to_check_manually.append(url)
        return []


def split1_urls_in_url(url):
    """Return 2 lists: one containing URLs composed by the given URL and the other one containing all other URLs"""
    list_url = urls_in_url(url)
    list_good_url = []
    list_bad_url = []
    for sublink in list_url:
        if url in sublink[: -1] and ".jpg" not in sublink and sublink not in list_good_url and "page" not in sublink \
                and sublink[: -2] not in url:
            list_good_url.append(str(sublink))
        elif ".jpg" not in sublink and sublink not in list_bad_url:
            list_bad_url.append(sublink)
    return [list_good_url, list_bad_url]


def loop_on_good_url(url):
    """Allows to repeat split1 function until getting the last URL containing the project
    ex: use split1 on www.projects.com then on www.projects/electrical then on www.projects/electrical/Théo_project"""
    list_final = []
    list_good = split1_urls_in_url(url)[0]
    if len(list_good) > 0:
        for elt_elt in list_good:
            if elt_elt not in list_final:
                list_to_add = loop_on_good_url(elt_elt)
                for element in list_to_add:
                    if element not in list_final:
                        list_final.append(element)
        return list_final
    else:
        return [url]


def split2_urls_in_url(url):
    """Returns a string and a list.
    The string refers to how the list has been found
    The list contains either URLs containing one project each or containing many projects that are not clickable"""
    list_good = split1_urls_in_url(url)[0]
    if len(list_good) > 1:
        list_to_return = []
        for elt in list_good:
            list_to_return += loop_on_good_url(elt)
        return "Directyl found", list_to_return
    else:
        return class_frequencies(url)


url_df = pd.read_csv('results.csv', delimiter=';')


def class_frequencies(url):
    """Returns a list of URLs containing projects, one project/URL or a list of projects that are not clickable
    This function uses classes in HTML code to get the ending URLs"""
    links_list_list = []
    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.content, "lxml")
        classes = []
        for element in soup.find_all(class_=True):
            list_class = element.get("class")
            classe = ""
            for elt in list_class:
                classe += elt + " "
            classe = classe[: -1]
            classes.append(classe)
        # print("Class:", classes, ":", len(classes))
        dict_frequencies = Counter(classes)
        list_frequencies = list(dict_frequencies.values())
        list_frequencies = list(set(list_frequencies))
        list_frequencies = sorted(list_frequencies, reverse=True)
        # list_frequencies = list_frequencies[: 5]
        # print("List frequency:", list_frequencies)
        for classe in dict_frequencies.keys():
            if dict_frequencies[classe] in list_frequencies and dict_frequencies[classe] > 2:
                # print("Classes:", classe, "|", dict_frequencies[classe])
                is_project_class = True
                for classes_removed in list_html_classes_removed:
                    if classes_removed in classe:
                        is_project_class = False
                links_projects_list = []
                soup2 = soup.find_all(class_=classe)
                for i in soup2:
                    linl = i.find('a', href=True)
                    links_projects_list.append(linl)
                    if linl is None:
                        is_project_class = False

                if is_project_class:
                    for i in range(len(links_projects_list)):
                        links_projects_list[i] = links_projects_list[i].get('href')
                    # print('Projects Links Found : ', links_projects_list)
                    links_list_list += [links_projects_list]
        b_set = set(map(tuple, links_list_list))
        list_unique_lists = list(map(list, b_set))
        domain = url.replace('http://', '')
        domain = domain.replace('https://', '')
        ndx = domain.find('/')
        domain = domain[: ndx]
        # print("b:", list_unique_lists, "| domain:", domain)
        count_good = 0
        list_good_list = []
        for list_urls_possibles in list_unique_lists:
            is_a_good_list = True
            for i, url_possible in enumerate(list_urls_possibles):
                if url_possible[: 4] == "http":
                    if domain not in url_possible[: -2] or ".jpg" in url_possible or url_possible[: -2] in url:
                        is_a_good_list = False
                else:
                    new_url_possible = domain + "/" + url_possible
                    if ".jpg" in new_url_possible or new_url_possible[: -2] in url:
                        is_a_good_list = False
                    else:
                        list_urls_possibles[i] = new_url_possible
            if is_a_good_list:
                count_good += 1
                list_good_list.append(list_urls_possibles)
                # print(list_urls_possibles)
        # print(count_good)
        if count_good > 0:
            return "Found by class", from_lists_to_list(list_good_list)
        else:
            url_test = url + "/"
            index_projects = url_test.find("projects")
            index_slash = url_test.find("/", index_projects)
            if len(url) > index_slash + 2:
                return "Direct project", [url]
            else:
                return "List of non clickable projects", [url]
    except requests.exceptions.ConnectionError:
        print("Error requests:", url)
        return "Nothing", []


def from_lists_to_list(lists):
    """Returns a list of URLs
    Get a list of lists of URLs following some rules
    ex: [[a,b,c,d, index.php,d,f,p,l], [b,c,d,a,k,l], [w,x,v], [a,z,e,r,t,y,u]]
    return [w,x,v, a,z,e,r,t,y,u]
    """
    new_lists = copy.deepcopy(lists)
    list_final = []
    for url_str in lists[-1]:
        if "index.php" in url_str or "javascript" in url_str:
            new_lists.remove(lists[-1])
    for j in range(len(lists) - 1):
        if lists[j] in new_lists:
            for i in range(j + 1, len(lists)):
                for k in range(len(lists[j])):
                    if "index.php" in lists[j][k] or "javascript" in str(lists[j][k]):
                        try:
                            new_lists.remove((lists[j]))
                        except ValueError:
                            pass
                    elif lists[j][k] in lists[i]:
                        if len(lists[i]) > len(lists[j]):
                            try:
                                new_lists.remove(lists[j])
                            except ValueError:
                                pass
                        elif len(lists[i]) < len(lists[j]):
                            try:
                                new_lists.remove(lists[i])
                            except ValueError:
                                pass
    for mini_list in new_lists:
        list_final.extend(mini_list)
    return list_final


def get_all_slash_indices(url):
    """Returns a list of slashes indices in a string"""
    list_slash_indices = []
    slash_ndx = 0
    while slash_ndx != -1:
        slash_ndx = url.find('/', slash_ndx + 1)
        if slash_ndx != -1:
            list_slash_indices.append(slash_ndx)
    return list_slash_indices



url_list = []

# counter_url_with_projects = 0
# list_project_url = []
# list_unclickable_projects = []
# for line in tqdm.tqdm(range(100)):
#     uen = url_df['UEN'][line]
#     url = url_df['WWW'][line]
#     url_list = []
#     if ('projects' in url or "portfolio" in url) and url not in url_list and ".jpg" not in url:
#         counter_url_with_projects += 1
#         # print("------------------------------------------------")
#         # print("\n", url, "\n")
#         response = split2_urls_in_url(url)
#         if "non clickable" in response[0]:
#             list_unclickable_projects.extend(response[1])
#         elif response[1] != []:
#             list_project_url.extend(response[1])

# print("\n\n-------------------------------- FINAL RESULT --------------------------------\n")
# print(counter_url_with_projects, "URLs used from Romain file")
# print(len(list_project_url), "Direct URLs found :", list_project_url)
# print(len(list_unclickable_projects), "URL with list of projects :", list_unclickable_projects)

# list_final_projects_results = split2_urls_in_url("http://3pa.sg/commercial-projects.php")
# print(list_final_projects_results)

# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ "project" -----------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

counter_list_projet = 0
""" Core of the script
Get the UEN of the company and the URL associated
Then separates the different cases highlighted in the summary in the beginning and calls the needed fucntions
"""
for line in range(len(url_df)):
    uen = url_df['UEN'][line]
    url = url_df['WWW'][line]
    url_list = []
    # url = 'http://ardex.com.sg/project-references/by-product/tile-stone-installation/noosa-springs-day-spa-case-study-australia/'
    if "project" in url and "projects" not in url and '.jpg' not in url:
        if url[-1] != '/':
            url += '/'
        counter_list_projet += 1
        project_index = url.rfind('project')
        list_slash_indexes = get_all_slash_indices(url)
        left_slash_index = 0
        right_slash_index = list_slash_indexes[-1]
        number_slashes_right_of_project = 1
        for rank, slash_ndx in enumerate(list_slash_indexes):
            if slash_ndx - project_index < 0:
                left_slash_index = slash_ndx
            elif slash_ndx < right_slash_index:
                right_slash_index = slash_ndx
                # Get the number of slashes at the right of the last word project in the url
                number_slashes_right_of_project = len(list_slash_indexes) - rank
        # print(url, left_slash_index, right_slash_index, number_slashes_right_of_project)
        if right_slash_index - left_slash_index == 8: # Check if project is the last word of the url
            if right_slash_index == list_slash_indexes[-1]:
                # print('HOP', url)
                # print(split1_urls_in_url(url))
                pass
        elif right_slash_index == list_slash_indexes[-1]: #check if the project is in the last word of the url (e.g. projects)
            # print('OPTION 2 :', url)
            result_split1 = split1_urls_in_url(url)
            # print(result_split1)
            if len(result_split1[0]) > 1:
                print(url, split2_urls_in_url(url))
        else:
            pass

# print(counter_list_projet)
#
# print(get_all_slash_indices('http://brkintl.com/project-management/'))
