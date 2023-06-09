import csv
import json
import sqlalchemy
import re
from datetime import date, datetime, timedelta
from models import Base, Reservations
from sqlalchemy.orm import sessionmaker
from typing import Optional


class Reservation:
    def __init__(self, name, start_dt, end_dt):
        self.name = name
        self.start_date = start_dt
        self.end_date = end_dt


class TennisCourt:
    def __init__(self):
        self.reservations = []
        connection_string = 'sqlite:///tennis_court.db'
        engine = sqlalchemy.create_engine(connection_string)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.session = session()

    def period_overlaps(self, start_dt: datetime, end_dt: datetime) -> bool:
        """
        Checks if the given time period overlaps with any existing reservations.

        Parameters
        ----------
        start_dt : datetime
            The start date and time of the time period.
        end_dt : datetime
            The end date and time of the time period.

        Returns
        -------
        bool
            True if there is an overlap, False otherwise.
        """
        for rsvn in self.reservations:
            if start_dt < rsvn.end_date and end_dt > rsvn.start_date:
                return True
        return False

    def date_not_available(self, start_dt: datetime) -> bool:
        """
        Checks if the given date and time is already reserved.

        Parameters
        ----------
        start_dt : datetime
            The start date and time to check.

        Returns
        -------
        bool
            True if the date and time is not available, False otherwise.
        """
        for rsvn in self.reservations:
            if rsvn.start_date <= start_dt < rsvn.end_date:
                return True
        return False

    def two_reservations_per_week(self, name: str, start_dt: datetime) -> bool:
        """
        Checks if the given person has already made two reservations in the same week.

        Parameters
        ----------
        name : str
            The name of the person.
        start_dt : datetime
            The start date and time of the reservation.

        Returns
        -------
        bool
            True if the person has reached the reservation limit, False otherwise.
        """
        counter = 0
        week_no = datetime.isocalendar(start_dt).week
        for rsvn in self.reservations:
            if name == rsvn.name and datetime.isocalendar(rsvn.start_date).week == week_no:
                counter += 1
                if counter > 1:
                    input(f'Sorry, {name} has reached the reservation limit for this week (2).\n'
                          f'Press enter to return to main menu.')
                    return True
        return False

    def next_available_datetime(self, start_dt: datetime) -> datetime:
        """
        Finds the next available date and time for a reservation.

        Parameters
        ----------
        start_dt : datetime
            The start date and time of the requested reservation.

        Returns
        -------
        datetime
            The next available date and time for a reservation.
        """
        closest_time = start_dt
        for rsvn in self.reservations:
            if rsvn.start_date >= closest_time + timedelta(minutes=30):
                return closest_time
            elif closest_time <= rsvn.end_date:
                closest_time = rsvn.end_date
        return closest_time

    def available_periods(self, start_dt: datetime) -> list[int]:
        """
        Finds available periods limited by 30, 60, 90 minutes for a reservation starting from the given datetime.

        Parameters
        ----------
        start_dt : datetime
            The start date and time of the reservation.

        Returns
        -------
        list[int]
            A list of available periods in minutes.
        """
        avl_periods = []
        periods = [30, 60, 90]
        for period in periods:
            end_dt = start_dt + timedelta(minutes=period)
            if self.period_overlaps(start_dt, end_dt):
                break 
            avl_periods.append(period)
        print('\nHow long would you like to book court?\n'
              'Available periods:')
        for i, period in enumerate(avl_periods, start=1):
            print(f'{i}) {period} Minutes')
        return avl_periods

    def make_reservation(self, name: str, start_dt: datetime, end_dt: datetime) -> None:
        """
        Makes a reservation for the specified name and time slot into tennis court reservations.

        Parameters
        ----------
        name : str
            The name of the person making the reservation.
        start_dt : datetime
            The start date and time of the reservation.
        end_dt : datetime
            The end date and time of the reservation.

        Returns
        -------
        None
        """
        for idx, rsvn in enumerate(self.reservations):
            if rsvn.start_date > start_dt:
                reservation = Reservation(name, start_dt, end_dt)
                self.reservations.insert(idx, reservation)
                return None
        reservation = Reservation(name, start_dt, end_dt)
        self.reservations.append(reservation)
        return None

    def cancel_reservation(self, name: str, start_dt: datetime) -> bool:
        """
        Checks if reservation already exists for given name, date and time.
        Cancels a reservation for the specified name and start date.

        Parameters
        ----------
        name : str
            The name of the person who made the reservation.
        start_dt : datetime
            The start date and time of the reservation to be canceled.

        Returns
        -------
        bool
            True if the reservation was successfully canceled, False otherwise.
        """
        for rsvn in self.reservations:
            if name == rsvn.name and start_dt == rsvn.start_date:
                self.reservations.remove(rsvn)
                return True
        return False

    def print_schedule(self, start_dt: date, end_dt: date) -> None:
        """
        Prints the schedule of reservations between the specified start and end date.

        Parameters
        ----------
        start_dt : date
            The start date to filter reservations.
        end_dt : date
            The end date to filter reservations.

        Returns
        -------
        None
        """
        current_date = start_dt
        while current_date <= end_dt:
            if current_date == date.today():
                print('Today')
            elif current_date == date.today() + timedelta(days=1):
                print('Tomorrow')
            else:
                print(current_date.strftime("%A, %d %B, %Y:"))
                
            reservations = [rsvn for rsvn in self.reservations if rsvn.start_date.date() == current_date]
            if not reservations:
                print("No reservations\n")
            else:
                for rsvn in reservations:
                    print(f"* {rsvn.name} {rsvn.start_date.strftime('%H:%M')} - {rsvn.end_date.strftime('%H:%M')}")
                print()
            current_date += timedelta(days=1)
        input('Schedule printed.\n'
              'Press enter to return to main menu.')
        return None

    def save_schedule(self, start_dt: date, end_dt: date, file_format: str, save_file_name: str) -> None:
        """
        Saves the schedule of reservations between start and end date to csv or json file.

        Parameters
        ----------
        start_dt : date
            The start date to filter reservations.
        end_dt : date
            The end date to filter reservations.
        file_format : str
            The format of the file to save the schedule. Only 'json' and 'csv' are supported.
        save_file_name : str
            The name of the file to save the schedule.

        Returns
        -------
        None
        """
        start_date = start_dt
        end_date = end_dt
        filtered_reservations = [rsvn for rsvn in self.reservations if start_date <= rsvn.start_date.date() <= end_date]
        if file_format == 'csv':
            with open(save_file_name, mode='w', encoding='utf-8') as csv_file:
                fieldnames = ['name', 'start_date', 'end_date']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for rsvn in filtered_reservations:
                    writer.writerow({'name': rsvn.name,
                                     'start_date': rsvn.start_date.strftime("%d.%m.%Y %H:%M"),
                                     'end_date': rsvn.end_date.strftime("%d.%m.%Y %H:%M")})
            csv_file.close()
        elif file_format == 'json':
            schedule_by_date = {}
            for rsvn in filtered_reservations:
                day_date = rsvn.start_date.strftime("%d.%m.%Y")
                appointment = {
                    "name": rsvn.name,
                    "start_time": rsvn.start_date.strftime("%H:%M"),
                    "end_time": rsvn.end_date.strftime("%H:%M")}
                if day_date not in schedule_by_date:
                    schedule_by_date[day_date] = [appointment]
                else:
                    schedule_by_date[day_date].append(appointment)
            with open(save_file_name, mode='w', encoding='utf-8') as json_file:
                json.dump(schedule_by_date, json_file, indent=2)
            json_file.close()

    def add_to_database(self, name: str, start_dt: datetime, end_dt: datetime) -> None:
        """
        Adds a reservation to the database.

        Parameters
        ----------
        name : str
            The name of the person making the reservation.
        start_dt : datetime
            The start date and time of the reservation.
        end_dt : datetime
            The end date and time of the reservation.

        Returns
        -------
        None
        """
        self.session.add(Reservations(name=name, start_date=start_dt, end_date=end_dt))
        self.session.commit()
        return None

    def subtract_from_database(self, name: str, start_dt: datetime):
        """
        Subtracts a reservation from the database.

        Parameters
        ----------
        name : str
            The name of the person whose reservation should be canceled.
        start_dt : datetime
            The start date and time of the reservation to be canceled.

        Returns
        -------
        None
        """
        reservation = self.session.query(Reservations).filter_by(name=name, start_date=start_dt).one()
        self.session.delete(reservation)
        self.session.commit()
        return None

    def load_schedule_from_database(self) -> None:
        """
        Loads the schedule of reservations from the database in chronological order.

        Returns
        -------
        None
        """
        self.reservations = self.session.query(Reservations).order_by(Reservations.start_date).all()
        return None


