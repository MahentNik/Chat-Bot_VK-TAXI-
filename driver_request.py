from data.receipt import Receipt


class DriverRequest:
    def __init__(self):
        self.user_message = None

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

    def third_status(self, message, db_sess):
        pass
