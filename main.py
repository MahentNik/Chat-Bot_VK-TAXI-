import random
from default_values import *
from data import db_session
from user import *
from request import RequestDriver
from client_request import ClientRequest
from driver_request import DriverRequest
from data.receipt import Receipt

TOKEN = "44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b"
ID = "212291557"

first_user_status = "client"
second_user_status = "driver"
s_s = special_symbol = "&"


def main(token, club_id):
    db_session.global_init("db/taxi.db")
    # add_default_values()

    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, club_id)

    all_driver_status = give_all_driver_status(True)
    all_class_car = give_all_class_car(True)
    sp_answers_client = ["закрыть заказ", "узнать информацию о заказе", "новый заказ", "все заказы"]
    client_answers = "\n".join(sp_answers_client)
    sp_answers_driver = ["закрыть заказ", "узнать информацию о заказе", "все заказы"]
    driver_answers = "\n".join(sp_answers_driver)
    sl_answers_driver = {"закрыть заказ": ["Чтобы закрыть заказ необходимо указать его id",
                                           "first"],
                         "узнать информацию о заказе":
                             ["Чтобы узнать информацию о заказе необходимо указать его id",
                              "second"],
                         "все заказы": ["", "forth"]
                         }
    sl_answers_client = {"закрыть заказ": [
        "Чтобы закрыть заказ необходимо указать его id", "first"
    ],
        "узнать информацию о заказе":
            [
                "Чтобы узнать информацию о заказе необходимо указать его id", "second"
            ],
        "новый заказ": [f"""Чтобы создать новый заказ необходимо указать:
                         1) Адрес вашего местанахождения (откуда вы поедите)
                         2) Адрес куда вы поедите (конечный пункт)
                         3) Класс автомобиля из предложенных ({all_class_car})
                         4) Время к которому вам нужен заказ (год(последние 2 цифры)/месяц/день часы:минуты)
                            Формат:
                            Адрес_1{s_s}Адрес_2{s_s}Класс авто{s_s}дата""", "third"
                        ],
        "все заказы": ["1234", "forth"]
    }

    users_today = {}

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            if not event.object['from_id'] in users_today:
                pre_user = User()
                pre_user.take_user_id(event)
                vk = vk_session.get_api()
                name = pre_user.give_user_name(vk)
                vk.messages.send(user_id=pre_user.give_user_id(),
                                 message=f"""Здравствуйте, {name}.
                                 Прочитайте это прежде чем что-то написать.
                                 Я глупый бот, не знающий сущностей, и умею распознавать ограниченный круг запросов (
                                 Прошу отнестись с пониманием и отвечать по указанной схеме.
                                 """, random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=pre_user.give_user_id(),
                                 message=f"""Кто вы?
                                            (!Пользователь/!Водитель)
                                             """, random_id=random.randint(0, 2 ** 64))
                users_today[event.obj['from_id']] = pre_user
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            if event.object.message["from_id"] not in users_today:
                pre_user = User()
                id_u = event.obj.message['from_id']
                pre_user.add_user_id(id_u)
                users_today[pre_user.give_user_id()] = pre_user
                vk.messages.send(user_id=pre_user.give_user_id(),
                                 message=f"""Здравствуйте, {pre_user.give_user_name(vk)}.
                                Я глупый бот, не знающий сущностей, и умею распознавать ограниченный круг запросов (
                                Прошу отнестись с пониманием и отвечать по указанной схеме.
                                             """, random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=pre_user.give_user_id(),
                                 message=f"""Кто вы?
                                                        (!Пользователь/!Водитель)
                                                         """, random_id=random.randint(0, 2 ** 64))
            else:
                user_id = event.object.message["from_id"]
                user = users_today[user_id]
                user_message = user.give_user_message(event).lower()
                if user_message == "!пользователь":
                    user.change_user_status(first_user_status)
                    client_request = ClientRequest()
                    user.change_special_request(client_request)
                    roll_back(user)
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
                elif user_message == "!водитель":
                    user.change_user_status(second_user_status)
                    driver_request = DriverRequest()
                    user.change_special_request(driver_request)
                    roll_back(user)
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
                    if user_message == "да":
                        user.change_registration_status()
                        request.add_driver_info(user, vk)
                        vk.messages.send(user_id=user.give_user_id(),
                                         message="Отлично, вы зарегистрировались.",
                                         random_id=random.randint(0, 2 ** 64))
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""У водителя есть несколько функций на выбор
                                                         (
                                                         {driver_answers}
                                                         )""",
                                         random_id=random.randint(0, 2 ** 64))
                        user.change_request_driver(None)
                    elif user_message == "нет":
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
                elif user.give_status_special_answers("second"):
                    db_sess = db_session.create_session()
                    user.change_status_special_answer("second", False)
                    request = user.give_special_request()
                    address_1, address_2, c_car, date, driver, price = request.give_receipt_info()
                    if user_message == "да":
                        user.change_function_work_status(False)
                        user.change_status_cl_dr_answers("third", False)
                        c_request = user.give_special_request()
                        c_request.add_new_receipt(db_sess, user)
                        vk.messages.send(user_id=user.give_user_id(),
                                         message="Отлично, вы оформили заказ",
                                         random_id=random.randint(0, 2 ** 64))
                    elif user_message == "нет":
                        vk.messages.send(user_id=user.give_user_id(),
                                         message="""Тогда вам придется ввести информацию занова.
                                                    """, random_id=random.randint(0, 2 ** 64))
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""{sl_answers_client["новый заказ"][0]}""",
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        user.change_status_special_answer("second", True)
                        if driver.account_id:
                            i = driver.account_id
                            d = "vk.com/id" + str(i)
                        else:
                            d = driver.name
                        vk.messages.send(user_id=user.give_user_id(),
                                         message=f"""Ваш заказ:
                                                        От: {address_1}
                                                        Куда: {address_2}
                                                        Авто: {c_car}
                                                        Время: {date}
                                                        Водитель: {d}
                                                        Цена: {price}
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
                elif user.give_user_status() and user.give_registration_status() \
                        and not user.give_function_work_status():
                    if user.give_user_status() == first_user_status:
                        if user_message.lower() in sl_answers_client:
                            if sl_answers_client[user_message][1] == "forth":
                                db_sess = db_session.create_session()
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""ID всех ваших заказов:
                                        {give_all_receipts(user, db_sess)}""",
                                                 random_id=random.randint(0, 2 ** 64))
                            else:
                                user.change_function_work_status(True)
                                user.change_status_cl_dr_answers(sl_answers_client[user_message][1], True)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""{sl_answers_client[user_message][0]}""",
                                                 random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=user.give_user_id(),
                                             message=f"""Некорректно введены данные! Попробуйте еще раз.
                                                     Достумные возможности:
                                                     {client_answers}""",
                                             random_id=random.randint(0, 2 ** 64))
                    elif user.give_user_status() == second_user_status:
                        if user_message in sl_answers_driver:
                            if sl_answers_driver[user_message][1] == "forth":
                                db_sess = db_session.create_session()
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""ID всех ваших заказов:
                                        {give_all_receipts(user, db_sess)}""",
                                                 random_id=random.randint(0, 2 ** 64))
                            else:
                                user.change_function_work_status(True)
                                user.change_status_cl_dr_answers(sl_answers_driver[user_message][1], True)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""{sl_answers_driver[user_message][0]}""",
                                                 random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=user.give_user_id(),
                                             message=f"""Некорректно введены данные! Попробуйте еще раз.
                                                                             Достумные возможности:
                                                                             {driver_answers}""",
                                             random_id=random.randint(0, 2 ** 64))
                elif user.give_function_work_status():
                    db_sess = db_session.create_session()
                    if user_message == "!отмена":
                        roll_back(user)
                        give_functions(user, vk, driver_answers, client_answers)
                    elif user.give_user_status() == second_user_status:
                        d_request = user.give_special_request()
                        if user.give_status_cl_dr_answers("first"):
                            if d_request.first_status(user_message, db_sess, user.give_user_id()):
                                user.change_function_work_status(False)
                                user.change_status_cl_dr_answers("first", False)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Заказ закрыт""",
                                                 random_id=random.randint(0, 2 ** 64))
                                give_functions(user, vk, driver_answers, client_answers)
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Некорректно введены данные, либо у вас нет такого заказа
                                                        Попробуйте еще раз.
                                                     Необходимо указать id заказа""",
                                                 random_id=random.randint(0, 2 ** 64))
                        elif user.give_status_cl_dr_answers("second"):
                            if d_request.second_status(user_message, db_sess):
                                user.change_function_work_status(False)
                                user.change_status_cl_dr_answers("second", False)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message="""Заказ:
                                                            id:
                                                            status:
                                                            cost:
                                                            date_time_need:
                                                            date_time_close:=None
                                                            """, random_id=random.randint(0, 2 ** 64))
                                give_functions(user, vk, driver_answers, client_answers)
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Некорректно введены данные, либо у вас нет такого заказа
                                                        Попробуйте еще раз.
                                                     Необходимо указать id заказа""",
                                                 random_id=random.randint(0, 2 ** 64))
                        elif user.give_status_cl_dr_answers("third"):
                            if d_request.third_status(user_message, db_sess):
                                pass
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Некорректно введены данные! Попробуйте еще раз.
                                                             Необходимо указать id заказа""",
                                                 random_id=random.randint(0, 2 ** 64))
                    elif user.give_user_status() == first_user_status:
                        c_request = user.give_special_request()
                        if user.give_status_cl_dr_answers("first"):
                            if c_request.first_status(user_message, db_sess, user.give_user_id()):
                                user.change_function_work_status(False)
                                user.change_status_cl_dr_answers("first", False)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message="Заказ закрыт", random_id=random.randint(0, 2 ** 64))
                                give_functions(user, vk, driver_answers, client_answers)
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Некорректно введены данные, либо у вас нет такого заказа
                                                        Попробуйте еще раз.
                                                     Необходимо указать id заказа""",
                                                 random_id=random.randint(0, 2 ** 64))
                        elif user.give_status_cl_dr_answers("second"):
                            if c_request.second_status(user_message, db_sess):
                                user.change_function_work_status(False)
                                user.change_status_cl_dr_answers("second", False)
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message="""Заказ:
                                                            id:
                                                            status:
                                                            driver:
                                                            cost:
                                                            date_time_need:
                                                            date_time_close:=None     
                                                            """, random_id=random.randint(0, 2 ** 64))
                                give_functions(user, vk, driver_answers, client_answers)
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=f"""Некорректно введены данные, либо у вас нет такого заказа
                                                        Попробуйте еще раз.
                                                        Необходимо указать id заказа""",
                                                 random_id=random.randint(0, 2 ** 64))
                        elif user.give_status_cl_dr_answers("third"):
                            if c_request.third_status(user_message, s_s, db_sess):
                                a_1, a_2, c_car, time, driver, cost = c_request.third_status(user_message, s_s, db_sess)
                                if a_1 and a_2 and c_car and time and driver and cost:
                                    if driver.account_id:
                                        i = driver.account_id
                                        d = "vk.com/id" + str(i)
                                    else:
                                        d = driver.name
                                    vk.messages.send(user_id=user.give_user_id(),
                                                     message=f"""
                                                            Ваш заказ:
                                                            От: {a_1}
                                                            Куда: {a_2}
                                                            Авто: {c_car}
                                                            Время: {time}
                                                            Водитель: {d}
                                                            Цена: {cost}
                                                            """,
                                                     random_id=random.randint(0, 2 ** 64))
                                    vk.messages.send(user_id=user.give_user_id(),
                                                     message=f"""Все верно? Вы готовы оформить заказ?
                                                                (да/нет)""",
                                                     random_id=random.randint(0, 2 ** 64))
                                    user.change_status_special_answer("second", True)
                                else:
                                    vk.messages.send(user_id=user.give_user_id(),
                                                     message="""Неверно введены данные:
                                                     Возможно не нашеля водитель для вашего заказа или
                                                      вы ввели нераспознаваемый адрес или
                                                      у нас нет такого класса авто, подходящего вашим требованиям.
                                                      Приносим свои извинения по этому поводу.
                                                     """,
                                                     random_id=random.randint(0, 2 ** 64))
                                    vk.messages.send(user_id=user.give_user_id(),
                                                     message=sl_answers_client["новый заказ"][0],
                                                     random_id=random.randint(0, 2 ** 64))
                            else:
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message="Неверно введены данные",
                                                 random_id=random.randint(0, 2 ** 64))
                                vk.messages.send(user_id=user.give_user_id(),
                                                 message=sl_answers_client["новый заказ"][0],
                                                 random_id=random.randint(0, 2 ** 64))


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


