import csv
import json
import os
import pytest
import sys
from datetime import date, datetime, timedelta
from io import StringIO
from tennis import TennisCourt, Reservation
from unittest import mock


@pytest.fixture
def tennis_court():
    court = TennisCourt()
    return court


def test_init(tennis_court):
    assert tennis_court.reservations == []


def test_period_overlaps(tennis_court):
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    rsvn = Reservation('John', start_dt, end_dt)
    tennis_court.reservations.append(rsvn)
    assert tennis_court.period_overlaps(start_dt, end_dt) is True

    start_dt_2 = end_dt - timedelta(minutes=1)
    end_dt_2 = end_dt + timedelta(minutes=1)
    assert tennis_court.period_overlaps(start_dt_2, end_dt_2) is True

    start_dt_3 = start_dt - timedelta(minutes=1)
    end_dt_3 = start_dt + timedelta(minutes=1)
    assert tennis_court.period_overlaps(start_dt_3, end_dt_3) is True

    start_dt_4 = end_dt
    end_dt_4 = end_dt + timedelta(minutes=1)
    assert tennis_court.period_overlaps(start_dt_4, end_dt_4) is False

    start_dt_5 = start_dt - timedelta(minutes=1)
    end_dt_5 = start_dt
    assert tennis_court.period_overlaps(start_dt_5, end_dt_5) is False


def test_date_not_available(tennis_court):
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    rsvn = Reservation('John', start_dt, end_dt)
    tennis_court.reservations.append(rsvn)
    assert tennis_court.date_not_available(start_dt) is True

    start_dt_2 = start_dt - timedelta(minutes=1)
    assert tennis_court.date_not_available(start_dt_2) is False

    start_dt_3 = end_dt
    assert tennis_court.date_not_available(start_dt_3) is False


def test_two_reservations_per_week(tennis_court):
    # Same week: 22.05.2023 - 28.05.2023 as example
    start_dt_1 = datetime(2023, 5, 22, 0, 0)
    end_dt_1 = datetime(2023, 5, 22, 0, 1)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    start_dt_2 = datetime(2023, 5, 28, 23, 59)
    end_dt_2 = datetime(2023, 5, 29, 0, 0)
    rsvn_2 = Reservation('John', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)

    start_dt_3 = datetime(2023, 5, 21, 23, 59)
    assert tennis_court.two_reservations_per_week('John', start_dt_3) is False

    start_dt_4 = datetime(2023, 5, 22, 0, 0)
    assert tennis_court.two_reservations_per_week('John', start_dt_4) is True

    start_dt_5 = datetime(2023, 5, 28, 23, 59)
    assert tennis_court.two_reservations_per_week('John', start_dt_5) is True

    start_dt_5 = datetime(2023, 5, 29, 0, 0)
    assert tennis_court.two_reservations_per_week('John', start_dt_5) is False


@mock.patch("tennis.datetime")
def test_one_hour_from_now_or_less(mock_datetime, tennis_court):
    mock_datetime.now.return_value = datetime(2023, 5, 29, 12, 00)

    start_dt_1 = datetime(2023, 5, 29, 12, 59)
    assert tennis_court.one_hour_from_now_or_less(start_dt_1) is True

    start_dt_1 = datetime(2023, 5, 29, 13, 00)
    assert tennis_court.one_hour_from_now_or_less(start_dt_1) is True

    start_dt_1 = datetime(2023, 5, 29, 13, 1)
    assert tennis_court.one_hour_from_now_or_less(start_dt_1) is False


def test_next_available_date(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00 (same day)
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    # reservation from 28.05.2023 13:00 - 29.05.2023 13:00 (next day)
    start_dt_2 = datetime(2023, 5, 28, 13, 0)
    end_dt_2 = datetime(2023, 5, 29, 13, 0)
    rsvn_2 = Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)

    # reservation from 28.05.2023 13:30 - 15:00 (same day)
    start_dt_3 = datetime(2023, 5, 29, 13, 30)
    end_dt_3 = datetime(2023, 5, 29, 15, 0)
    rsvn_3 = Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)

    # Next available datetime: 29.05.2023 13:00 (until 13:30).
    # Between reservation 2 and 3.
    next_available = tennis_court.next_available_datetime(start_dt_1)
    expected_datetime = datetime(2023, 5, 29, 13, 00)
    assert next_available == expected_datetime


def test_available_periods(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00 (same day)
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    # Available 30 minutes between reservation 1 and 2
    # reservation from 28.05.2023 13:30 - 29.05.2023 13:00 (next day)
    start_dt_2 = datetime(2023, 5, 28, 13, 30)
    end_dt_2 = datetime(2023, 5, 29, 13, 0)
    rsvn_2 = Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)
    assert tennis_court.available_periods(end_dt_1) == [30]

    # Available 30 and 60 minutes between reservation 2 and 3
    # reservation from 29.05.2023 14:00 - 15:00 (same day)
    start_dt_3 = datetime(2023, 5, 29, 14, 00)
    end_dt_3 = datetime(2023, 5, 29, 15, 0)
    rsvn_3 = Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)
    assert tennis_court.available_periods(end_dt_2) == [30, 60]

    # Available 30, 60, 90 minutes between reservation 3 and 4
    # reservation from 29.05.2023 16:00 - 17:00 (same day)
    start_dt_4 = datetime(2023, 5, 29, 16, 30)
    end_dt_4 = datetime(2023, 5, 29, 17, 0)
    rsvn_4 = Reservation('Alice', start_dt_4, end_dt_4)
    tennis_court.reservations.append(rsvn_4)
    assert tennis_court.available_periods(end_dt_3) == [30, 60, 90]

    # Available 3 hours between reservation 4 and 5 but should return [30, 60, 90]
    # reservation from 29.05.2023 20:00 - 21:00 (same day)
    start_dt_5 = datetime(2023, 5, 29, 20, 0)
    end_dt_5 = datetime(2023, 5, 29, 21, 0)
    rsvn_5 = Reservation('Alan', start_dt_5, end_dt_5)
    tennis_court.reservations.append(rsvn_5)
    assert tennis_court.available_periods(end_dt_3) == [30, 60, 90]


