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
        self.registration_status = False  # пройдена ли регистрация

    def change_registration_status(self):
        self.registration_status = True

    def give_registration_status(self):
        return self.registration_status

    def take_user_id(self, event):
        self.user_id = str(event.obj['from_id'])

    def change_user_status(self, status):
        self.user_status = status

    def give_user_id(self):
        return self.user_id

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
        if self.user_status == first_user_status:
            session.add(user)
        elif self.user_status == second_user_status:
            session.add(user)
        session.commit()
