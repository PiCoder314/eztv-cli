#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019  <@localhost>
#
# Distributed under terms of the MIT license.

""" eztv.io scraper """

def check_dependencies(exe):
    try:
        __import__(exe)
    except ImportError:
        print(f"Trying to Install required module: {exe}\n")
        os.system(f'python3 -m pip install {exe}')



# Dependency Check
check_dependencies('requests')
check_dependencies('inquirer')
check_dependencies('bs4')
check_dependencies('html5lib')
# Pip Modules
import requests
import inquirer
from bs4 import BeautifulSoup
import re
import settings
import os
import sys
# Global Variables
SEARCH_LINK = settings.SEARCH_LINK
HOME_LINK = settings.HOME_LINK
DOWNLOAD_LINK = settings.DOWNLOAD_LINK
TITLE_CLASS = settings.TITLE_CLASS
YEAR_CLASS = settings.YEAR_CLASS


def get_show(query):
    PROXIES = settings.PROXIES
    print("Getting Data...")

    try:
        response = requests.get(SEARCH_LINK.replace('{query}', query), proxies=PROXIES)
    except requests.exceptions.ProxyError:
        print('ProxyError please try again later.\nWe recommend to use a VPN.')
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print('Use the proxy flag or a VPN')
        sys.exit(1)

    html = response.text

    soup = BeautifulSoup(html, 'html5lib')
    tv_info = {}

    tags = soup.find_all(name='a',
            attrs={'class': TITLE_CLASS}
            )

    tv_info['id'] =  tuple(map(lambda x: re.search('[sS]{1}[0-9]+[eE]{1}[0-9]+|$', x.string).group(), tags))

    tv_info['quality'] =  tuple(map(lambda x: re.search('720p|360p|480p|1080p|$', x.string).group(), tags))

    tv_info['seasons'] = tuple(map(lambda x: x[1:3], tv_info['id']))

    tv_info['episodes'] = tuple(map(lambda x: x[4:6], tv_info['id']))

    shows = list()

    for i, _ in enumerate(tv_info['id']):
        shows.append({
            "id": tv_info['id'][i],
            "link": tags[i].get('href'),
            "name": tags[i].string,
            "season": tv_info['seasons'][i],
            "episode": tv_info['episodes'][i],
            "quality": tv_info['quality'][i]
            })

    shows = [show for show in shows if show['id']]
    shows = [show for show in shows if show['quality']]

    for show in shows:
        show['season'] = int(show['season'])
        show['episode'] = int(show['episode'])

    for show in shows:
        show['provider'] = show['name'][show['name'].index(show['quality'])+5:].replace('[eztv]', '')

    for show in shows:
        show['name'] = show['name'][0:show['name'].index(show['id'])-1]

    return shows


def get_downloads(link, show):
    PROXIES = settings.PROXIES

    try:
        response = requests.get(link, proxies=PROXIES)
    except requests.exceptions.ProxyError:
        print('ProxyError please try again later.\nWe recommend to use a VPN.')
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print('Use the proxy flag or a VPN')
        sys.exit(1)
    html = response.text

    soup = BeautifulSoup(html, 'html5lib')

    links = soup.find_all('a',
            attrs={
                "class": re.compile("download_[12]"),
                "title": re.compile(f".*{show['name']}.*{show['id']}.*{show['provider']}.*")
                })
    
    links = [link.get('href') for link in links]
            
    return links


def open_torrent(link):
    PROXIES = settings.PROXIES
    with open('tmp.torrent', 'wb+') as file:
        try:
            file.write(requests.get(link, proxies=PROXIES).content)
        except requests.exceptions.ProxyError:
            print('ProxyError please try again later.\nWe recommend to use a VPN.')
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print('Use the proxy flag or a VPN')
            sys.exit(1)
    os.system('settings.OPEN_COMMAND')


def main():
    print("Cant be used as a main script")


if __name__ == "__main__":
    main()
