from src.keyboards import *
from telethon import events


@bot.on(events.callbackquery.CallbackQuery())
async def new_button(event):
    try:
        id = event.original_update.user_id
    except Exception as e:
        id = ''
    command = event.original_update.data.decode('utf-8')

    logging.info(f'Command|{id}: {command}')
    print(id, command)

    if 'clear' == command:
        pass
        # template = Button.clear()
        # await event.edit(buttons=template)

    elif 'stop' == command:
        add_button.discard(id)
        change_controller.discard(id)
        change_admin.discard(id)
        message_mode.discard(id)
        update(id, 'button_id', 0, 'users')
        old = await event.edit('✅')
        await asyncio.sleep(5)
        await old.delete()

    elif 'get' == command[:3]:
        if command.count('=') == 0:
            template = await form_education()
            await event.edit('Выберите нужный пункт', buttons=template)
        elif command.count('=') == 1:
            formId = int(command.split('=')[-1])
            template = await course_number(formId)
            await event.edit('Выберите курс', buttons=template)
        elif command.count('=') == 2:
            formId, courseNumber = map(int, command.split('=')[1:])
            template = await group_choice(formId, courseNumber)
            await event.edit('Выберите свою группу', buttons=template)
        elif command.count('=') == 3:
            formId, courseNumber, scheduleId = map(int, command.split('=')[1:])
            template = await mode_choice(formId, courseNumber, scheduleId)
            await event.edit('Выберите нужный пункт', buttons=template)
        elif command.count('=') == 4:
            formId, courseNumber, scheduleId, modeId = map(int, command.split('=')[1:])
            template = [
                # Button.inline('Убрать кнопки', 'clear'),
                Button.inline('Назад⏏', f'get={formId}={courseNumber}={scheduleId}'),
            ]
            txt = parser_make_txt(scheduleId, modeId)
            await event.edit(txt, buttons=template)

    elif 'link' == command[:4]:
        if command.count('=') == 1:
            prevId = int(command.split('=')[-1])
            template = await link_choice(prevId)
            await event.edit(buttons=template)

    elif 'setDefault' == command[:10]:
        formId, courseNumber, scheduleId = map(int, command.split('=')[1:])
        update(id, 'current_group', f'{formId}={courseNumber}={scheduleId}', 'users')
        template = await mode_choice(formId, courseNumber, scheduleId)
        await event.edit('Настройки по умолчанию установлены!', buttons=template)

    elif 'changeDistribution' == command:
        flag = users_get(id)['is_active']
        update(id, 'is_active', (flag + 1) % 2, 'users')
        data = users_get(id)
        txt = f'Ежедневная рассылка {"🟢ВКЛЮЧЕНА" if data["is_active"] else "🔴ВЫКЛЮЧЕНА"}'
        template = [
            Button.inline('Переключить', 'changeDistribution'),
            Button.inline('Скрыть', 'stop'),
        ]
        await event.edit(txt, buttons=template)

    elif 'like' == command[:4]:
        if command.count('=') == 4:
            userId, likes, dislikes, value = map(int, command.split('=')[1:])
            if userId != id:
                try:
                    if value:
                        template = await judge_buttons(userId, likes + 1, dislikes)
                    else:
                        template = await judge_buttons(userId, likes, dislikes + 1)
                    await event.edit(buttons=template)
                except Exception:
                    pass

    elif 'addHere' == command:
        add_button.add(id)
        txt = 'Введите содержимое'
        await event.edit(txt, buttons=Button.inline('Отменить добавление', 'stop'))

    elif 'deleteButton' == command[:12]:
        deleteId = int(command.split('=')[-1])
        prev_id = users_get(id)["button_id"]
        buttons_delete(deleteId)
        if prev_id >= -1:
            template = await change_categories(prev_id)
        else:
            template = await change_final(prev_id)
        await event.edit(buttons=template)

    elif 'changeMenu' == command[:10]:
        idx = int(command.split('=')[-1])
        update(id, 'button_id', idx, 'users')
        template = await change_categories(idx)
        await event.edit('Продолжить редактирование', buttons=template)

    elif 'changeRole' == command[:10]:
        if command.count('=') == 1:
            idx = int(command.split('=')[-1])
            if idx == 0:  # изменить is_controller
                change_controller.add(id)
            elif idx == 1:  # изменить is_admin
                change_admin.add(id)
            txt = 'Введите ID устройства'
            template = [Button.inline('Отмена', 'settings')]
            await event.edit(txt, buttons=template)
        elif command.count('=') == 2:
            idx, deviceId = map(int, command.split('=')[1:])
            answer = 'Обновление завершено'
            if idx == 0:
                change_controller.discard(id)
                flag = users_get(deviceId)["is_controller"]
                update(deviceId, 'is_controller', (flag + 1) % 2, 'users')
                try:
                    txt = 'Ваши права изменены\nНеобходимо написать **`/start`** для обновления интерфейса'
                    await bot.send_message(deviceId, txt)
                except Exception as e:
                    logging.error(str(e))
            elif idx == 1:
                change_admin.discard(id)
                flag = users_get(deviceId)["is_admin"]
                if deviceId == mainAdmin and flag == 0 or deviceId != mainAdmin and id != deviceId:
                    update(deviceId, 'is_admin', (flag + 1) % 2, 'users')
                    try:
                        txt = 'Ваши права изменены\nНеобходимо написать **`/start`** для обновления интерфейса'
                        await bot.send_message(deviceId, txt)
                    except Exception as e:
                        logging.error(str(e))
                else:
                    answer = 'Запрещено изменять права администратора у данного пользователя'
            await event.edit(answer, buttons=settings_buttons)

    elif 'settings' == command:
        add_button.discard(id)
        update(id, 'button_id', 0, 'users')
        change_controller.discard(id)
        change_admin.discard(id)
        txt = '⚙Выберите необходимый пункт'
        await event.edit(txt, buttons=settings_buttons)
