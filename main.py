import random
import math
from flask import Flask
from default_values import *
from data import db_session
from user import *
from request import RequestDriver

TOKEN = "44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b"
ID = "212291557"

first_user_status = "client"
second_user_status = "driver"
sp_answers_client = ["закрыть заказ", "узнать информацию о заказе", "новый заказ"]
client_answers = "\n".join(sp_answers_client)
sp_answers_driver = ["закрыть заказ", "узнать информацию о заказе"]
driver_answers = "\n".join(sp_answers_driver)


def main(token, club_id):
    db_session.global_init("db/taxi.db")
    # add_default_values()

    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, club_id)

    users_today = {}

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_TYPING_STATE and event.object['from_id'] not in users_today:
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
                                        (!Пользователь/!Водитель)
                                         """, random_id=random.randint(0, 2 ** 64))
            users_today[event.obj['from_id']] = pre_user
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.object.message["from_id"]
            user = users_today[user_id]
            user_message = user.give_user_message(event)
            if user_message.lower() == "!пользователь":
                user.change_user_status(first_user_status)
                db_sess = db_session.create_session()
                vk = vk_session.get_api()
                if user.check_data_base(db_sess):
                    user.change_registration_status()
                else:
                    user.add_to_data_base(db_sess)
                    user.change_registration_status()
                vk.messages.send(user_id=user.give_user_id(),
                                 message=f"""У пользователя есть несколько функций на выбор 
                                 (
                                 {client_answers}
                                 )""",
                                 random_id=random.randint(0, 2 ** 64))
            elif user_message.lower() == "!водитель":
                user.change_user_status(second_user_status)
                db_sess = db_session.create_session()
                vk = vk_session.get_api()
                if user.check_data_base(db_sess):
                    user.change_registration_status()
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""У водителя есть несколько функций на выбор 
                                                     (
                                                     {driver_answers}
                                                     )""",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    user.change_registration_status(False)
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
                                 message="Повторяю вопрос, кто вы? Следует отвечать (!водитель/!пользователь)",
                                 random_id=random.randint(0, 2 ** 64))
            elif not user.give_registration_status and user.give_user_status() == second_user_status:
                vk = vk_session.get_api()
                address, class_car, driver_status_of_work = work_with_text(user_message)
                request = RequestDriver()
                latitude, longitude = request.find_latitude_longitude(address)
                status_class_car = request.check_class_car(class_car)
                status_of_driver_status_of_work = request.check_driver_status_of_work(driver_status_of_work)
                if latitude and longitude and status_class_car and status_of_driver_status_of_work:
                    user.change_registration_status()
                    request.add_driver_info(latitude, longitude, status_class_car, status_of_driver_status_of_work)
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="Данные корректны. Вы зарегистрировались.",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""У водителя есть несколько функций на выбор 
                                                     (
                                                     {driver_answers}
                                                     )""",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="Некорректно введены данные!",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Формат ввода: Все в том порядке, как было указано выше и через ' / ':
                                            страна город улица дом / класс вашего авто (эконом, бизнес, комфорт...) /
                                            смена в которую вы будете работать (дневная, ночная)""",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Попробуйте еще раз""",
                                     random_id=random.randint(0, 2 ** 64))
            elif user.give_user_status() and user.give_registration_status():
                vk = vk_session.get_api()
                if user.give_user_status() == first_user_status:
                    if user_message.lower() in sp_answers_client:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""CLIENTCLIENT YESYES""",
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""CLIENT:Некорректно введены данные! Попробуйте еще раз.
                                                 Достумные возможность:
                                                 {client_answers}""",
                                         random_id=random.randint(0, 2 ** 64))
                elif user.give_user_status() == second_user_status:
                    if user_message.lower() in sp_answers_driver:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""DRIVERDRIVER YESYES""",
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""DRIVER:Некорректно введены данные! Попробуйте еще раз.
                                                                         Достумные возможность:
                                                                         {driver_answers}""",
                                         random_id=random.randint(0, 2 ** 64))


def work_with_text(text):
    address, class_car, driver_status_of_work = text.split(" / ")
    return address, class_car, driver_status_of_work


def calculate_distance(a, b):
    radius = 6371
    distance = 2 * radius * math.asin(math.sqrt(math.sin((math.radians(b[0]) - math.radians(a[0])) / 2) ** 2
                                                + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
                                                * math.sin((math.radians(b[1]) - math.radians(a[1])) / 2) ** 2))
    return distance


if __name__ == '__main__':
    main(TOKEN, ID)
