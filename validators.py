from datetime import datetime

from re import fullmatch
from typing import Optional


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
    if fullmatch(pattern, usr_datetime):
        try:
            usr_datetime = datetime.strptime(usr_datetime, "%d.%m.%Y %H:%M")
            return usr_datetime
        except ValueError:
            input(f'Chosen date and time do not exist in Gregorian calendar.\n'
                  f'Press enter to return to main menu.')
            return None
    else:
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
    if fullmatch(pattern, user_date):
        try:
            user_date = datetime.strptime(user_date, "%d.%m.%Y").date()
            return user_date
        except ValueError:
            input(f'Chosen date does not exist in Gregorian calendar.\n'
                  f'Press enter to return to main menu.')
            return None
    else:
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
        input(f'Chosen period must be a number.\n'
              f'Press enter to return to the main menu.')
        return None
    else:
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
