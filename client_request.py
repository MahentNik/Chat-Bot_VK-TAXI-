from data.receipt import Receipt
from data.users import Users
import datetime as dt
from data.drivers import Drivers
from data.driver_status_in_receipt import DriverStatusInReceipt
from data.receipt_status import ReceiptStatus
import requests
import math
from data.class_car import ClassCar
from data.driver_status import DriverStatus


class ClientRequest:
    def __init__(self):
        self.user_message = None
        self.receipt_info = {"address_1": "",
                             "address_2": "",
                             "cost": "",
                             "class_car": "",
                             "driver": "",
                             "date_time": ""
                             }

    def give_receipt_info(self):
        return self.receipt_info["address_1"], self.receipt_info["address_2"], self.receipt_info["class_car"], \
               self.receipt_info["date_time"], self.receipt_info["driver"], self.receipt_info["cost"]

    def first_status(self, message, db_sess, user_id):
        u_i = db_sess.query(Users.id).filter(Users.account_id == user_id).first()
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message), Receipt.user_id == u_i[0]).first()
            receipt_id = db_sess.query(Receipt.id).filter(Receipt.id == int(message), Receipt.user_id == u_i[0]).first()
        except Exception:
            return None
        if res and self.receipt_not_closed(db_sess, receipt_id):
            self.change_status_in_receipt(db_sess, res, receipt_id)
            return True
        return None

    def second_status(self, message, db_sess):
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message)).first()
        except Exception:
            return None
        if res:
            return self.get_info_about_receipt(res)
        else:
            return None

    def get_info_about_receipt(self, res):
        pass

    def third_status(self, message, s_s, db_sess):
        try:
            address_1, address_2, class_car, data_time = message.split(s_s)
            res_a_1 = self.check_address(address_1)
            res_a_2 = self.check_address(address_2)
            if not self.check_date(data_time):
                raise Exception
            if not self.check_class_car(db_sess, class_car):
                raise Exception
            c_c = class_car
            date = data_time
            cost = self.calculate_cost(c_c, res_a_1, res_a_2, db_sess)
            driver = self.find_driver(date, c_c, db_sess, res_a_1)
            self.receipt_info["address_1"] = res_a_1
            self.receipt_info["address_2"] = res_a_2
            self.receipt_info["cost"] = cost
            self.receipt_info["class_car"] = c_c
            self.receipt_info["driver"] = driver
            self.receipt_info["date_time"] = date
        except Exception:
            return False
        return res_a_1, res_a_2, c_c, date, driver, cost


    def take_status_driver(self, date):
        given = dt.datetime.strptime(date, "%y/%m/%d %H:%M")
        hour = given.hour
        if 18 > int(hour) > 6:
            return "дневная"
        else:
            return "ночная"

    def find_driver(self, date, class_car, db_sess, res_a_1):
        class_car_id = db_sess.query(ClassCar.id).filter(ClassCar.name == class_car).first()
        driver_status = self.take_status_driver(date)
        driver_status_in_receipt = db_sess.query(DriverStatusInReceipt.id) \
            .filter(DriverStatusInReceipt.name == "свободен").first()
        driver_s = db_sess.query(DriverStatus.id).filter(DriverStatus.name == driver_status).first()
        drivers = db_sess.query(Drivers).filter(Drivers.class_car_id == class_car_id[0]
                                                , Drivers.status_of_work_id == driver_s[0],
                                                Drivers.status_on_receipt_id == driver_status_in_receipt[0]).all()
        sp = []
        sl = {}
        la, lo = self.get_coordinates(res_a_1)
        b = float(la), float(lo)
        if drivers:
            for i in drivers:
                dist = self.calculate_distance((float(i.location_latitude), float(i.location_longitude)), b)
                sp.append(dist)
                sl[dist] = i
            min_dist = min(sp)
            return sl[min_dist]
        return False

    def calculate_cost(self, class_car, a_1, a_2, db_sess):
        min_cost = 40
        la_1, lo_1 = self.get_coordinates(a_1)
        la_2, lo_2 = self.get_coordinates(a_2)
        a = float(la_1), float(lo_1)
        b = float(la_2), float(lo_2)
        distance = self.calculate_distance(a, b)
        k = 10
        cost_class_car = db_sess.query(ClassCar.cost).filter(ClassCar.name == class_car).first()
        cost = float(distance * k) + min_cost + int(cost_class_car[0])
        cost = math.ceil(cost)
        return cost

    def check_address(self, address):
        try:
            d = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                 "geocode": address,
                 "format": "json"}
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
            response = requests.get(geocoder_request, params=d)
            json_res = response.json()
            res_address = json_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                "metaDataProperty"]["GeocoderMetaData"]["text"]
        except Exception:
            return False
        return res_address

    def check_class_car(self, db_sess, class_car):
        try:
            res = db_sess.query(ClassCar.id).filter(ClassCar.name == class_car).first()
        except Exception:
            return False
        if res:
            return res
        return False

    def get_coordinates(self, address):
        try:
            d = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                 "geocode": address,
                 "format": "json"}
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
            response = requests.get(geocoder_request, params=d)
            json_res = response.json()
            la, lo = json_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                "pos"].split()
        except Exception:
            return False
        return la, lo

    def give_latitude_longitude(self, address):
        pass

    def add_new_receipt(self, db_sess, user):
        status_id = db_sess.query(ReceiptStatus.id).filter(ReceiptStatus.name == "в роботе").first()
        status_on_receipt = db_sess.query(DriverStatusInReceipt.id).filter(
            DriverStatusInReceipt.name == "занят").first()
        print(status_on_receipt)
        user_id = db_sess.query(Users.id).filter(Users.account_id == user.give_user_id()).first()
        driver = self.receipt_info["driver"]
        driver_id = int(driver.id)
        d = db_sess.query(Drivers).filter(Drivers.id == driver_id).first()
        d.status_on_receipt_id = status_on_receipt[0]
        db_sess.commit()

        date = self.receipt_info["date_time"]
        date_time = dt.datetime.strptime(date, "%y/%m/%d %H:%M")

        cost = self.receipt_info["cost"]
        latitude_1, longitude_1 = self.get_coordinates(self.receipt_info["address_1"])
        latitude_2, longitude_2 = self.get_coordinates(self.receipt_info["address_2"])
        a = float(latitude_1), float(longitude_1)
        b = float(latitude_2), float(longitude_2)

        receipt = Receipt()
        receipt.date_now = dt.datetime.now()
        receipt.status_id = status_id[0]
        receipt.user_id = user_id[0]
        receipt.driver_id = driver_id
        receipt.cost = cost
        receipt.first_place_latitude = a[0]
        receipt.first_place_longitude = a[1]
        receipt.second_place_latitude = b[0]
        receipt.second_place_longitude = b[1]
        receipt.date_need_for_user = date_time
        db_sess.add(receipt)
        db_sess.commit()

    def change_status_in_receipt(self, db_sess, receipt, receipt_id):
        driver_id = db_sess.query(Receipt.driver_id).filter(Receipt.id == receipt_id[0]).first()
        driver = db_sess.query(Drivers).filter(Drivers.id == driver_id[0]).first()
        status_receipt_id = db_sess.query(ReceiptStatus.id).filter(ReceiptStatus.name == "завершен").first()
        status_driver_id = db_sess.query(DriverStatusInReceipt.id).filter(DriverStatusInReceipt.name == "свободен") \
            .first()
        driver.status_on_receipt_id = status_driver_id[0]
        receipt.status_id = status_receipt_id[0]
        receipt.date_close = dt.datetime.now()
        db_sess.commit()

    def receipt_not_closed(self, db_sess, receipt_id):
        status_receipt_id = db_sess.query(ReceiptStatus.id).filter(ReceiptStatus.name == "завершен").first()
        res = db_sess.query(Receipt.status_id).filter(Receipt.id == receipt_id[0]).first()
        if res != status_receipt_id:
            return True
        return False

    def get_info_about_receipt(self, receipt):
        r_id = receipt.id
        r_status = receipt.status_id
        r_driver = receipt.user_id
        cost = receipt.cost
        a = receipt.first_place_latitude, receipt.first_place_longitude
        b = receipt.second_place_latitude, receipt.second_place_latitude
        first_address = self.find_address(a)
        second_address = self.find_address(b)
        date_for_user = receipt.date_need_for_user
        date_create = receipt.date_now
        date_close = receipt.date_close
        print(r_id, r_status, r_driver, cost, first_address, second_address, date_for_user, date_create, date_close)

    def find_address(self, coordinates):
        try:
            d = {"apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                 "geocode": ",".join(coordinates),
                 "format": "json"}
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
            response = requests.get(geocoder_request, params=d)
            json_res = response.json()
            res_address = json_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                "metaDataProperty"]["GeocoderMetaData"]["text"]
        except Exception:
            return None
        return res_address

    def calculate_distance(self, a, b):
        radius = 6371
        distance = 2 * radius * math.asin(math.sqrt(math.sin((math.radians(b[0]) - math.radians(a[0])) / 2) ** 2
                                                    + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
                                                    * math.sin((math.radians(b[1]) - math.radians(a[1])) / 2) ** 2))
        return distance

    def check_date(self, date):
        try:
            given = dt.datetime.strptime(date, "%y/%m/%d %H:%M")
            delta_time = dt.timedelta(minutes=10)
            current_time = dt.datetime.now()
            if given < current_time + delta_time:
                return False
            return True
        except Exception:
            return False