def one_hour_from_now_or_less(start_dt: datetime) -> bool:
    """
    Checks if the given date and time is within one hour from the current time.

    Parameters
    ----------
    start_dt : datetime
        The start date and time of the reservation.

    Returns
    -------
    bool
        True if the reservation is within one hour from the current time, False otherwise.
    """
    if start_dt - timedelta(hours=1) <= datetime.now():
        input(f'\nYour reservation must be made at least one hour in advance.\n'
              f'Press enter to return to main menu.')
        return True
    return False


def main_menu() -> str:
    """
    Displays the main menu options and prompts the user for a choice.

    Returns
    -------
    str
        The user's menu choice as a string.
    """
    print('\nWhat do you want to do:\n')
    print('1. Make a reservation')
    print('2. Cancel a reservation')
    print('3. Print schedule')
    print('4. Save schedule to a file')
    print('5. Exit')
    user_menu_choice = input('Enter your choice (1-5):\n\n$ ')
    return user_menu_choice


def name_validation(question_name: str) -> Optional[str]:
    """
    Validates the user's name input.

    Parameters
    ----------
    question_name : str
        The specific expression related to the input question.

    Returns
    -------
    str or None
        The user's name if valid, or None if empty string.
    """
    name = input(f"\nWhat's {question_name}?\n\n$ ")
    if name == '':
        input('Invalid name.\n'
              'Press enter to return to main menu.')
        return None
    return name


