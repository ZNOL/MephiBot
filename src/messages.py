import os
import random
from src.keyboards import *
from telethon import events


async def messenger():
    while True:
        now = datetime.now(timezone('Europe/Moscow'))
        now = now.replace(tzinfo=None)

        if now.time() > time(9):
            next_date = now + timedelta(days=1)
        else:
            next_date = now
        delta = (datetime.fromisoformat(f'{next_date.date()} {time(8)}') - now).seconds

        for user in users_get_all():
            if user['is_active'] and user['current_group']:
                formId, courceNumber, scheduleId = map(int, user['current_group'].split('='))
                txt = parser_make_txt(scheduleId, 0)
                if txt:
                    template = [
                        # Button.inline('Убрать кнопки', 'clear'),
                        Button.inline('Скрыть🔺', 'stop'),
                        Button.inline('Назад⏏', f'get={formId}={courceNumber}={scheduleId}'),
                    ]
                    try:
                        await bot.send_message(user['id'], 'Доброе утро🔅\n\n' + txt, buttons=template)
                    except Exception as e:
                        logging.error(str(e))
        logging.info(f'До следующей рассылки {delta} секунд')
        await asyncio.sleep(delta)


@bot.on(events.NewMessage)
async def new_message(event):
    try:
        id = event.peer_id.user_id
        from_id = id
        flag = True
    except Exception as e:
        try:
            id = event.peer_id.channel_id
            from_id = event.from_id.user_id
            flag = False
        except Exception as e:
            id = event.peer_id.chat_id
            flag = False
            from_id = event.from_id.user_id
    text, media = event.raw_text, event.media

    if flag:
        logging.info(f'Message|{id}: {text}')

    if '/start' == text and flag:
        await event.delete()
        if not users_get(id):
            users_add(id)
            cur_user = await bot.get_entity(id)
            await bot.send_message(mainAdmin, 'Новый пользователь (`{}`) @{}'.format(id, cur_user.username))

        template = main_keyboard[::]
        if users_is_controller(id):
            template += controller_keyboard[::]
        if users_is_admin(id):
            template += admin_keyboard[::]

        txt = 'Приветсвую тебя в боте ИИКС МИФИ.\nЗдесь ты можешь получить расписание для своей группы и много '\
              'полезного в разделе ссылок\n\n'\
              'Предложения по улучшению функционала [приветствуются](https://t.me/ZNOL4)'

        await bot.send_message(id, txt, buttons=template, link_preview=False)

    elif '📄Расписание группы' == text and flag:
        await event.delete()
        data = users_get(id)['current_group']
        try:
            formId, courceNumber, scheduleId = map(int, data.split('='))
            template = await mode_choice(formId, courceNumber, scheduleId)
            await bot.send_message(id, 'Выберите нужный пункт', buttons=template)
        except (ValueError, AttributeError):
            txt = 'У вас не установлены настройки по умолчанию\nУстнановите их выбрав вашу группу в Общем расписании'
            await bot.send_message(id, txt)

    elif '🗓Общее расписание' == text and flag:
        await event.delete()
        template = await form_education()
        await bot.send_message(id, 'Выберите нужный пункт', buttons=template)

    elif '🔗Полезные ссылки' == text and flag:
        await event.delete()
        template = await link_choice()
        await bot.send_message(id, 'Выберите нужный вам пункт', buttons=template)

    elif '/link' == text[:5]:
        await event.delete()
        template = await link_choice()
        old = await bot.send_message(id, 'Выберите нужный вам пункт', buttons=template)
        await asyncio.sleep(120)
        await old.delete()

    elif '🛠Управление рассылкой' == text and flag:
        await event.delete()
        data = users_get(id)
        if data['current_group'] is not None:
            txt = f'Ежедневная рассылка {"🟢ВКЛЮЧЕНА" if data["is_active"] else "🔴ВЫКЛЮЧЕНА"}'
            template = [
                Button.inline('Переключить', 'changeDistribution'),
                Button.inline('Скрыть', 'stop'),
            ]
            await bot.send_message(id, txt, buttons=template)
        else:
            await bot.send_message(id, 'Сперва настройте вашу группу по умолчанию через общее расписание')

    elif '🔈Вещать' == text and users_is_admin(id) and flag:
        await event.delete()
        if id in message_mode:
            message_mode.discard(id)
        else:
            message_mode.add(id)
        old = await bot.send_message(id, f'Режим пересылки {"**ВКЛЮЧЁН**" if id in message_mode else "ВЫКЛЮЧЕН"}')
        await asyncio.sleep(3)
        await old.delete()

    elif '/judge' == text[:6]:
        await event.delete()
        text = text[6:]
        try:
            person = await bot.get_entity(from_id)

            if person.username is not None:
                text += f'\n\nАвтор: @{person.username}'
            else:
                text += f'\n\nАвтор: `{from_id}`'
            template = await judge_buttons(from_id, 0, 0)
            await bot.send_message(id, text, buttons=template)
            now = datetime.now(timezone('Europe/Moscow'))
            name = f'{now.date()}-{str(now.time()).replace(":", "-").replace(".", "-")}'
            with open('files/memes/txt/' + f'{name}.txt', 'w', encoding='utf-8') as file:
                file.write(text)

        except Exception as e:
            logging.error(str(e))
            txt = 'Сначала необходимо активировать [бота](https://t.me/iics_bot)'
            old = await bot.send_message(id, txt)
            await asyncio.sleep(10)
            await old.delete()

    elif '/meme' == text[:5]:
        await event.delete()
        tmp = os.listdir('files/memes/txt')
        idx = random.randint(0, len(tmp) - 1)
        try:
            with open('files/memes/txt/' + tmp[idx], 'r', encoding='utf-8') as file:
                template = await judge_buttons(0, 0, 0)
                old = await bot.send_message(id, file.read(), buttons=template)
                await asyncio.sleep(300)
                await old.delete()
        except Exception as e:
            logging.error(str(e))

    elif '/pic' == text[:4]:
        await event.delete()
        tmp = os.listdir('files/memes/pic')
        idx = random.randint(0, len(tmp) - 1)
        try:
            template = await judge_buttons(0, 0, 0)
            old = await bot.send_file(
                id,
                file='files/memes/pic/' + tmp[idx],
                buttons=template
            )
            await asyncio.sleep(300)
            await old.delete()
        except Exception as e:
            logging.error(str(e))

    elif media is not None and '/add' == text:
        await event.delete()
        now = datetime.now(timezone('Europe/Moscow'))
        name = f'{now.date()}-{str(now.time()).replace(":", "-").replace(".", "-")}'
        try:
            await bot.download_media(event.original_update.message, file=f'files/memes/pic/{name}')
            template = await judge_buttons(from_id, 0, 0)
            await bot.send_file(
                id,
                file=f'files/memes/pic/{name}.jpg',
                buttons=template,
            )
        except Exception as e:
            old = await bot.send_message(id, 'Ошибка во время загрузки.')
            await asyncio.sleep(5)
            await old.delete()

    elif id in add_button and users_is_admin(id):
        await event.delete()
        add_button.discard(id)
        prev_id = users_get(id)["button_id"]
        buttons_add(text, prev_id)

        if prev_id > 0:
            next_count = buttons_get(id=prev_id)["next_count"]
            update(prev_id, 'next_count', next_count + 1, 'buttons')

        if prev_id >= -1:
            template = await change_categories(prev_id)
        else:
            template = await change_final(prev_id)

        await bot.send_message(id, 'Продолжить редактирование', buttons=template)

    elif '⚙️Настройки' == text and users_is_admin(id):
        await event.delete()
        txt = '⚙Выберите необходимый пункт'
        await bot.send_message(id, txt, buttons=settings_buttons)

    elif id in change_controller:
        await event.delete()
        try:
            deviceId = int(text)
            data = users_get(deviceId)
            if data is None:
                raise ValueError
            flag = data["is_controller"]
            txt = f'Контроллер: {"✅" if flag else "❌"}'
            template = [
                Button.inline('Изменить права', f'changeRole=0={text}'),
                Button.inline('Отмена', 'settings')
            ]
            await bot.send_message(id, txt, buttons=template)
        except ValueError:
            template = [Button.inline('Отмена', 'stop')]
            await bot.send_message(id, 'Девайс не найден\nПовторите отправку ID', buttons=template)

    elif id in change_admin:
        await event.delete()
        try:
            deviceId = int(text)
            data = users_get(deviceId)
            if data is None:
                raise ValueError
            flag = data["is_admin"]
            txt = f'Администратор: {"✅" if flag else "❌"}'
            template = [
                Button.inline('Изменить права', f'changeRole=1={text}'),
                Button.inline('Отмена', 'settings')
            ]
            await bot.send_message(id, txt, buttons=template)
        except ValueError:
            template = [Button.inline('Отмена', 'settings')]
            await bot.send_message(id, 'Девайс не найден\nПовторите отправку ID', buttons=template)

    elif '/get_id' == text[:7] and (flag or users_is_admin(from_id)):
        await event.delete()
        txt = f'🆔 `{id}`'
        old = await bot.send_message(id, txt)
        await asyncio.sleep(10)
        await old.delete()

    elif '/get' == text[:4] and (users_is_admin(from_id) or flag):
        await event.delete()
        template = await form_education()
        await bot.send_message(id, 'Выберите нужный пункт', buttons=template)

    elif '/sendChat' == text[:9] and users_is_controller(from_id):
        await event.delete()
        template = Button.inline('Скрыть', 'stop')
        async for user in bot.iter_participants(mainChat):
            try:
                await bot.send_message(user.id, text[10:], buttons=template)
            except Exception as e:
                logging.error(str(e))

    elif '/sendUser' == text[:9] and users_is_admin(from_id):
        await event.delete()
        template = Button.inline('Скрыть', 'stop')
        for user in users_get_all():
            try:
                await bot.send_message(user['id'], text[10:], buttons=template)
            except Exception as e:
                logging.error(str(e))

    elif '/find' == text[:5] and users_is_admin(from_id):
        await event.delete()
        userId = int(text.split()[-1])
        txt = 'Пользователь не найден'
        async for userEntity in bot.iter_participants(id):
            if userId == userEntity.id:
                txt = f'@{userEntity.username} | {userEntity.first_name} {userEntity.last_name} | `{userId}`'
                break
        old = await bot.send_message(id, txt)
        await asyncio.sleep(10)
        await old.delete()

    elif id in message_mode:
        await bot.send_message(mainChat, text, link_preview=False)

    elif text and '/' == text[0]:
        await event.delete()

    elif flag:
        await event.delete()
        old = await bot.send_message(id, 'Вся жизнь - борьба!')
        await asyncio.sleep(3)
        await old.delete()
