from src.keyboards import *
from telethon import events


@bot.on(events.ChatAction)
async def handler(event):
    if event.user_joined:
        txt = 'Приветсвуем в нашем чатике первокурсников ИИКС 2021\n'\
              'Надеемся здесь ты найдешь что-то полезное\n\n' \
              '**ОЧЕНЬ** рекомендую ознакомится с закрепленными сообщениями\n'\
              '[БОТ ИИКС](https://t.me/iics_bot) <- здесь можно будет получать расписание'\
              ' и другую оперативную информацию'
        old = await event.reply(txt)
        await asyncio.sleep(40)
        await old.delete()

'''
ChatAction.Event(
action_message=MessageService(id=1275, 
peer_id=PeerChannel(channel_id=1528046112), 
date=datetime.datetime(2021, 8, 8, 18, 20, 13, tzinfo=datetime.timezone.utc), 
action=MessageActionChatJoinedByLink(inviter_id=1087968824), 
out=False, mentioned=False, media_unread=False, silent=False,
 post=False, legacy=False, from_id=PeerUser(user_id=1117177977), 
 reply_to=None, ttl_period=None), 
 original_update=UpdateNewChannelMessage(message=MessageService(
    id=1275, peer_id=PeerChannel(channel_id=1528046112), 
    date=datetime.datetime(2021, 8, 8, 18, 20, 13, tzinfo=datetime.timezone.utc), 
    action=MessageActionChatJoinedByLink(inviter_id=1087968824), 
    out=False, mentioned=False, media_unread=False, silent=False, 
    post=False, legacy=False, from_id=PeerUser(user_id=1117177977), 
    reply_to=None, ttl_period=None), pts=1402, pts_count=1), new_pin=False, new_photo=False, photo=None, 
    user_added=False, user_joined=True, user_left=False, user_kicked=False, unpin=True, created=False, new_title=None
)
'''