def roll_back(user):
    user.change_function_work_status(False)
    user.change_status_cl_dr_answers("first", False)
    user.change_status_cl_dr_answers("second", False)
    user.change_status_cl_dr_answers("third", False)


def give_functions(user, vk, driver_answers, client_answers):
    if user.give_user_status() == second_user_status:
        vk.messages.send(user_id=user.give_user_id(),
                         message=f"""Достумные возможности:
                        {driver_answers}""", random_id=random.randint(0, 2 ** 64))
    elif user.give_user_status() == first_user_status:
        vk.messages.send(user_id=user.give_user_id(),
                         message=f"""Достумные возможности:
                                                    {client_answers}""",
                         random_id=random.randint(0, 2 ** 64))


def give_all_receipts(user, db_sess):
    if user.give_user_status() == second_user_status:
        user_id = db_sess.query(Drivers.id).filter(Drivers.account_id == user.give_user_id()).first()
        request = db_sess.query(Receipt.id).filter(Receipt.driver_id == user_id[0]).all()
    else:
        user_id = db_sess.query(Users.id).filter(Users.account_id == user.give_user_id()).first()
        request = db_sess.query(Receipt.id).filter(Receipt.user_id == user_id[0]).all()
    if request:
        return ", ".join(list(map(lambda x: str(x[0]), request)))
    else:
        return "У вас нет не одного заказа"


if __name__ == '__main__':
    main(TOKEN, ID)
