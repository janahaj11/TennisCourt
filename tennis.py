import csv
import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Base, Reservations
from datetime import date, datetime, timedelta


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

    def period_overlaps(self, start_dt, end_dt):
        for rsvn in self.reservations:
            if start_dt < rsvn.end_date and end_dt > rsvn.start_date:
                return True
        return False

    def date_not_available(self, start_dt):
        for rsvn in self.reservations:
            if rsvn.start_date <= start_dt < rsvn.end_date:
                return True
        return False

    def two_reservations_per_week(self, name, start_dt):
        counter = 0
        week_no = datetime.isocalendar(start_dt).week
        for rsvn in self.reservations:
            if name == rsvn.name and datetime.isocalendar(rsvn.start_date).week == week_no:
                counter += 1
                if counter > 1:
                    return True
        return False

    def one_hour_from_now_or_less(self, start_dt):
        if start_dt - timedelta(hours=1) <= datetime.now():
            return True
        return False

    def next_available_datetime(self, start_dt):
        closest_time = start_dt
        for rsvn in self.reservations:
            if rsvn.start_date >= closest_time + timedelta(minutes=30):
                return closest_time
            elif closest_time <= rsvn.end_date:
                closest_time = rsvn.end_date
        return closest_time

    def available_periods(self, start_dt):
        available_periods = []
        periods = [30, 60, 90]
        for period in periods:
            end_dt = start_dt + timedelta(minutes=period)
            if self.period_overlaps(start_dt, end_dt):
                break 
            available_periods.append(period)
        return available_periods

    def make_reservation(self, name, start_dt, end_dt):
        for idx, rsvn in enumerate(self.reservations):
            if rsvn.start_date > start_dt:
                reservation = Reservation(name, start_dt, end_dt)
                self.reservations.insert(idx, reservation)
                return None
        reservation = Reservation(name, start_dt, end_dt)
        self.reservations.append(reservation)
        return None

    def cancel_reservation(self, name, start_dt):
        for rsvn in self.reservations:
            if name == rsvn.name and start_dt == rsvn.start_date:
                self.reservations.remove(rsvn)
                return True
        return False

    def print_schedule(self, start_dt, end_dt):
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
        return None

    def save_schedule(self, start_dt, end_dt, file_format, file_name):
        start_date = start_dt
        end_date = end_dt
        filtered_reservations = [rsvn for rsvn in self.reservations if start_date <= rsvn.start_date.date() <= end_date]
        if file_format == 'csv':
            with open(file_name, mode='w', encoding='utf-8') as csv_file:
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
                date = rsvn.start_date.strftime("%d.%m.%Y")
                appointment = {
                    "name": rsvn.name,
                    "start_time": rsvn.start_date.strftime("%H:%M"),
                    "end_time": rsvn.end_date.strftime("%H:%M")}
                if date not in schedule_by_date:
                    schedule_by_date[date] = [appointment]
                else:
                    schedule_by_date[date].append(appointment)
            with open(file_name, mode='w', encoding='utf-8') as json_file:
                json.dump(schedule_by_date, json_file, indent=2)
            json_file.close()

    def add_to_database(self, name, start_dt, end_dt):
        self.session.add(Reservations(name=name, start_date=start_dt, end_date=end_dt))
        self.session.commit()

    def subtract_from_database(self, name, start_dt):
        reservation = self.session.query(Reservations).filter_by(name=name, start_date=start_dt).one()
        self.session.delete(reservation)
        self.session.commit()

    def load_schedule_from_database(self):
        self.reservations = self.session.query(Reservations).order_by(Reservations.start_date).all()


