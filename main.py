import random
from flask import Flask
from default_values import *
from data import db_session
from user import *
from request import Request

TOKEN = "44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b"
ID = "212291557"
first_user_status = "client"
second_user_status = "driver"


def main(token, club_id):
    db_session.global_init("db/taxi.db")
    # add_default_values()

    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, club_id)

    users_today = {}
    sp_answers_client = ["", "", ""]
    sp_answers_driver = ["", "", ""]

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_TYPING_STATE and event.obj['from_id'] not in users_today:
            pre_user = User()
            pre_user.take_user_id(event)
            vk = vk_session.get_api()
            name = pre_user.give_user_name(vk)
            vk.messages.send(user_id=event.object['from_id'],
                             message=f"""Здравствуйте, {name}.
                             Прочитайте это прежде чем что-то написать.
                             Я глупый бот, не знающий сущностей, и умею распознавать ограниченный круг запросов (
                             Прошу отнестись с пониманием и отвечать по указанной схеме.
                             """, random_id=random.randint(0, 2 ** 64))
            vk.messages.send(user_id=event.object['from_id'],
                             message=f"""Кто вы?
                                        (Пользователь/Водитель)
                                         """, random_id=random.randint(0, 2 ** 64))
            users_today[event.obj['from_id']] = pre_user

        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message["from_id"]
            user = users_today[user_id]

            if event.obj.message['text'].lower == "пользователь":
                user.change_user_status(first_user_status)
                db_sess = db_session.create_session()
                vk = vk_session.get_api()

                if user.check_data_base(db_sess):
                    user.change_registration_status()

                else:
                    user.add_to_data_base(db_sess)
                    user.change_registration_status()
                vk.messages.send(user_id=user.give_user_id(),
                                 message="", random_id=random.randint(0, 2 ** 64))

            elif event.obj.message['text'].lower == "водитель":
                user.change_user_status(second_user_status)
                db_sess = db_session.create_session()
                vk = vk_session.get_api()

                if user.check_data_base(db_sess):
                    user.change_registration_status()

                else:
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""К сожалению, мне не удалось найти ваш аккаунт на нашем сервере,
                                     поэтому я вас туда добавлю, но чтобы операция прошла успешно,
                                     вы должны сообщить мне информацию,
                                     чтобы беспрепятственно сотрудничать с нашим сервисом.""",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Итам, мне необходимо узнать:
                                     1) Адресс вашего проживания;
                                     2) К какому классу относится ваш автомобиль;
                                     3) Ваш режим работы.
                                     """, random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Формат ввода: Все в том порядке, как было указано выше и через ' / ':
                                     страна город улица дом / класс вашего авто (эконом, бизнес, комфорт...) /
                                     смена в которую вы будете работать (дневная, ночная)""",
                                     random_id=random.randint(0, 2 ** 64))

            elif not user.give_user_status():
                vk = vk_session.get_api()
                vk.messages.send(user_id=user.give_user_id(),
                                 message="Повторяю вопрос, кто вы? Следует отвечать (водитель/пользователь)",
                                 random_id=random.randint(0, 2 ** 64))

            elif not user.give_registration_status and user.give_user_status():
                text_message = event.object.message["text"]
                address, class_car, driver_status_of_work = work_with_text(text_message)
                request = Request()
                latitude, longitude = request.find_latitude_longitude(address)
                status_class_car = request.check_class_car(class_car)
                status_of_driver_status_of_work = request.check_driver_status_of_work(driver_status_of_work)

            elif user.give_user_status() == "client" and event.obj.message["text"].lower in sp_answers_client:
                pass

            elif user.give_user_status() == "driver" and event.obj.message["text"].lower in sp_answers_driver:
                pass


def work_with_text(text):
    address, class_car, driver_status_of_work = text.split(" / ")
    return address, class_car, driver_status_of_work


if __name__ == '__main__':
    main(TOKEN, ID)
