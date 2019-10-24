#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019  <@localhost>
#
# Distributed under terms of the MIT license.

""" eztv.io cli-client """
import re
import sys
import settings
import getopt
import scraper
import inquirer
import itertools


def main():
    try:
        args = sys.argv[1:]
        opts, args = getopt.getopt(args, 'hq:pcd', ['query=', 'use-proxy', 'use-cli'])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print('usage: ./main.py [query] [options]\noptions\n-q, --query= : movie to search for\n-p,--use-proxy : use anonymous proxy')
                sys.exit(0)
            if opt in ('-q', '--query'):
                query=arg
            if opt in ('-p', '--use-proxy'):
                settings.PROXIES = {
                        'http': 'http://35.236.147.162:80',
                        'https': 'https://103.224.5.5:54143'
                        }
            if opt in ('-c', '--use-cli'):
                settings.OPEN_COMMAND = 'aria2c tmp.torrent'

    except getopt.GetoptError:
        print('usage: ./main.py [query] [options]\noptions\n-q, --query= : movie to search for\n-p,--use-proxy: use anonymous proxy')

    if 'query' not in locals():
        query = input('Enter movie name: ')

    query = query.replace(' ', '-')

    # Getting TV Shows

    print(f"Searching for {query}...")
    shows = scraper.get_show(query)

    if len(shows) == 0:
        print('No movies found check the spelling')
        sys.exit(1)

    # Filter out duplicates
    u_shows = []
    for providers in shows:
        if providers['name'] not in u_shows:
            u_shows.append(providers['name'])

    if len(u_shows) > 1:
        print("Choose a show to download")
        questions = [
                inquirer.List('show',
                    '==> ',
                    u_shows,
                    carousel=True
                    )
                ]

        answers = inquirer.prompt(questions)
        answer = answers['show']
    else:
        answer = u_shows[0]


    print("Show:", answer)
        

    # Filter by choosen name
    shows = [show for show in shows if show['name'] == answer]

    # Get seasons
    seasons = [show['season'] for show in shows]

    # Filter out duplicates
    u_seasons = []
    for show in shows:
        if show['season'] not in u_seasons:
            u_seasons.append(show['season'])
    print("Choose a season to download")

    questions = [
            inquirer.List('season',
                '==> ',
                u_seasons,
                carousel=True
                )
            ]

    answers = inquirer.prompt(questions)
    answer = answers['season']

    print("Season:", answer)

    # Filter by season
    shows = [show for show in shows if show['season'] == answer]

    # Filter out duplicates
    u_episodes = []
    for show in shows:
        if show['episode'] not in u_episodes:
            u_episodes.append(show['episode'])
    print("Choose an episode to download")

    questions = [
            inquirer.List('episode',
                '==> ',
                u_episodes,
                carousel=True
                )
            ]

    answers = inquirer.prompt(questions)
    answer = answers['episode']

    print("Episode:", answer)

    # Filter by episodes
    shows = [show for show in shows if show['episode'] == answer]
    # Get qualities
    qualities = [show['quality'] for show in shows]
    u_qualities = []
    for quality in qualities:
        if quality not in u_qualities:
            u_qualities.append(quality)

    if len(u_qualities) > 1:
        print("Choose a quality to download")
        questions = [
                inquirer.List('quality',
                    '==> ',
                    u_qualities,
                    carousel=True
                    )
                ]

        answers = inquirer.prompt(questions)
        answer = answers['quality']
    else:
        answer = u_qualities[0]

    print("Quality:", answer)

    # Filter by quality
    shows = [show for show in shows if show['quality'] == answer]
    # Get providers
    providers = [show['provider'] for show in shows]
    sizes = [show['size'] for show in shows]
    lst = list()
    print(providers, sizes)
    for p, s in itertools.zip_longest(providers, sizes):
        lst.append(f"{p} ({s})")

    if len(providers) > 1:
        print("Choose a provider to download from")
        questions = [
            inquirer.List('provider',
                '==> ',
            lst,
            carousel=True
            )
        ]
        answers = inquirer.prompt(questions)
        answer = answers['provider']
    else:
        answer = providers[0]


    print("Provider:", answer)

    # Filter by provider
    for show in shows:
        x = f"{show['provider']} ({show['size']})"
        if x == answer:
            shows = [show,]
    # Get first show
    show = shows[0]

    # Get download links if available
    print('Getting Download Links...')
    links = scraper.get_downloads(f"https://eztv.unblocked.ltda/search/{query}", show)

    if len(links) > 1:
        print("Choose a mirror to download from?")
        questions = [
                inquirer.List('mirror',
                    '==> ',
                    [f"Mirror {i+1}" for i, link in enumerate(links)],
                    carousel=True
                    )
                ]

        answers = inquirer.prompt(questions)
        answer = answers['mirror'].replace('Mirror ', '')
    else:
        answer = "1"
    
    link = links[0] if answer == "1" else links[1]

    print("Link:", link)

    scraper.open_torrent(link)


if __name__ == "__main__":
    main()
