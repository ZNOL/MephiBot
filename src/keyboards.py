from telethon.tl.types import *
from telethon.tl.custom import *
from src.users import *


async def change_categories(prev_id=-1):
    buttons = []
    for button_val in buttons_get_all(prev_id):
        buttons.append([Button.inline(button_val["value"], f"changeMenu={button_val['id']}")])
        buttons[-1].append(Button.inline('🗑', f"deleteButton={button_val['id']}"))

    buttons.append([Button.inline('➕Добавить здесь', 'addHere')])
    if prev_id != -1:
        parentId = buttons_get(id=prev_id)['prev_id']
        buttons.append([Button.inline('Назад⏏️️', f'changeMenu={parentId}')])
    else:
        buttons.append([Button.inline('Завершить', 'settings')])
    return buttons


async def change_final(prev_id):
    buttons = []
    k = 0
    for button_val in buttons_get_all(prev_id):
        template = Button.inline(f'🗑 {button_val["value"]}', f"deleteButton={button_val['id']}")
        if not k:
            buttons.append([template])
        else:
            buttons[-1].append(template)
        k = (k + 1) % 2
    buttons.append([Button.inline('➕Добавить здесь', 'addHere')])
    buttons[-1].append(Button.inline('Завершить', 'settings'))
    return buttons


async def link_choice(prevId=-1):
    buttons = []
    k = 0
    for button_val in buttons_get_all(prevId):
        if button_val['next_count'] == 0 and button_val['value'].count('|'):
            name, currentLink = button_val['value'].split('|')
            template = Button.url(name, currentLink)
        else:
            template = Button.inline(button_val['value'], f'link={button_val["id"]}')

        if not k:
            buttons.append([template])
        else:
            buttons[-1].append(template)
        k = (k + 1) % 2

    if prevId != -1:
        parentId = buttons_get(id=prevId)['prev_id']
        buttons.append([Button.inline('Назад⏏️', f'link={parentId}')])
    else:
        buttons.append([Button.inline('Скрыть', 'stop')])
    return buttons


async def form_education():
    buttons = [
        [
            Button.inline('Бакалавриат', 'get=0'),
            Button.inline('Специалитет', 'get=1'),
        ],
        [
            Button.inline('Магистратура', 'get=2'),
            Button.inline('Аспирантура', 'get=3'),
        ],
        [
            Button.inline('Скрыть', 'stop'),
        ],
    ]
    return buttons


async def course_number(formId):
    buttons = [
        [
            Button.inline('1 курс', f'get={formId}=1'),
            Button.inline('2 курс', f'get={formId}=2'),
            Button.inline('3 курс', f'get={formId}=3'),
        ],
        [
            Button.inline('4 курс', f'get={formId}=4'),
            Button.inline('5 курс', f'get={formId}=5'),
            Button.inline('6 курс', f'get={formId}=6'),
        ],
        [
            Button.inline('Назад⏏️', 'get')
        ]
    ]
    return buttons


async def group_choice(formId, courceNumber):
    buttons = []
    tmp = parser_get_urls(formId)
    k = 0
    print(tmp)
    if courceNumber in tmp:
        for group in tmp[courceNumber]:
            template = Button.inline(group['name'], f'get={formId}={courceNumber}={group["href"]}')
            if not k:
                buttons.append([template])
            else:
                buttons[-1].append(template)
            k = (k + 1) % 4
    buttons.append([Button.inline('Назад⏏️', f'get={formId}')])
    return buttons


async def mode_choice(formId, courceNumber, scheduleId):
    buttons = [
        [
            Button.inline('Текущий день', f'get={formId}={courceNumber}={scheduleId}=0'),
            Button.inline('Текущая неделя', f'get={formId}={courceNumber}={scheduleId}=1'),
        ],
        [
            Button.inline('Все недели', f'get={formId}={courceNumber}={scheduleId}=2'),
            Button.inline('Сессия', f'get={formId}={courceNumber}={scheduleId}=3'),
        ],
        [
            Button.inline('Устнановить поумолчанию', f'setDefault={formId}={courceNumber}={scheduleId}'),
            Button.inline('Скрыть', 'stop'),
        ],
        [
            Button.inline('Назад⏏️', f'get={formId}={courceNumber}'),
        ],
    ]
    return buttons


async def judge_buttons(userId, likes, dislikes):
    return [
        Button.inline(f'👍 {likes}', f'like={userId}={likes}={dislikes}=1'),
        Button.inline(f'👎 {dislikes}', f'like={userId}={likes}={dislikes}=0')
    ]


main_keyboard = [
    [
        Button.text('📄Расписание группы', resize=True),
        Button.text('🗓Общее расписание', resize=True),
    ],
    [
        Button.text('🔗Полезные ссылки', resize=True),
        Button.text('🛠Управление рассылкой', resize=True),
    ]
]

controller_keyboard = [

]

admin_keyboard = [
    [
        Button.text('🔈Вещать', resize=True),
        Button.text('⚙️Настройки', resize=True),
    ]
]

settings_buttons = [
    [Button.inline('Настроить ссылки', 'changeMenu=-1')],
    [Button.inline('Добавить/удалить управляющего', 'changeRole=0')],
    [Button.inline('Добавить/удалить администратора', 'changeRole=1')],
    [Button.inline('Завершить', 'stop')],
]
