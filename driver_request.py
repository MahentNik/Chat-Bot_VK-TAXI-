from data.receipt import Receipt
from data.drivers import Drivers
import datetime as dt
from data.drivers import Drivers
from data.driver_status_in_receipt import DriverStatusInReceipt
from data.receipt_status import ReceiptStatus
import requests


class DriverRequest:
    def __init__(self):
        self.user_message = None

    def first_status(self, message, db_sess, user_id):
        u_i = db_sess.query(Drivers.id).filter(Drivers.account_id == user_id).first()
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message), Receipt.driver_id == u_i[0]).first()
            receipt_id = db_sess.query(Receipt.id).filter(Receipt.id == int(message), Receipt.driver_id == u_i[0])\
                .first()
        except Exception:
            return None
        if res and self.receipt_not_closed(db_sess, receipt_id):
            self.change_status_in_receipt(db_sess, res, u_i)
            return True
        return None

    def second_status(self, message, db_sess):
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message)).first()
        except Exception:
            return None
        if res:
            return self.get_receipt_info(res)
        else:
            return None

    def get_receipt_info(self, receipt):
        r_id = receipt.id
        r_status = receipt.status_id
        r_user = receipt.user_id
        cost = receipt.cost
        a = str(receipt.first_place_latitude), str(receipt.first_place_longitude)
        b = str(receipt.second_place_latitude), str(receipt.second_place_longitude)
        first_address = self.find_address(a)
        second_address = self.find_address(b)
        date_for_user = receipt.date_need_for_user
        date_create = receipt.date_now
        date_close = receipt.date_close
        return r_id, r_status, r_user, cost, first_address, second_address, date_for_user, date_create, date_close

    def third_status(self, message, db_sess):
        pass

    def change_status_in_receipt(self, db_sess, receipt, driver_id):
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
        r_user = receipt.user_id
        cost = receipt.cost
        a = receipt.first_place_latitude, receipt.first_place_longitude
        b = receipt.second_place_latitude, receipt.second_place_latitude
        first_address = self.find_address(a)
        second_address = self.find_address(b)
        date_for_user = receipt.date_need_for_user
        date_create = receipt.date_now
        date_close = receipt.date_close
        print(r_id, r_status, r_user, cost, first_address, second_address, date_for_user, date_create, date_close)

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