if __name__ == '__main__':
    court = TennisCourt()
    court.load_schedule_from_database()

    while True:
        print('\nWhat do you want to do:\n')
        print('1. Make a reservation')
        print('2. Cancel a reservation')
        print('3. Print schedule')
        print('4. Save schedule to a file')
        print('5. Exit')
        menu_choice = input('Enter your choice (1-5):\n\n$ ')

        match menu_choice:
            case '1':  # 1. Make a reservation
                usr_name = input("\nWhat's your name?\n\n$ ")

                if usr_name == '':
                    input('Invalid name.\n'
                          'Press enter to return to main menu.')
                    continue

                while True:
                    usr_date = input("\nWhen would you like to book? {DD.MM.YYYY HH:MM}\n\n$ ")

                    try:
                        usr_date = datetime.strptime(usr_date, "%d.%m.%Y %H:%M")
                    except ValueError:
                        input(f'Invalid date format.\n'
                              f'Press enter to return to main menu.')
                        break

                    if court.two_reservations_per_week(usr_name, usr_date):
                        input(f'Sorry, {usr_name} has reached the reservation limit for this week (2).\n'
                              f'Press enter to return to main menu.')
                        break

                    if court.one_hour_from_now_or_less(usr_date):
                        input(f'\nYour reservation must be made at least one hour in advance.\n'
                              f'Press enter to return to main menu.')
                        break

                    if court.date_not_available(usr_date):
                        usr_date = court.next_available_datetime(usr_date)
                        agreement = input(f'The time you chose is unavailable.\n'
                                          f'Would you like to make a reservation for {usr_date} instead?(yes/no)\n\n$ ')
                        if agreement.lower() != 'yes':
                            continue

                    available_periods = court.available_periods(usr_date)
                    print('\nHow long would you like to book court?\n'
                          'Available periods:')

                    for i, period in enumerate(available_periods, start=1):
                        print(f'{i}) {period} Minutes')

                    try:
                        chosen_period = int(input(f'\n$ '))
                    except ValueError:
                        input(f'Chosen period not available.\n'
                              f'Press enter to return to main menu.')
                        break

                    if chosen_period not in available_periods:
                        input(f'Chosen period "{chosen_period}" not available.\n'
                              f'Press enter to return to main menu.')
                        break

                    usr_start = usr_date
                    usr_end = usr_start + timedelta(minutes=chosen_period)
                    court.make_reservation(usr_name, usr_start, usr_end)
                    court.add_to_database(usr_name, usr_start, usr_end)
                    input(f'Reservation successfully made.\n'
                          f'Press enter to return to main menu.')
                    break

            case '2':  # 2. Cancel a reservation
                usr_name = input("\nWhat's your name?\n\n$ ")

                if usr_name == '':
                    input('Invalid name.\n'
                          'Press enter to return to main menu.')
                    continue

                usr_date = input("\nEnter reservation you would like to cancel. {DD.MM.YYYY HH:MM}\n\n$ ")

                try:
                    usr_date = datetime.strptime(usr_date, "%d.%m.%Y %H:%M")
                except ValueError:
                    input(f'Invalid date format.\n'
                          f'Press enter to return to main menu.')
                    continue

                if court.one_hour_from_now_or_less(usr_date):
                    input(f'\nCancellation must be made at least one hour in advance.\n'
                          f'Press enter to return to main menu.')
                    continue

                if court.cancel_reservation(usr_name, usr_date):
                    court.subtract_from_database(usr_name, usr_date)
                    input(f'Reservation successfully cancelled!.\n'
                          f'Press enter to return to main menu.')
                    continue
                else:
                    input(f'No reservation found for the given name and date.\n'
                          f'Press enter to return to main menu.')
                    continue

            case '3':  # 3. Print schedule
                try:
                    start_schedule = input('\nPlease enter start date {DD.MM.YYYY}\n\n$ ')
                    start_schedule = datetime.strptime(start_schedule, "%d.%m.%Y").date()
                except ValueError:
                    input(f'Invalid date format.\n'
                          f'Press enter to return to main menu.')
                    continue

                try:
                    end_schedule = input('\nPlease enter end date {DD.MM.YYYY}\n\n$ ')
                    end_schedule = datetime.strptime(end_schedule, "%d.%m.%Y").date()
                except ValueError:
                    input(f'Invalid date format.\n'
                          f'Press enter to return to main menu.')
                    continue

                court.print_schedule(start_schedule, end_schedule)
                input('Schedule printed.\n'
                      'Press enter to return to main menu.')
                continue

            case '4':  # 4. Save schedule to a file
                try:
                    start_save = input('\nPlease enter start date {DD.MM.YYYY}\n\n$ ')
                    start_save = datetime.strptime(start_save, "%d.%m.%Y").date()
                except ValueError:
                    input(f'Invalid date format.\n'
                          f'Press enter to return to main menu.')
                    continue

                try:
                    end_save = input('\nPlease enter end date {DD.MM.YYYY}\n\n$ ')
                    end_save = datetime.strptime(end_save, "%d.%m.%Y").date()
                except ValueError:
                    input(f'Invalid date format.\n'
                          f'Press enter to return to main menu.')
                    continue

                file_type = input('\nPlease enter type of the file (json/csv)\n\n$ ')
                if file_type not in ['json', 'csv']:
                    input('Invalid file format\n'
                          'Press enter to return to main menu.')
                    continue

                file_name = input('\nPlease enter name of the file\n\n$ ')
                if file_name == '':
                    input('Invalid name.\n'
                          'Press enter to return to main menu.')
                    continue

                court.save_schedule(start_save, end_save, file_type, file_name)
                input(f'\n{file_name} saved successfully!\n'
                      f'Press enter to return to main menu.')
                continue
            case '5':  # 5. Exit
                break

            case other:
                print('Invalid choice. Please try again.'
                      'Press enter to return to main menu.')
                continue
