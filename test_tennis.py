import csv
import json
from datetime import date, datetime, timedelta

import pytest
import sys
from os import remove
from io import StringIO
from unittest import mock

import tennis
import validators


@pytest.fixture
def tennis_court():
    court = tennis.TennisCourt()
    return court


def test_init(tennis_court):
    assert tennis_court.reservations == []


def test_is_period_overlaps(tennis_court):
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    reservation = tennis.Reservation('John', start_dt, end_dt)
    tennis_court.reservations.append(reservation)
    assert tennis_court.is_period_overlaps(start_dt, end_dt) is True

    start_dt_2 = end_dt - timedelta(minutes=1)
    end_dt_2 = end_dt + timedelta(minutes=1)
    assert tennis_court.is_period_overlaps(start_dt_2, end_dt_2) is True

    start_dt_3 = start_dt - timedelta(minutes=1)
    end_dt_3 = start_dt + timedelta(minutes=1)
    assert tennis_court.is_period_overlaps(start_dt_3, end_dt_3) is True

    start_dt_4 = end_dt
    end_dt_4 = end_dt + timedelta(minutes=1)
    assert tennis_court.is_period_overlaps(start_dt_4, end_dt_4) is False

    start_dt_5 = start_dt - timedelta(minutes=1)
    end_dt_5 = start_dt
    assert tennis_court.is_period_overlaps(start_dt_5, end_dt_5) is False


def test_is_date_not_available(tennis_court):
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    reservation = tennis.Reservation('John', start_dt, end_dt)
    tennis_court.reservations.append(reservation)
    assert tennis_court.is_date_not_available(start_dt) is True

    start_dt_2 = start_dt - timedelta(minutes=1)
    assert tennis_court.is_date_not_available(start_dt_2) is False

    start_dt_3 = end_dt
    assert tennis_court.is_date_not_available(start_dt_3) is False


@mock.patch('tennis.input')
def test_is_two_reservations_per_week(mock_input, tennis_court):
    mock_input.return_value = None
    # Same week: 22.05.2023 - 28.05.2023 as example
    start_dt_1 = datetime(2023, 5, 22, 0, 0)
    end_dt_1 = datetime(2023, 5, 22, 0, 1)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    start_dt_2 = datetime(2023, 5, 28, 23, 59)
    end_dt_2 = datetime(2023, 5, 29, 0, 0)
    reservation_2 = tennis.Reservation('John', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)

    start_dt_3 = datetime(2023, 5, 21, 23, 59)
    assert tennis_court.is_two_reservations_per_week('John', start_dt_3) is False

    start_dt_4 = datetime(2023, 5, 22, 0, 0)
    assert tennis_court.is_two_reservations_per_week('John', start_dt_4) is True

    start_dt_5 = datetime(2023, 5, 28, 23, 59)
    assert tennis_court.is_two_reservations_per_week('John', start_dt_5) is True

    start_dt_6 = datetime(2023, 5, 29, 0, 0)
    assert tennis_court.is_two_reservations_per_week('John', start_dt_6) is False


@mock.patch("tennis.datetime")
@mock.patch("tennis.input")
def test_is_one_hour_from_now(mock_input, mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 5, 29, 12, 00)
    mock_input.return_value = None

    start_dt_1 = datetime(2023, 5, 29, 12, 59)
    assert tennis.is_one_hour_from_now(start_dt_1) is True

    start_dt_2 = datetime(2023, 5, 29, 13, 00)
    assert tennis.is_one_hour_from_now(start_dt_2) is True

    start_dt_3 = datetime(2023, 5, 29, 13, 1)
    assert tennis.is_one_hour_from_now(start_dt_3) is False


def test_next_available_date(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00 (same day)
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    # reservation from 28.05.2023 13:00 - 29.05.2023 13:00 (next day)
    start_dt_2 = datetime(2023, 5, 28, 13, 0)
    end_dt_2 = datetime(2023, 5, 29, 13, 0)
    reservation_2 = tennis.Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)

    # reservation from 28.05.2023 13:30 - 15:00 (same day)
    start_dt_3 = datetime(2023, 5, 29, 13, 30)
    end_dt_3 = datetime(2023, 5, 29, 15, 0)
    reservation_3 = tennis.Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)

    # Next available datetime: 29.05.2023 13:00 (until 13:30).
    # Between reservation 2 and 3.
    next_available = tennis_court.next_available_datetime(start_dt_1)
    expected_datetime = datetime(2023, 5, 29, 13, 00)
    assert next_available == expected_datetime


