from collections import UserDict
from datetime import datetime, timedelta
import pickle
from abc import ABC, abstractmethod

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Phone number must be 10 digits long.")

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def to_datetime(self):
        return datetime.strptime(self.value, "%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if self.find_phone(phone):
            raise ValueError(f"Phone number '{phone}' already exists.")
        self.phones.append(Phone(phone))



    def edit_phone(self, old_phone, new_phone):
        if self.find_phone(new_phone):
            raise ValueError(f"Phone number '{new_phone}' already exists.")
        self.add_phone(new_phone)
        self.remove_phone(old_phone)
 
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if not phone:
            raise ValueError(f"Phone number '{phone_number}' not found.")
        self.phones.remove(phone)
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        bday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{bday}"
    

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)
        
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Record with name '{name}' not found.")
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = record.birthday.to_datetime().date()
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)

            days_diff = (bday_this_year - today).days

            if 0 <= days_diff <= 7:
                congratulate_date = bday_this_year
                if congratulate_date.weekday() >= 5:
                    days_to_monday = 7 - congratulate_date.weekday()
                    congratulate_date += timedelta(days=days_to_monday)
                upcoming.append({
                    "name": record.name.value,
                    "birthday": congratulate_date.strftime("%d.%m.%Y")
                })

        return upcoming

class View(ABC):
    @abstractmethod
    def display(self, message: str):
        pass

    @abstractmethod
    def prompt(self, message: str) -> str:
        pass

class ConsoleView(View):
    def display(self, message: str):
        print(message)

    def prompt(self, message: str) -> str:
        return input(message)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  

    def __str__(self):
        result = ""
        for record in self.data.values():
            result += str(record) + "\n"
        return result.strip()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Invalid input. Please provide the correct number of arguments."
    return inner


def parse_input(user_input): 
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, book):  
    name, phone = args
    record = book.find(name)  

    if not record:
        record = Record(name)
        book.add_record(record) 

    try:
        record.add_phone(phone)  
        return "Contact added."
    except ValueError as e:
        return str(e)



@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."



@input_error
def show_phone(args, contacts):
    name = args[0]
    record = contacts.get(name)
    if not record:
        raise KeyError("Contact not found.")
    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(contacts): 
    if not contacts:
        return "No contacts saved."
    return "\n".join(str(record) for record in contacts.values())

@input_error
def remove_phone_command(args, contacts):
    name, phone = args
    record = contacts.get(name)

    if not record:
        raise KeyError
    
    try:
        record.remove_phone(phone)
        
        if not record.phones:
            del contacts[name]
            return f"Phone removed. Contact '{name}' deleted because no phones left."
        return f"Phone '{phone}' removed from contact '{name}'."
    except ValueError as e:
        return str(e)

@input_error
def delet(args, contacts):
    name = args[0]
    contacts.delete(name) 
    return f"Contact <{name}> deleted."

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Please provide both name and birthday. Format: <name> <DD.MM.YYYY>")

    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(bday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise KeyError("Birthday not found.")
    return record.birthday.value

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    return "\n".join([f"{item['name']} - {item['birthday']}" for item in upcoming])



def bot_support():
    return (
        "Supported commands:\n"
        "hello - Greet the bot\n"
        "add <name> <phone> - Add a new contact\n"
        "change <name> <old_phone> <new_phone> - Change a contact's phone\n"
        "phone <name> - Show phone numbers for a contact\n"
        "all - Show all contacts\n"
        "add-birthday <name> <date> - Add birthday\n"
        "show-birthday <name> - Show birthday\n"
        "birthdays - Show all birthdays\n"
        "help - Show this help message\n"
        "remove-phone <name> <phone> - Remove a phone number from a contact\n"
        "delet <name> - Delete a contact\n"
        "exit - Exit the bot"
    )


def main():
    view = ConsoleView()
    book = load_data() 
    view.display("Welcome to the assistant bot!")

    while True:
        user_input = view.prompt("Enter a command: ").strip()
        if not user_input:
            view.display("Please enter a valid command. Write <help> to see all commands.")
            continue
        
        command, args = parse_input(user_input)

        if command == "exit":
            save_data(book) 
            view.display("Good bye!")
            break
        elif command == "help":
            view.display(bot_support())

        elif command == "hello":
            view.display("How can I help you?")

        elif command == "add":
            view.display(add_contact(args, book))

        elif command == "change":
            view.display(change_contact(args, book))

        elif command == "phone":
            view.display(show_phone(args, book))

        elif command == "all":
            view.display(show_all(book))

        elif command == "delet":
            view.display(delet(args, book))

        elif command == "add-birthday":
            view.display(add_birthday(args, book))

        elif command == "show-birthday":
            view.display(show_birthday(args, book))

        elif command == "birthdays":
            view.display(birthdays(args, book))

        elif command == "remove-phone":
            view.display(remove_phone_command(args, book))

        else:
            view.display("Invalid command.")


if __name__ == "__main__":
    main()