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
    first_receipt_status.name = "в роботе"
    db_sess.add(first_receipt_status)

    second_receipt_status = ReceiptStatus()
    second_receipt_status.name = "завершен"
    db_sess.add(second_receipt_status)


def fill_class_car(db_sess):
    first_class_car = ClassCar()
    first_class_car.name = "эконом"
    first_class_car.cost = 1.0
    db_sess.add(first_class_car)

    second_class_car = ClassCar()
    second_class_car.name = "бизнес"
    second_class_car.cost = 1.0
    db_sess.add(second_class_car)

    third_class_car = ClassCar()
    third_class_car.name = "комфорт"
    third_class_car.cost = 1.0
    db_sess.add(third_class_car)

    fourth_class_car = ClassCar()
    fourth_class_car.name = 'универсал'
    fourth_class_car.cost = 1.0
    db_sess.add(fourth_class_car)


def fill_driver_status(db_sess):
    first_driver_status = DriverStatus()
    first_driver_status.name = "дневная"
    db_sess.add(first_driver_status)

    second__driver_status = DriverStatus()
    second__driver_status.name = "ночная"
    db_sess.add(second__driver_status)


def fill_driver_status_in_receipt(db_sess):
    first_driver_status_in_receipt = DriverStatusInReceipt()
    first_driver_status_in_receipt.name = "занят"
    db_sess.add(first_driver_status_in_receipt)

    second_driver_status_in_receipt = DriverStatusInReceipt()
    second_driver_status_in_receipt.name = "свободен"
    db_sess.add(second_driver_status_in_receipt)


def add_drivers(db_sess):
    first_driver = Drivers()
    first_driver.name = "Игорь"
    first_driver.location_latitude = "56.08211939293616"
    first_driver.location_longitude = "63.6054739873212"
    first_driver.class_car_id = 1
    first_driver.status_of_work_id = 1
    db_sess.add(first_driver)

    second_driver = Drivers()
    second_driver.name = "Нурлан"
    second_driver.location_latitude = "55.44127205252368"
    second_driver.location_longitude = "65.34396703163385"
    second_driver.class_car_id = 2
    second_driver.status_of_work_id = 2
    db_sess.add(second_driver)

    third_driver = Drivers()
    third_driver.name = "Рустам"
    third_driver.location_latitude = "57.1612607931535"
    third_driver.location_longitude = "65.50347036752743"
    third_driver.class_car_id = 3
    third_driver.status_of_work_id = 1
    db_sess.add(third_driver)

    fourth_driver = Drivers()
    fourth_driver.name = "Эмир"
    fourth_driver.location_latitude = "56.09063949527911"
    fourth_driver.location_longitude = "63.62477822914894"
    fourth_driver.class_car_id = 4
    fourth_driver.status_of_work_id = 2
    db_sess.add(fourth_driver)
