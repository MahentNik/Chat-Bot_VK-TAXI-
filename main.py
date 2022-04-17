import random
import math
from flask import Flask
from default_values import *
from data import db_session
from user import *
from request import RequestDriver

TOKEN = "44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b"
ID = "212291557"

s_s = special_symbol = "&"
first_user_status = "client"
second_user_status = "driver"
sp_answers_client = ["закрыть заказ", "узнать информацию о заказе", "новый заказ"]
client_answers = "\n".join(sp_answers_client)
sl_answers_client = {"закрыть заказ": "Чтобы закрыть заказ ",
                     # или обычный id
                     "узнать информацию о заказе":
                         "Чтобы узнать информацию о заказе необходимо указать его специальный id (special_id)",
                     "новый заказ": "Чтобы создать новый заказ необходимо указать"}
sp_answers_driver = ["закрыть заказ", "узнать информацию о заказе"]
driver_answers = "\n".join(sp_answers_driver)
sl_answers_driver = {"закрыть заказ": "Чтобы закрыть заказ необходимо указать его специальный id (special_id)",
                     "узнать информацию о заказе":
                         "Чтобы узнать информацию о заказе необходимо указать его специальный id (special_id)"}


def main(token, club_id):
    db_session.global_init("db/taxi.db")
    #  add_default_values()

    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, club_id)

    all_driver_status = give_all_driver_status(True)
    all_class_car = give_all_class_car(True)
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
            vk = vk_session.get_api()
            user_id = event.object.message["from_id"]
            user = users_today[user_id]
            user_message = user.give_user_message(event)
            if user_message.lower() == "!пользователь":
                user.change_user_status(first_user_status)
                user.change_function_work_status(False)
                db_sess = db_session.create_session()
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
                user.change_function_work_status(False)
                db_sess = db_session.create_session()
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
                                     message=f"""Все в том порядке, как было указано и через спец. символ - {s_s}.
                                        Формат ввода:
                                        страна город улица дом (для точности) {s_s}
                                        класс вашего авто ({all_class_car}) {s_s}
                                        смена в которую вы будете работать ({all_driver_status})""",
                                     random_id=random.randint(0, 2 ** 64))
            elif user.give_status_special_answers("first"):
                user.change_status_special_answer("first", False)
                request = user.give_request_driver()
                if user_message.lower() == "да":
                    user.change_registration_status()
                    request.add_driver_info(user, vk)
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Отлично, вы зарегистрировались."""
                                     , random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""У водителя есть несколько функций на выбор
                                                     (
                                                     {driver_answers}
                                                     )"""
                                     , random_id=random.randint(0, 2 ** 64))
                    user.change_request_driver(None)
                elif user_message.lower() == "нет":
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Тогда вам придется ввести информацию занова.
                                     Итам, мне необходимо узнать:
                                                1) Адресс вашего проживания;
                                                2) К какому классу относится ваш автомобиль;
                                                3) Ваш режим работы.
                                                """, random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""Все в том порядке, как было указано и через спец. символ - {s_s}.
                                                            Формат ввода:
                                                            страна город улица дом (для точности) {s_s}
                                                            класс вашего авто ({all_class_car}) {s_s}
                                                            смена в которую вы будете работать ({all_driver_status})""",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    user.change_status_special_answer("first", True)
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""Позвольте я повторю.
                                                 Вы проживаете: {request.give_address()}
                                                 Ваш класс авто: {request.give_class_car()}
                                                Ваша смена: {request.give_driver_status()}
                                                СЛЕДУЕТ ОТВЕЧАТЬ
                                                (Да/Нет)
                                                 """, random_id=random.randint(0, 2 ** 64))
            elif not user.give_user_status():
                vk.messages.send(user_id=user.give_user_id(),
                                 message="Повторяю вопрос, кто вы? Следует отвечать (!водитель/!пользователь)",
                                 random_id=random.randint(0, 2 ** 64))
            elif not user.give_registration_status() and user.give_user_status() == second_user_status:
                if work_with_text(user_message):
                    address, class_car, driver_status_of_work = work_with_text(user_message)
                    request = RequestDriver(class_car, driver_status_of_work)
                    if request.find_address(address):
                        res_address = request.find_address(address)
                        if class_car in give_all_class_car(False):
                            if driver_status_of_work in give_all_driver_status(False):
                                user.change_status_special_answer("first", True)
                                user.change_request_driver(request)
                                message = f"""Позвольте я повторю.
                                                        Вы проживаете: {res_address}
                                                        Ваш класс авто: {class_car}
                                                        Ваша смена: {driver_status_of_work}
                                                        (Да/Нет)
                                                        """
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=message,
                                                 random_id=random.randint(0, 2 ** 64))
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Введена неккоректная смена работы.
                                                У вас нет доступа добавлять новую смену. Выбирайте из предложенных:
                                                        ({all_driver_status})
                                                        """,
                                                 random_id=random.randint(0, 2 ** 64))
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message="""Попробуйте еще раз""",
                                                 random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=user.give_user_id(),
                                             message=f"""Введен неккоректный тип автомобиля.
                                                        У вас нет доступа добавлять новый. Выбирайте из предложенных:
                                                        ({all_class_car})
                                                        """,
                                             random_id=random.randint(0, 2 ** 64))
                            vk.messages.send(user_id=user.give_user_id(),
                                             message="""Попробуйте еще раз""",
                                             random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message="Введен некорректный адрес!",
                                         random_id=random.randint(0, 2 ** 64))
                        vk.messages.send(user_id=user.give_user_id(),
                                         message="""Попробуйте еще раз""",
                                         random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="Некорректно введены данные!",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message=f"""Все в том порядке, как было указано и через спец. символ - {s_s}.
                                        Формат ввода:
                                        страна город улица дом {s_s}
                                        класс вашего авто ({all_class_car}) {s_s}
                                        смена в которую вы будете работать ({all_driver_status})""",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=user.give_user_id(),
                                     message="""Попробуйте еще раз""",
                                     random_id=random.randint(0, 2 ** 64))
            elif user.give_user_status() and user.give_registration_status() and not user.give_function_work_status()\
                    and True:
                if user.give_user_status() == first_user_status:
                    if user_message.lower() in sl_answers_client:
                        user.change_function_work_status(True)
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""{sl_answers_client[user_message.lower()]}""",
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""CLIENT:Некорректно введены данные! Попробуйте еще раз.
                                                 Достумные возможности:
                                                 {client_answers}""",
                                         random_id=random.randint(0, 2 ** 64))
                elif user.give_user_status() == second_user_status:
                    if user_message.lower() in sl_answers_driver:
                        user.change_function_work_status(True)
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""{sl_answers_driver[user_message.lower()]}""",
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""DRIVER:Некорректно введены данные! Попробуйте еще раз.
                                                                         Достумные возможности:
                                                                         {driver_answers}""",
                                         random_id=random.randint(0, 2 ** 64))
            elif user.give_function_work_status():
                pass


def work_with_text(text):
    try:
        address, class_car, driver_status_of_work = text.split(special_symbol)
    except Exception:
        return None
    return address, class_car, driver_status_of_work


def give_all_driver_status(status):
    session = db_session.create_session()
    request = session.query(DriverStatus.name).all()
    if status:
        return ", ".join(list(map(lambda x: x[0], request)))
    else:
        return list(map(lambda x: x[0], request))


def give_all_class_car(status):
    session = db_session.create_session()
    request = session.query(ClassCar.name).all()
    if status:
        return ", ".join(list(map(lambda x: x[0], request)))
    else:
        return list(map(lambda x: x[0], request))


def calculate_distance(a, b):
    radius = 6371
    distance = 2 * radius * math.asin(math.sqrt(math.sin((math.radians(b[0]) - math.radians(a[0])) / 2) ** 2
                                                + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
                                                * math.sin((math.radians(b[1]) - math.radians(a[1])) / 2) ** 2))
    return distance


if __name__ == '__main__':
    main(TOKEN, ID)
