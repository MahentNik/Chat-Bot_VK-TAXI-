from data.receipt import Receipt


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

    def first_status(self, message, db_sess):
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message)).first()
        except Exception:
            return None
        if res:
            self.user_message = message
            return True
        else:
            return None

    def second_status(self, message, db_sess):
        try:
            res = db_sess.query(Receipt).filter(Receipt.id == int(message)).first()
        except Exception:
            return None
        if res:
            self.user_message = message
            return True
        else:
            return None

    def third_status(self, message, s_s):
        try:
            address_1, address_2, class_car, data_time = message.split(s_s)

        except Exception:
            return None

    def check_address(self, address):
        pass

    def give_latitude_longitude(self, address):
        pass

    def add_receipt(self):
        pass
