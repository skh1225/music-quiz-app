# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection
from channels.db import database_sync_to_async
from core.models import (
    Room,
    Music,
    User
)

@database_sync_to_async
def update_user_channel(user, channel_name, room_group_name):
    user.channel_name = channel_name
    user.room_name = room_group_name
    user.save()

@database_sync_to_async
def get_music_titles(room_name):
    result = []
    music_list = Room.objects.get(name=room_name).music_list
    for music in music_list:
        result.append(''.join(Music.objects.get(id=music).title.split(' ')).lower())
    return result

@database_sync_to_async
def get_user_names(user_ids):
    result = ''
    for user_id in user_ids:
        result += User.objects.get(id=user_id).name +','
    return result

@database_sync_to_async
def delete_room(room_group_name):
    instance = Room.objects.get(name=room_group_name)
    instance.delete()


class ChatConsumer(AsyncWebsocketConsumer):

    conn = get_redis_connection('default')

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.room_name
        reconnect = False
        try:
            if self.scope['user'].is_anonymous:
                raise Exception('is not authenticated')
        except:
            await self.close()
            return

        if self.scope['user'].room_name is not None:
            await self.channel_layer.group_discard(self.scope['user'].room_name, self.scope['user'].channel_name)

            if self.scope['user'].room_name != self.room_group_name:
                self.conn.srem(self.scope['user'].room_name+'_ready', self.scope['user'].id)
                self.conn.zrem(self.scope['user'].room_name+'_score', self.scope['user'].id)

                if int(self.conn.zcard('asgi:group:'+self.scope['user'].room_name)) == 0:
                    self.conn.delete(self.scope['user'].room_name+'_info')
                    self.conn.delete(self.scope['user'].room_name+'_mlist')
                    self.conn.delete(self.scope['user'].room_name+'_score')
                    await delete_room(self.scope['user'].room_name)
                else:
                    await self.channel_layer.group_send(
                                self.scope['user'].room_name, {
                                    "type": "notice_message",
                                    "notice": "exit",
                                    "total": int(self.conn.zcard('asgi:group:'+self.scope['user'].room_name)),
                                    "user_name": self.scope['user'].name
                                    }
                            )
            else:
                reconnect = True

        if not self.conn.exists(self.room_group_name+'_info'):
            self.conn.hmset(self.room_group_name+'_info', { 'round': -1, 'state': 0 })
            music_list = await get_music_titles(self.room_name)
            for ml in music_list:
                self.conn.rpush(self.room_group_name+'_mlist', ml)
        else:
            total = int(self.conn.zcard('asgi:group:'+self.room_group_name))
            if total >= 8:
              await self.close()
              return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await update_user_channel(self.scope['user'], self.channel_name, self.room_group_name)

        await self.accept()

        if not self.conn.zscore(self.room_group_name+'_score', self.scope['user'].id):
            self.conn.zadd(self.room_group_name+'_score', { self.scope['user'].id: 0 })

        if not reconnect:
            await self.channel_layer.group_send(
                                self.room_group_name, {
                                    "type": "notice_message",
                                    "notice": "enter",
                                    "total": int(self.conn.zcard('asgi:group:'+self.room_group_name)),
                                    "user_name": self.scope['user'].name
                                    }
                            )

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        self.conn.srem(self.room_group_name+'_ready', self.scope['user'].id)
        self.conn.zrem(self.room_group_name+'_score', self.scope['user'].id)

        if int(self.conn.zcard('asgi:group:'+self.room_group_name)) == 0:
            self.conn.delete(self.room_group_name+'_info')
            self.conn.delete(self.room_group_name+'_mlist')
            self.conn.delete(self.room_group_name+'_score')
            await delete_room(self.room_group_name)
        else:
            await self.channel_layer.group_send(
                        self.room_group_name, {
                            "type": "notice_message",
                            "notice": "exit",
                            "total": int(self.conn.zcard('asgi:group:'+self.room_group_name)),
                            "user_name": self.scope['user'].name
                            }
                    )
        await update_user_channel(self.scope['user'], None, None)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        i = int(self.conn.hget(self.room_group_name+'_info','round'))
        if 'message' in text_data_json:
            message = text_data_json["message"]
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": message, "user_name": self.scope['user'].name}
            )

            if (i >= 0 and i < 50 and
                ''.join(message.split(' ')).lower() == self.conn.lrange(self.room_group_name+'_mlist', i, i)[0].decode() and
                not int(self.conn.hget(self.room_group_name+'_info','state'))):
                  self.conn.hset(self.room_group_name+'_info', 'state', 1)
                  self.conn.zincrby(self.room_group_name+'_score', 1, self.scope['user'].id)
                  await self.channel_layer.group_send(
                      self.room_group_name, {"type": "correct_message", "action": "correct", "user_name": self.scope['user'].name}
                  )
                  await self.channel_layer.group_send(
                            self.room_group_name, {"type": "score_message"}
                        )
        if 'action' in text_data_json:
            action = text_data_json["action"]
            if action == 'skip':
                self.conn.sadd(self.room_group_name+'_ready', self.scope['user'].id)
                total_num = int(self.conn.zcard('asgi:group:'+self.room_group_name))
                ready_num = int(self.conn.scard(self.room_group_name+'_ready'))
                if i == -1:
                    if total_num == ready_num:
                        self.conn.delete(self.room_group_name+'_ready')
                        self.conn.hset(self.room_group_name+'_info', 'state', 0)
                        await self.channel_layer.group_send(
                            self.room_group_name, {"type": "action_message", "action": "start", "round": i+1}
                        )
                        await self.channel_layer.group_send(
                            self.room_group_name, {"type": "score_message"}
                        )
                        self.conn.hincrby(self.room_group_name+'_info', 'round', 1)
                    else:
                        await self.channel_layer.group_send(
                            self.room_group_name, {"type": "ready_message", "ready": ready_num, "total": total_num}
                        )
                else:
                    if total_num//2+1 == ready_num:
                        if i == 50-1:
                            self.conn.delete(self.room_group_name+'_ready')
                            self.conn.hset(self.room_group_name+'_info', 'state', 0)
                            await self.channel_layer.group_send(
                                self.room_group_name, {"type": "action_message", "action": "end", "round": i+1}
                            )
                            self.conn.hincrby(self.room_group_name+'_info', 'round', 1)
                        else:
                            self.conn.delete(self.room_group_name+'_ready')
                            self.conn.hset(self.room_group_name+'_info', 'state', 0)
                            await self.channel_layer.group_send(
                              self.room_group_name, {"type": "action_message", "action": "skip", "round": i+1}
                            )
                            self.conn.hincrby(self.room_group_name+'_info', 'round', 1)
                    else:
                        await self.channel_layer.group_send(
                            self.room_group_name, {"type": "ready_message", "ready": ready_num, "total": total_num}
                        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        user_name = event["user_name"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "user_name": user_name}))

    async def correct_message(self, event):
        action = event["action"]
        user_name = event["user_name"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": action, "user_name": user_name}))

    async def action_message(self, event):
        action = event["action"]
        rnd = event["round"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": action, "round": rnd}))

    async def ready_message(self, event):
        ready = event["ready"]
        total = event["total"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"ready": ready, "total": total}))

    async def notice_message(self, event):
        total = event["total"]
        notice = event["notice"]
        user_name = event["user_name"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"notice": notice, "total": total, "user_name": user_name}))

    async def score_message(self, event):
        score_board = self.conn.zrevrange(self.room_group_name+'_score', 0, -1, withscores=True)
        user_ids = []
        user_scores = ''
        for user_id, score in score_board:
            user_ids.append(int(user_id))
            user_scores += str(int(score))+','
        user_names = await get_user_names(user_ids)
        await self.send(text_data=json.dumps({"score": user_scores, "user_names": user_names}))



# Redis

# hash
# room_info {
#   total: int,
#   round: int,
#   isUnderWay: bool,
#   state: bool,
# }

# list
# room_titles

# set
# room_ready

# 'name': 'message'
# 1. send
# 2. round != 0 && !state => room_titles[round] == message? => !state => send


# 'userId': 'action'
# skip:
# 1. isUnderWay => len(room_ready) > room_info.total//2+1 => round++
#   1) round > 50 => isUnderWay = false => send(game end)
#   2) else => send(round)
# 2. else => len(room_ready) >= room_info.total => send(++round)

# state = false
# room_ready = clear
