import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Class to store names
class Name(Field):
    pass

# Class to store and validate phone numbers
class Phone(Field):
    def __init__(self, value):
        # Validate the phone number before initializing
        if not self.validate(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    @staticmethod
    def validate(phone):
        # Check if the phone number is exactly 10 digits
        return phone.isdigit() and len(phone) == 10

# Class to store and validate birthdays
class Birthday(Field):
    def __init__(self, value):
        try:
            # Try to convert the string value to a datetime object
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Class to store a single contact record
class Record:
    def __init__(self, name):
        self.name = Name(name)  # Store the name
        self.phones = []  # Initialize an empty list for phone numbers
        self.birthday = None  # Initialize birthday as None

    def add_phone(self, phone):
        # Add a phone number to the record
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        # Remove a phone number from the record
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        # Edit an existing phone number in the record
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone

    def find_phone(self, phone):
        # Find a phone number in the record
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        # Add a birthday to the record
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        # Calculate the number of days until the next birthday
        if self.birthday is None:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

# Class to store the address book
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def get_upcoming_birthdays(self, days=30):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday is not None:
                birthday = record.birthday.value.replace(year=today.year)
                if today <= birthday <= today + timedelta(days=days):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

# Decorator to handle input errors
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return wrapper

# Function to add a new contact
@input_error
def add_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

# Function to change an existing contact's phone number
@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number changed."

# Function to show a contact's phone number(s)
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return ", ".join(str(phone) for phone in record.phones)

# Function to show all contacts
@input_error
def show_all(args, book):
    return "\n".join(str(record) for record in book.data.values())

# Function to add a birthday to a contact
@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

# Function to show a contact's birthday
@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday is None:
        return f"{name} has no birthday set."
    return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"

# Function to show upcoming birthdays
@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(f"{record.name.value}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}" for record in upcoming_birthdays)

# Helper function to parse user input
def parse_input(user_input):
    return user_input.split()

# Function to save the address book to a file
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# Function to load the address book from a file
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# Main function to handle user commands
def main():
    # Load the address book from file or create a new one if file doesn't exist
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

    save_data(book)

if __name__ == "__main__":
    main()