import requests
from data.drivers import Drivers
from data import db_session
from data.class_car import ClassCar
from data.driver_status import DriverStatus


class RequestDriver:
    def __init__(self, class_car, driver_status_of_work):
        self.address = ""
        self.class_car = class_car
        self.driver_status = driver_status_of_work

    def find_address(self, address):
        d = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
             "geocode": address,
             "format": "json"}
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
        try:
            response = requests.get(geocoder_request, params=d)
            json_res = response.json()
            res_a = json_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                "metaDataProperty"]["GeocoderMetaData"]["text"]
        except Exception:
            return None
        self.address = res_a
        return res_a

    def add_driver_info(self, user, vk):
        db_sess = db_session.create_session()

        latitude, longitude = self.get_pos()
        id_class_car = db_sess.query(ClassCar.id).filter(ClassCar.name == self.class_car).first()
        id_driver_status = db_sess.query(DriverStatus.id).filter(DriverStatus.name == self.driver_status).first()

        driver = Drivers()
        driver.account_id = user.give_user_id()
        driver.name = user.give_user_name(vk)
        driver.location_latitude = latitude
        driver.location_longitude = longitude
        driver.status_of_work_id = id_driver_status[0]
        driver.class_car_id = id_class_car[0]
        db_sess.add(driver)

        db_sess.commit()

    def get_pos(self):
        d = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
             "geocode": self.address,
             "format": "json"}
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_request, params=d)
        json_res = response.json()
        la, lo = json_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            "pos"].split()
        return la, lo

    def give_address(self):
        return self.address

    def give_class_car(self):
        return self.class_car

    def give_driver_status(self):
        return self.driver_status
