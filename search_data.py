import requests
from bs4 import BeautifulSoup as Bs
import pg_helper as db


def __check_media_links() -> list[dict[str, str]]:
    """
    Creates a list of currently available media.
    :return: List of dict {source, title, link}
    """

    sources: list[list[str]] = [
        ['amtliche-bekanntmachungen', 'https://www.freising.de/rathaus/amtliche-bekanntmachungen'],
        ['aktuelle-auslegungen', 'https://www.freising.de/rathaus/amtliche-bekanntmachungen/aktuelle-auslegungen'],
        ['haushalt-der-stadt-freising', 'https://www.freising.de/rathaus/finanzen/haushalt-der-stadt-freising'],
        ['stadtrat', 'https://www.freising.de/rathaus/politik/stadtrat']
    ]
    media: list[dict[str, str]] = []

    for s in sources:
        r = requests.get(s[1])

        soup = Bs(r.text, features='html.parser')

        for link in soup.findAll('a'):
            if link.get('class') is not None and link.get('class')[0] == 'm-download-item__link':
                media.append({'source': s[0], 'title': link.get('title'),
                              'link': f"https://www.freising.de{link.get('href')}"})

    return media


def add_media_links_to_db():
    """
    Adds currently available media to database.
    """
    db.create_media_link_table()
    db.extend_media_link_table(__check_media_links())


def __get_motion_data() -> list[list[str]]:
    """
    Generates a list of current motions.
    :return: list[party, regarding, media, status]
    """
    r = requests.get('https://www.freising.de/rathaus/politik/antraege-aus-dem-stadtrat')

    table = Bs(r.text, features='html.parser').findAll('tr')
    table.pop(0)

    """party, regarding, media, status"""
    motions: list[list[str]] = []

    for row in table:

        lines = Bs(str(row), features='html.parser').findAll('td')

        party = ' '.join(str(lines[0]).replace('<td rowspan="1">', '').replace('</td>', '')
                         .replace('<br/>', '').replace('<td>', '').split())

        regarding = ' '.join(str(lines[1]).replace('<td rowspan="1">', '').replace('</td>', '')
                             .replace('<br/>', '').split())

        media: str = None

        if regarding.__contains__('href="'):
            media = regarding.split('href="')[1].split('"')[0]
            regarding = regarding.split('title="')[1].split('">')[1].split('</a>')[0]

        status = ' '.join(str(lines[2]).replace('<td rowspan="1">', '').replace('</td>', '')
                          .replace('<br/>', '').replace('<td>', '').split())

        motions.append([party, regarding, media, status])

    return motions


def add_city_council_motion_to_db():
    """
    Adds currently available motions to database.
    """
    db.create_motion_table()
    motions = __get_motion_data()

    print(f'[INFO]: {len(motions)} current motions found.')

    updated_motions = 0

    for m in motions:
        b = db.update_motion_table(m[0], m[1], m[2], m[3])
        if b:
            updated_motions = updated_motions + 1

    print(f'[INFO]: {updated_motions} motions added or updated.')