def test_available_periods(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00 (same day)
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    # Available 30 minutes between reservation 1 and 2
    # reservation from 28.05.2023 13:30 - 29.05.2023 13:00 (next day)
    start_dt_2 = datetime(2023, 5, 28, 13, 30)
    end_dt_2 = datetime(2023, 5, 29, 13, 0)
    reservation_2 = tennis.Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)
    assert tennis_court.available_periods(end_dt_1) == [30]

    # Available 30 and 60 minutes between reservation 2 and 3
    # reservation from 29.05.2023 14:00 - 15:00 (same day)
    start_dt_3 = datetime(2023, 5, 29, 14, 00)
    end_dt_3 = datetime(2023, 5, 29, 15, 0)
    reservation_3 = tennis.Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)
    assert tennis_court.available_periods(end_dt_2) == [30, 60]

    # Available 30, 60, 90 minutes between reservation 3 and 4
    # reservation from 29.05.2023 16:00 - 17:00 (same day)
    start_dt_4 = datetime(2023, 5, 29, 16, 30)
    end_dt_4 = datetime(2023, 5, 29, 17, 0)
    reservation_4 = tennis.Reservation('Alice', start_dt_4, end_dt_4)
    tennis_court.reservations.append(reservation_4)
    assert tennis_court.available_periods(end_dt_3) == [30, 60, 90]

    # Available 3 hours between reservation 4 and 5 but should return [30, 60, 90]
    # reservation from 29.05.2023 20:00 - 21:00 (same day)
    start_dt_5 = datetime(2023, 5, 29, 20, 0)
    end_dt_5 = datetime(2023, 5, 29, 21, 0)
    reservation_5 = tennis.Reservation('Alan', start_dt_5, end_dt_5)
    tennis_court.reservations.append(reservation_5)
    assert tennis_court.available_periods(end_dt_3) == [30, 60, 90]


def test_make_reservation(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    # One day gap between reservation 1 and 3
    # reservation from 30.05.2023 12:30 - 30.05.2023 13:00
    start_dt_3 = datetime(2023, 5, 30, 12, 0)
    end_dt_3 = datetime(2023, 5, 30, 13, 0)
    reservation_3 = tennis.Reservation('Jenny', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)

    # New reservation to be made between reservation 1 and 3
    reservation_2 = ('Jack', datetime(2023, 5, 29, 12, 0), datetime(2023, 5, 29, 13, 0))
    tennis_court.make_reservation(*reservation_2)

    reservation_4 = ('Alan', datetime(2023, 5, 30, 12, 0), datetime(2023, 5, 30, 13, 0))
    tennis_court.make_reservation(*reservation_4)

    assert len(tennis_court.reservations) == 4
    assert tennis_court.reservations[1].name == 'Jack'
    assert tennis_court.reservations[1].start_date == datetime(2023, 5, 29, 12, 0)
    assert tennis_court.reservations[1].end_date == datetime(2023, 5, 29, 13, 0)


@mock.patch('tennis.input')
def test_is_reservation_cancelled(mock_input, tennis_court):
    mock_input.return_value = None
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    tennis_court.make_reservation('John', start_dt, end_dt)

    assert tennis_court.is_reservation_cancelled('John', start_dt) is True
    assert tennis_court.is_reservation_cancelled('Mike', start_dt) is False


@mock.patch('tennis.input')
def test_print_schedule(mock_input, tennis_court):
    mock_input.return_value = None
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    reservation_2 = tennis.Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)

    start_dt_3 = datetime(2023, 5, 28, 16, 0)
    end_dt_3 = datetime(2023, 5, 28, 17, 0)
    reservation_3 = tennis.Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)

    captured_output = StringIO()
    sys.stdout = captured_output

    tennis_court.print_schedule(date(2023, 5, 28), date(2023, 5, 28))

    output = captured_output.getvalue().strip()

    expected_output = ('Sunday, 28 May, 2023\n'
                       '* John 09:00 - 10:00\n'
                       '* Jenny 12:00 - 14:00\n'
                       '* Jack 16:00 - 17:00')

    assert output == expected_output


