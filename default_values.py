from data.receipt_status import ReceiptStatus
from data.driver_status_in_receipt import DriverStatusInReceipt
from data.driver_status import DriverStatus
from data.class_car import ClassCar
from data.drivers import Drivers
from data import db_session


def add_default_values():
    db_sess = db_session.create_session()

    fill_class_car(db_sess)
    fill_driver_status(db_sess)
    fill_receipt_status(db_sess)
    fill_driver_status_in_receipt(db_sess)
    add_drivers(db_sess)

    db_sess.commit()


def fill_receipt_status(db_sess):
    first_receipt_status = ReceiptStatus()
    first_receipt_status.name = "В роботе"
    db_sess.add(first_receipt_status)

    second_receipt_status = ReceiptStatus()
    second_receipt_status.name = "Завершен"
    db_sess.add(second_receipt_status)


def fill_class_car(db_sess):
    first_class_car = ClassCar()
    first_class_car.name = "Эконом"
    first_class_car.cost = 1.0
    db_sess.add(first_class_car)

    second_class_car = ClassCar()
    second_class_car.name = "Бизнес"
    second_class_car.cost = 1.0
    db_sess.add(second_class_car)

    third_class_car = ClassCar()
    third_class_car.name = "Комфорт"
    third_class_car.cost = 1.0
    db_sess.add(third_class_car)

    fourth_class_car = ClassCar()
    fourth_class_car.name = 'Универсал'
    fourth_class_car.cost = 1.0
    db_sess.add(fourth_class_car)


def fill_driver_status(db_sess):
    first_driver_status = DriverStatus()
    first_driver_status.name = "Дневная"
    db_sess.add(first_driver_status)

    second__driver_status = DriverStatus()
    second__driver_status.name = "Ночная"
    db_sess.add(second__driver_status)


def fill_driver_status_in_receipt(db_sess):
    first_driver_status_in_receipt = DriverStatusInReceipt()
    first_driver_status_in_receipt.name = "Занят"
    db_sess.add(first_driver_status_in_receipt)

    second__driver_status_in_receipt = DriverStatusInReceipt()
    second__driver_status_in_receipt.name = "Свободен"
    db_sess.add(second__driver_status_in_receipt)


def add_drivers(db_sess):
    pass
