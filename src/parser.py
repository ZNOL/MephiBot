from src.database import *
import requests
from bs4 import BeautifulSoup


def parser_get_urls(formID):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    url = mainUrl + f'/study_groups?level={formID}&organization_id=1&term_id=14'  # TODO обновление каждый сем
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features='html.parser')
    a_list = soup.find_all('a', {'class': 'list-group-item text-center text-nowrap'})

    year = datetime.now().year % 100

    result = {}
    for tmp in a_list:
        name = tmp.get_text(strip=True)
        href = tmp.get('href').split('/')[2]

        course = year - int(name[1:3])   # TODO обновление каждый сем
        try:
            result[course].append({'name': name, 'href': href})
        except KeyError:
            result[course] = list()
            result[course].append({'name': name, 'href': href})
    return result


def parser_make_txt(scheduleId, modeId):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    url = mainUrl + f'/study_groups/{scheduleId}/'
    if modeId == 0:
        url += 'day'
    elif modeId == 1:
        url += 'week'
    elif modeId == 2:
        url += 'schedule'
    elif modeId == 3:
        url += 'exams'

    answer = f'**[Расписание]({url})**\n\n'

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features='html.parser')

    week_days = [day.get_text(strip=True) for day in soup.find_all('h3', {'class': 'lesson-wday'})]
    week_idx = 0

    list_group = soup.find_all('div', {'class': 'list-group'})
    for group in list_group:
        lessons = group.find_all('div', {'class': 'list-group-item'})

        if week_days:
            answer += f'**{week_days[week_idx]}:**\n'
            week_idx += 1

        for lesson in lessons:
            time = lesson.find('div', {'class': ('lesson-time', 'lesson-date')}).get_text(strip=True).replace('\n', ' ')
            mode = lesson.find('div', {'class': 'pull-right'}).get_text(strip=True)
            item = lesson.find('div', {'class': (
                                                'lesson lesson-lecture',
                                                'lesson lesson-test',
                                                'lesson lesson-att',
                                                'lesson lesson-exam',
                                                'lesson lesson-practice',
                                                'lesson lesson-lab',
                                                'lesson',
            )})
            links = lesson.find_all('a', {'class': 'text-nowrap'})

            tmp_txt = time
            try:
                text = item.get_text().split('\n')
                start_idx = text.index(mode) + 1

                for sample in text[start_idx:]:
                    if sample and len(sample) <= 4:
                        tmp_txt += f' | ({sample}) | '
                    elif sample:
                        tmp_txt += f' {sample}\n'
                        break

                if mode == 'ДОТ':
                    tmp_txt += 'ДОТ | '
                for link in links:
                    tmp_txt += f'[{link.get_text(strip=True)}]({mainUrl + link.get("href")}) | '

                if tmp_txt[-2:] == '| ':
                    tmp_txt = tmp_txt[:-2]

                answer += f'{tmp_txt}\n\n'
            except Exception as e:
                logging.error(str(e))
        answer += '\n'
    if answer == f'**[Расписание]({url})**\n\n':
        return ''
    else:
        return answer