@mock.patch('tennis.input')
def test_save_schedule_csv(mock_input, tennis_court):
    mock_input.return_value = None
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    reservation_2 = tennis.Reservation('Alice', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)

    start_dt_3 = datetime(2023, 5, 29, 12, 0)
    end_dt_3 = datetime(2023, 5, 29, 13, 0)
    reservation_3 = tennis.Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)

    tennis_court.save_schedule(date(2023, 5, 28), date(2023, 5, 30), 'csv', 'schedule.csv')

    with open('schedule.csv', mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    expected_rows = [
        {'name': 'John', 'start_date': '28.05.2023 09:00', 'end_date': '28.05.2023 10:00'},
        {'name': 'Alice', 'start_date': '28.05.2023 12:00', 'end_date': '28.05.2023 14:00'},
        {'name': 'Jack', 'start_date': '29.05.2023 12:00', 'end_date': '29.05.2023 13:00'}
    ]
    assert rows == expected_rows
    remove('schedule.csv')  # # os.remove()


@mock.patch('tennis.input')
def test_save_schedule_json(mock_input, tennis_court):
    mock_input.return_value = None
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    reservation_1 = tennis.Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(reservation_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    reservation_2 = tennis.Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(reservation_2)

    start_dt_3 = datetime(2023, 5, 29, 12, 0)
    end_dt_3 = datetime(2023, 5, 29, 13, 0)
    reservation_3 = tennis.Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(reservation_3)

    tennis_court.save_schedule(date(2023, 5, 28), date(2023, 5, 30), 'json', 'schedule.json')

    with open('schedule.json', mode='r', encoding='utf-8') as json_file:
        saved_data = json.load(json_file)

    expected_data = {'28.05.2023': [{'end_time': '10:00', 'name': 'John', 'start_time': '09:00'},
                                    {'end_time': '14:00', 'name': 'Jenny', 'start_time': '12:00'}],
                     '29.05.2023': [{'end_time': '13:00', 'name': 'Jack', 'start_time': '12:00'}]}
    assert saved_data == expected_data
    remove('schedule.json')  # os.remove()


@mock.patch("tennis.input")
def test_main_menu(mock_input):
    mock_input.return_value = '1'
    assert tennis.main_menu() == '1'

    mock_input.return_value = '5'
    assert tennis.main_menu() == '5'

    mock_input.return_value = 'foo'
    assert tennis.main_menu() == 'foo'


@mock.patch("validators.input")
def test_name_validation(mock_input):
    mock_input.return_value = 'John'
    assert validators.name_validation('test') == 'John'

    mock_input.return_value = ''
    assert validators.name_validation('test') is None


@mock.patch("validators.input")
def test_datetime_validation(mock_input):
    mock_input.return_value = '29.05.2023 12:00'
    expected_datetime = datetime(2023, 5, 29, 12, 0)
    assert validators.datetime_validation('test') == expected_datetime

    mock_input.return_value = '29.05.2023 02:01'
    expected_datetime = datetime(2023, 5, 29, 2, 1)
    assert validators.datetime_validation('test') == expected_datetime

    mock_input.return_value = '30.02.2023 12:00'
    assert validators.datetime_validation('test') is None

    mock_input.return_value = '29.05.2023 12:1'
    assert validators.datetime_validation('test') is None

    mock_input.return_value = '29/05/2023 2:21'
    assert validators.datetime_validation('test') is None

    mock_input.return_value = '29.05.2023 12:61'
    assert validators.datetime_validation('test') is None

    mock_input.return_value = 'invalid datetime'
    assert validators.datetime_validation('test') is None


@mock.patch("validators.input")
def test_date_validation(mock_input):
    mock_input.return_value = '29.05.2023'
    expected_date = datetime(2023, 5, 29).date()
    assert validators.date_validation('test') == expected_date

    mock_input.return_value = '01.05.2023'
    expected_date = datetime(2023, 5, 1).date()
    assert validators.date_validation('test') == expected_date

    mock_input.return_value = '1.5.2023'
    assert validators.date_validation('test') is None

    mock_input.return_value = '1.05.2023'
    assert validators.date_validation('test') is None

    mock_input.return_value = 'invalid date'
    assert validators.date_validation('test') is None


@mock.patch("validators.input")
def test_period_validation(mock_input):
    available_periods = [1, 2, 3]
    mock_input.return_value = '2'
    assert validators.period_validation(available_periods) == 2

    mock_input.return_value = '5'
    assert validators.period_validation(available_periods) is None


@mock.patch("validators.input")
def test_agreement(mock_input):
    mock_input.return_value = 'yes'
    assert validators.agreement(datetime(2023, 5, 29)) == 'yes'

    mock_input.return_value = 'no'
    assert validators.agreement(datetime(2023, 5, 29)) == 'no'


@mock.patch("validators.input")
def test_validation_file_type(mock_input):
    mock_input.return_value = 'json'
    assert validators.validation_file_type() == 'json'

    mock_input.return_value = 'csv'
    assert validators.validation_file_type() == 'csv'

    mock_input.return_value = 'txt'
    assert validators.validation_file_type() is None
