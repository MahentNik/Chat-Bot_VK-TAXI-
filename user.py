import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from data.users import Users
from data.drivers import Drivers

first_user_status = "client"
second_user_status = "driver"


class User:
    def __init__(self):
        self.user_status = None
        self.user_id = None
        self.special_answers_activated = {
            "first": False,
            "second": False,
            "third": False
        }
        self.client_answers_activated = {
            "first": False,
            "second": False,
            "third": False
        }
        self.driver_answers_activated = {
            "first": False,
            "second": False,
            "third": False
        }
        self.function_work_status = False
        self.registration_status = False  # пройдена ли регистрация
        self.request_driver = None
        self.special_request = None

    def give_special_request(self):
        return self.special_request

    def change_special_request(self, request):
        self.special_request = request

    def change_request_driver(self, request):
        self.request_driver = request

    def give_request_driver(self):
        return self.request_driver

    def change_status_special_answer(self, answer, status):
        self.special_answers_activated[answer] = status

    def change_status_cl_dr_answers(self, answer, status):
        if self.give_user_status() == first_user_status:
            self.client_answers_activated[answer] = status
        elif self.give_user_status() == second_user_status:
            self.driver_answers_activated[answer] = status

    def give_status_cl_dr_answers(self, answer):
        if self.give_user_status() == first_user_status:
            return self.client_answers_activated[answer]
        elif self.give_user_status() == second_user_status:
            return self.driver_answers_activated[answer]

    def give_status_special_answers(self, answer):
        return self.special_answers_activated[answer]

    def change_registration_status(self, status=True):
        self.registration_status = status

    def change_function_work_status(self, status):
        self.function_work_status = status

    def give_function_work_status(self):
        return self.function_work_status

    def give_registration_status(self):
        return self.registration_status

    def add_user_id(self, i):
        self.user_id = i

    def take_user_id(self, event):
        self.user_id = str(event.object['from_id'])

    def change_user_status(self, status):
        self.user_status = status

    def give_user_id(self):
        return self.user_id

    def give_user_message(self, event):
        return event.object.message['text']

    def give_user_status(self):
        return self.user_status

    def give_user_name(self, vk):
        user = vk.users.get(user_id=self.give_user_id())
        user_name = user[0]['first_name']
        return user_name

    def check_data_base(self, session):
        request = None

        if self.user_status == first_user_status:
            request = session.query(Users).filter(Users.account_id == self.user_id).first()
        elif self.user_status == second_user_status:
            request = session.query(Drivers).filter(Drivers.account_id == self.user_id).first()

        if request:
            return True
        else:
            return False

    def add_to_data_base(self, session):
        if self.give_user_status() == first_user_status:
            u = Users()
            u.account_id = self.give_user_id()
            session.add(u)
            session.commit()
