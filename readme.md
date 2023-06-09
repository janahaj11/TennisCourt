# Tennis Court Reservation System

The Tennis Court Reservation System is a program that allows users to make, cancel, and manage reservations for a tennis court. It provides various features such as checking reservation availability, limiting the number of reservations per person, printing the schedule, and saving the schedule to a file.

## Classes

### Reservation

Represents a reservation made by a person for a specific time period.

#### Properties

- `name`: The name of the person making the reservation.
- `start_date`: The start date and time of the reservation.
- `end_date`: The end date and time of the reservation.

### TennisCourt

Manages the reservations and provides functionality to interact with the reservation system.

#### Methods

- `__init__()`: Initializes the TennisCourt object and establishes a connection to the database.
- `period_overlaps(start_dt: datetime, end_dt: datetime) -> bool`: Checks if the given time period overlaps with any existing reservations.
- `date_not_available(start_dt: datetime) -> bool`: Checks if the given date and time is already reserved.
- `two_reservations_per_week(name: str, start_dt: datetime) -> bool`: Checks if the given person has already made two reservations in the same week.
- `next_available_datetime(start_dt: datetime) -> datetime`: Finds the next available date and time for a reservation.
- `available_periods(start_dt: datetime) -> list[int]`: Finds available periods limited by 30, 60, and 90 minutes for a reservation starting from the given datetime.
- `make_reservation(name: str, start_dt: datetime, end_dt: datetime) -> None`: Makes a reservation for the specified name and time slot.
- `cancel_reservation(name: str, start_dt: datetime) -> bool`: Cancels a reservation for the specified name and start date.
- `print_schedule(start_dt: datetime.date, end_dt: datetime.date) -> None`: Prints the schedule of reservations between the specified start and end date.
- `save_schedule(start_dt: date, end_dt: date, file_format: str, save_file_name: str) -> None`: Saves the schedule of reservations between start and end date to a CSV or JSON file.
- `add_to_database(name: str, start_dt: datetime, end_dt: datetime) -> None`: Adds a reservation to the database.
- `subtract_from_database(name: str, start_dt: datetime) -> None`: Subtracts a reservation from the database.
- `load_schedule_from_database() -> None`: Loads the schedule of reservations from the database in chronological order.

### Functions

- `one_hour_from_now_or_less(start_dt: datetime) -> bool`: Checks if the given date and time is within one hour from the current time.
- `main_menu() -> str`: Displays the main menu options and prompts the user for a choice.
- `name_validation(question_name: str) -> Optional[str]`: Validates the user's name input.
- `datetime_validation(question_name: str) -> Optional[datetime]`: Validates the user's input for the reservation date and time.
- `date_validation(question_name: str) -> Optional[datetime.date]`: Validates the user's input for the date of the reservation.
- `period_validation(avl_periods: list[int]) -> Optional[int]`: Validates the user's input for the chosen reservation period.

## Usage

The Tennis Court Reservation System can be used by executing the main_menu() function, which displays the main menu options and prompts the user for a choice. The user can then select an option to perform the desired action, such as making a reservation, canceling a reservation, printing the schedule, saving the schedule, or exiting the program.