def test_make_reservation(tennis_court):
    # reservation from 28.05.2023 12:00 - 13:00
    start_dt_1 = datetime(2023, 5, 28, 12, 0)
    end_dt_1 = datetime(2023, 5, 28, 13, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    # One day gap between reservation 1 and 3
    # reservation from 30.05.2023 12:30 - 30.05.2023 13:00
    start_dt_3 = datetime(2023, 5, 30, 12, 0)
    end_dt_3 = datetime(2023, 5, 30, 13, 0)
    rsvn_3 = Reservation('Jenny', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)

    # New reservation to be made between reservation 1 and 3
    rsvn_2 = ('Jack', datetime(2023, 5, 29, 12, 0), datetime(2023, 5, 29, 13, 0))
    tennis_court.make_reservation(*rsvn_2)

    rsvn_4 = ('Alan', datetime(2023, 5, 30, 12, 0), datetime(2023, 5, 30, 13, 0))
    tennis_court.make_reservation(*rsvn_4)

    assert len(tennis_court.reservations) == 4
    assert tennis_court.reservations[1].name == 'Jack'
    assert tennis_court.reservations[1].start_date == datetime(2023, 5, 29, 12, 0)
    assert tennis_court.reservations[1].end_date == datetime(2023, 5, 29, 13, 0)


def test_cancel_reservation(tennis_court):
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(hours=1)
    tennis_court.make_reservation('John', start_dt, end_dt)

    assert tennis_court.cancel_reservation('John', start_dt) is True
    assert tennis_court.cancel_reservation('Mike', start_dt) is False


def test_print_schedule(tennis_court):
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    rsvn_2 = Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)

    start_dt_3 = datetime(2023, 5, 28, 16, 0)
    end_dt_3 = datetime(2023, 5, 28, 17, 0)
    rsvn_3 = Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)

    captured_output = StringIO()
    sys.stdout = captured_output

    tennis_court.print_schedule(date(2023, 5, 28), date(2023, 5, 28))

    output = captured_output.getvalue().strip()

    expected_output = ('Sunday, 28 May, 2023:\n'
                       '* John 09:00 - 10:00\n'
                       '* Jenny 12:00 - 14:00\n'
                       '* Jack 16:00 - 17:00')

    assert output == expected_output


def test_save_schedule_csv(tennis_court, tmp_path):
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    rsvn_2 = Reservation('Alice', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)

    start_dt_3 = datetime(2023, 5, 29, 12, 0)
    end_dt_3 = datetime(2023, 5, 29, 13, 0)
    rsvn_3 = Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)

    tennis_court.save_schedule(date(2023, 5, 28), date(2023, 5, 30), 'csv', 'schedule.csv')

    with open('schedule.csv', mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    expected_rows = [
        {'name': 'John', 'start_date': '28.05.2023 09:00', 'end_date': '28.05.2023 10:00'},
        {'name': 'Alice', 'start_date': '28.05.2023 12:00', 'end_date': '28.05.2023 14:00'},
        {'name': 'Jack', 'start_date': '29.05.2023 12:00', 'end_date': '29.05.2023 13:00'}
    ]
    csv_file.close()
    assert rows == expected_rows
    os.remove('schedule.csv')


def test_save_schedule_json(tennis_court, tmp_path):
    start_dt_1 = datetime(2023, 5, 28, 9, 0)
    end_dt_1 = datetime(2023, 5, 28, 10, 0)
    rsvn_1 = Reservation('John', start_dt_1, end_dt_1)
    tennis_court.reservations.append(rsvn_1)

    start_dt_2 = datetime(2023, 5, 28, 12, 0)
    end_dt_2 = datetime(2023, 5, 28, 14, 0)
    rsvn_2 = Reservation('Jenny', start_dt_2, end_dt_2)
    tennis_court.reservations.append(rsvn_2)

    start_dt_3 = datetime(2023, 5, 29, 12, 0)
    end_dt_3 = datetime(2023, 5, 29, 13, 0)
    rsvn_3 = Reservation('Jack', start_dt_3, end_dt_3)
    tennis_court.reservations.append(rsvn_3)

    tennis_court.save_schedule(date(2023, 5, 28), date(2023, 5, 30), 'json', 'schedule.json')

    with open('schedule.json', mode='r', encoding='utf-8') as json_file:
        saved_data = json.load(json_file)

    expected_data = {'28.05.2023': [{'end_time': '10:00', 'name': 'John', 'start_time': '09:00'},
                                    {'end_time': '14:00', 'name': 'Jenny', 'start_time': '12:00'}],
                     '29.05.2023': [{'end_time': '13:00', 'name': 'Jack', 'start_time': '12:00'}]}
    json_file.close()
    assert saved_data == expected_data
    os.remove('schedule.json')