def datetime_validation(question_name: str) -> Optional[datetime]:
    """
    Validates the user's input for the reservation date and time.
    Accepts only - dd.mm.yyyy hh:mm format - zero-padded hours and minutes.

    Parameters
    ----------
    question_name : str
        The specific expression related to the input question.

    Returns
    -------
    datetime or None
        The reservation date and time as a datetime.datetime object if valid, or None if invalid.
    """
    pattern = r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"
    usr_datetime = input(f"\nEnter the date and time for which you would like to {question_name} a reservation? "
                         "{DD.MM.YYYY HH:MM}\n\n$ ")
    if re.fullmatch(pattern, usr_datetime):
        try:
            usr_datetime = datetime.strptime(usr_datetime, "%d.%m.%Y %H:%M")
            return usr_datetime
        except ValueError:
            pass
    input(f'Invalid date format.\n'
          f'Press enter to return to main menu.')
    return None


def date_validation(question_name: str) -> Optional[datetime.date]:
    """
    Validates the user's input for the date of the reservation.
    Accepts only - dd.mm.yyyy format.

    Parameters
    ----------
    question_name : str
        The specific expression related to the input question.

    Returns
    -------
    datetime.date or None
        The reservation start date as a date object if valid, or None if invalid.
    """
    pattern = r"\d{2}\.\d{2}\.\d{4}"
    user_date = input(f'\nPlease enter the {question_name} date {{DD.MM.YYYY}}\n\n$ ')
    if re.fullmatch(pattern, user_date):
        try:
            user_date = datetime.strptime(user_date, "%d.%m.%Y").date()
            return user_date
        except ValueError:
            pass
    input(f'Invalid date format.\n'
          f'Press enter to return to main menu.')
    return None


