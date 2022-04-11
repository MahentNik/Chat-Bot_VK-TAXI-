import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from flask import Flask
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
TOKEN = "44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b"
ID = "212291557"


def main(token, club_id):
    db_session.global_init("db/taxi.db")
    # add_default_values()

    app.run()

    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, club_id)

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event)
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            vk = vk_session.get_api()
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message="Спасибо, что написали нам. Мы обязательно ответим",
                             random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main(TOKEN, ID)
