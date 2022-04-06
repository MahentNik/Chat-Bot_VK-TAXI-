import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random


def main():
    vk_session = vk_api.VkApi(
        token="44800dbb397fec66933604dea75498f5bce42c0fa027e8506f99e1af7578f2fb4948c7fe2a210cb75371b")

    longpoll = VkBotLongPoll(vk_session, "212291557")

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            pass


if __name__ == '__main__':
    main()