def period_validation(avl_periods: list[int]) -> Optional[int]:
    """
    Validates the user's input for the chosen reservation period.

    Parameters
    ----------
    avl_periods : list[int]
        A list of available reservation periods.

    Returns
    -------
    int or None
        The user's chosen reservation period if valid, or None if invalid.
    """
    try:
        user_chosen_period = int(input(f'\n$ '))
        if user_chosen_period in avl_periods:
            return user_chosen_period
    except ValueError:
        pass
    input(f'Chosen period not available.\n'
          f'Press enter to return to the main menu.')
    return None


def agreement(datetime_of_next_reservation: datetime) -> str:
    """
    Prompts the user to confirm or change the reservation date and time.

    Parameters
    ----------
    datetime_of_next_reservation : datetime.datetime
        The alternative reservation date related to the input question.

    Returns
    -------
    str
        The user's agreement choice as a string.
    """
    user_agreement = input(f'The time you chose is unavailable.\n'
                           f'Would you like to make a reservation for '
                           f'{datetime_of_next_reservation} instead?(yes/no)\n\n$ ')
    return user_agreement


def validation_file_type() -> Optional[str]:
    """
    Validates the user's input for the file type.

    Returns
    -------
    str or None
        The user's chosen file type ('json' or 'csv') if it is valid,
        or None if the input is invalid.
    """
    available_file_types = ('json', 'csv')
    user_file_type = input('\nPlease enter type of the file (json/csv)\n\n$ ')
    if user_file_type not in available_file_types:
        input('Invalid file format\n'
              'Press enter to return to main menu.')
        return None
    return user_file_type


if __name__ == '__main__':
    court = TennisCourt()
    court.load_schedule_from_database()

    while True:
        menu_choice = main_menu()

        match menu_choice:
            case '1':  # 1. Make a reservation
                usr_name = name_validation('your name')
                if usr_name is None:
                    continue

                while True:
                    usr_date = datetime_validation('make')
                    if usr_date is None:
                        break

                    if court.two_reservations_per_week(usr_name, usr_date):
                        break

                    if one_hour_from_now_or_less(usr_date):
                        break

                    if court.date_not_available(usr_date):
                        usr_date = court.next_available_datetime(usr_date)
                        if agreement(usr_date).lower() != 'yes':
                            continue

                    available_periods = court.available_periods(usr_date)

                    chosen_period = period_validation(available_periods)
                    if chosen_period is None:
                        break

                    usr_start = usr_date
                    usr_end = usr_start + timedelta(minutes=chosen_period)

                    court.make_reservation(usr_name, usr_start, usr_end)
                    court.add_to_database(usr_name, usr_start, usr_end)
                    input(f'Reservation successfully made!\n'
                          f'Press enter to return to main menu.')
                    break

            case '2':  # 2. Cancel a reservation
                usr_name = name_validation('your name')
                if usr_name is None:
                    continue

                usr_date = datetime_validation('cancel')
                if usr_date is None:
                    continue

                if one_hour_from_now_or_less(usr_date):
                    continue

                if court.cancel_reservation(usr_name, usr_date):
                    court.subtract_from_database(usr_name, usr_date)
                    input('Reservation successfully cancelled!\n'
                          'Press enter to return to main menu.')
                    continue
                else:
                    input('No reservation found for the given name and date.\n'
                          'Press enter to return to main menu.')
                    continue

            case '3':  # 3. Print schedule
                start_schedule = date_validation('start')
                if start_schedule is None:
                    continue

                end_schedule = date_validation('end')
                if end_schedule is None:
                    continue

                court.print_schedule(start_schedule, end_schedule)
                continue

            case '4':  # 4. Save schedule to a file
                start_save = date_validation('start')
                if start_save is None:
                    continue

                end_save = date_validation('end')
                if end_save is None:
                    continue

                file_type = validation_file_type()
                if file_type is None:
                    continue

                file_name = name_validation('name of your file')
                if file_name is None:
                    continue

                court.save_schedule(start_save, end_save, file_type, file_name)
                input(f'\n{file_name} saved successfully!\n'
                      f'Press enter to return to main menu.')
                continue

            case '5':  # 5. Exit
                break

            case other:
                input('Invalid choice.\n'
                      'Press enter to return to main menu.')
                continue
