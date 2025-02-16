from datetime import datetime, timedelta
from collections import UserDict

def input_error(required_args=0, error_message="Invalid input. Please provide the correct arguments."):
    def decorator(func):
        def inner(*args, **kwargs):
            try:
                if required_args > 0 and len(args[0]) < required_args:
                    raise ValueError(error_message)
                return func(*args, **kwargs)
            except ValueError as e:
                return str(e)
            except KeyError:
                return "This contact doesn't exist."
            except IndexError:
                return "Invalid input. Please provide the correct arguments."
            except TypeError:
                return "Invalid argument type provided."
        return inner
    return decorator

# Base class for all record fields
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Class for storing contact name (required field)
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name can't be empty")
        super().__init__(value)

# Class for storing phone number with validation
class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value  # Validation
                return
        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, Phones: {phones}{birthday}"

# Class for storing and managing records
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)
                if 0 <= (bday - today).days <= 7:
                    congrats_day = bday
                    if bday.weekday() >= 5:
                        congrats_day += timedelta(days=(7 - bday.weekday()))
                    upcoming_birthdays.append({"name": record.name.value, "birthday": congrats_day.strftime("%d.%m.%Y")})
        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

@input_error(required_args=2, error_message="Write name and phone, please")
def add_contact(args, book: AddressBook):
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error(required_args=3, error_message="Write name, old phone, and new phone, please")
def change_contact(args, book):
    name, old_phone, new_phone = args[:3]
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    return "Contact not found."

@input_error(required_args=1, error_message="Write name, please")
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join(p.value for p in record.phones)
    return "Contact not found."

@input_error(required_args=0)
def show_all(args, book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(r) for r in book.data.values())

@input_error(required_args=2, error_message="Write name and birthday, please")
def add_birthday(args, book):
    name, birthday = args[:2]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."

@input_error(required_args=1, error_message="Write name, please")
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    return "No birthday found."

@input_error(required_args=0)
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    return "\n".join(f"{b['name']} - {b['birthday']}" for b in upcoming) if upcoming else "No upcoming birthdays."

def parse_input(user_input):
    parts = user_input.strip().split(" ", 1)
    command = parts[0].lower()
    args = parts[1].lower().split() if len(parts) > 1 else []
    return command, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
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

if __name__ == "__main__":
    main()
