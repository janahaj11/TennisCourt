import csv
import json
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import validators
from models import Base, Reservations


class Reservation:
    def __init__(self, name, start_dt, end_dt):
        self.name = name
        self.start_date = start_dt
        self.end_date = end_dt


class TennisCourt:
    def __init__(self):
        self.reservations = []
        connection_string = 'sqlite:///tennis_court.db'
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.session = session()

    def is_period_overlaps(self, start_dt: datetime, end_dt: datetime) -> bool:
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
        for reservation in self.reservations:
            if start_dt < reservation.end_date and end_dt > reservation.start_date:
                return True
        return False

    def is_date_not_available(self, start_dt: datetime) -> bool:
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
        for reservation in self.reservations:
            if reservation.start_date <= start_dt < reservation.end_date:
                return True
        return False

    def is_two_reservations_per_week(self, name: str, start_dt: datetime) -> bool:
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
        for reservation in self.reservations:
            if name == reservation.name and datetime.isocalendar(reservation.start_date).week == week_no:
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
        for reservation in self.reservations:
            if reservation.start_date >= closest_time + timedelta(minutes=30):
                return closest_time
            elif closest_time <= reservation.end_date:
                closest_time = reservation.end_date
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
            if self.is_period_overlaps(start_dt, end_dt):
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
        for idx, reservation in enumerate(self.reservations):
            if reservation.start_date > start_dt:
                new_reservation = Reservation(name, start_dt, end_dt)
                self.reservations.insert(idx, new_reservation)
                return None
        new_reservation = Reservation(name, start_dt, end_dt)
        self.reservations.append(new_reservation)
        return None

    def is_reservation_cancelled(self, name: str, start_dt: datetime) -> bool:
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
        for reservation in self.reservations:
            if name == reservation.name and start_dt == reservation.start_date:
                self.reservations.remove(reservation)
                return True
        input('No reservation found for the given name and date.\n'
              'Press enter to return to main menu.')
        return False

    def print_schedule(self, start_dt: datetime.date, end_dt: datetime.date) -> None:
        """
        Prints the schedule of reservations between the specified start and end date.

        Parameters
        ----------
        start_dt : datetime.date
            The start date to filter reservations.
        end_dt : datetime.date
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
                print(current_date.strftime("%A, %d %B, %Y"))
                
            reservations = [reservation for reservation in self.reservations
                            if reservation.start_date.date() == current_date]
            if not reservations:
                print("No reservations\n")
            else:
                for reservation in reservations:
                    print(f"* {reservation.name} "
                          f"{reservation.start_date.strftime('%H:%M')} - "
                          f"{reservation.end_date.strftime('%H:%M')}")
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
        filtered_reservations = [reservation for reservation in self.reservations
                                 if start_date <= reservation.start_date.date() <= end_date]
        if file_format == 'csv':
            with open(save_file_name, mode='w', encoding='utf-8') as csv_file:
                fieldnames = ['name', 'start_date', 'end_date']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for reservation in filtered_reservations:
                    writer.writerow({'name': reservation.name,
                                     'start_date': reservation.start_date.strftime("%d.%m.%Y %H:%M"),
                                     'end_date': reservation.end_date.strftime("%d.%m.%Y %H:%M")})
        elif file_format == 'json':
            schedule_by_date = {}
            for reservation in filtered_reservations:
                day_date = reservation.start_date.strftime("%d.%m.%Y")
                appointment = {
                    "name": reservation.name,
                    "start_time": reservation.start_date.strftime("%H:%M"),
                    "end_time": reservation.end_date.strftime("%H:%M")}
                if day_date not in schedule_by_date:
                    schedule_by_date[day_date] = [appointment]
                else:
                    schedule_by_date[day_date].append(appointment)
            with open(save_file_name, mode='w', encoding='utf-8') as json_file:
                json.dump(schedule_by_date, json_file, indent=2)
        input(f'\n{save_file_name}.{file_format} saved successfully!\n'
              f'Press enter to return to main menu.')
        return None

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
        input(f'Reservation successfully made!\n'
              f'Press enter to return to main menu.')
        return None

    def subtract_from_database(self, name: str, start_dt: datetime) -> None:
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
        input('Reservation successfully cancelled!\n'
              'Press enter to return to main menu.')
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


def is_one_hour_from_now(start_dt: datetime) -> bool:
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


if __name__ == '__main__':
    court = TennisCourt()
    court.load_schedule_from_database()

    while True:
        menu_choice = main_menu()

        match menu_choice:
            case '1':  # 1. Make a reservation
                usr_name = validators.name_validation('your name')
                if usr_name is None:
                    continue

                while True:
                    usr_date = validators.datetime_validation('make')
                    if usr_date is None:
                        break

                    if court.is_two_reservations_per_week(usr_name, usr_date):
                        break

                    if is_one_hour_from_now(usr_date):
                        break

                    if court.is_date_not_available(usr_date):
                        usr_date = court.next_available_datetime(usr_date)
                        if validators.agreement(usr_date).lower() != 'yes':
                            continue

                    available_periods = court.available_periods(usr_date)

                    chosen_period = validators.period_validation(available_periods)
                    if chosen_period is None:
                        break

                    usr_start = usr_date
                    usr_end = usr_start + timedelta(minutes=chosen_period)

                    court.make_reservation(usr_name, usr_start, usr_end)
                    court.add_to_database(usr_name, usr_start, usr_end)
                    break

            case '2':  # 2. Cancel a reservation
                usr_name = validators.name_validation('your name')
                if usr_name is None:
                    continue

                usr_date = validators.datetime_validation('cancel')
                if usr_date is None:
                    continue

                if is_one_hour_from_now(usr_date):
                    continue

                if court.is_reservation_cancelled(usr_name, usr_date):
                    court.subtract_from_database(usr_name, usr_date)
                continue

            case '3':  # 3. Print schedule
                start_schedule = validators.date_validation('start')
                if start_schedule is None:
                    continue

                end_schedule = validators.date_validation('end')
                if end_schedule is None:
                    continue

                court.print_schedule(start_schedule, end_schedule)
                continue

            case '4':  # 4. Save schedule to a file
                start_save = validators.date_validation('start')
                if start_save is None:
                    continue

                end_save = validators.date_validation('end')
                if end_save is None:
                    continue

                file_type = validators.validation_file_type()
                if file_type is None:
                    continue

                file_name = validators.name_validation('name of your file')
                if file_name is None:
                    continue

                court.save_schedule(start_save, end_save, file_type, file_name)
                continue

            case '5':  # 5. Exit
                break

            case other:
                input('Invalid choice.\n'
                      'Press enter to return to main menu.')
                continue
