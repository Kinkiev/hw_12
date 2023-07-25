from collections import UserDict
from datetime import datetime
import pickle
import csv


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not self.is_valid_phone(new_value):
            raise ValueError("Invalid phone number format")
        self._value = new_value

    @staticmethod
    def is_valid_phone(phone):
        if phone:
            if not phone.startswith("+380"):
                return False
            if len(phone) != 13:
                return False
            if not phone[4:].isdigit():
                return False
            return True
        return True


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not self.is_valid_date(new_value):
            raise ValueError("Invalid date format")
        self._value = new_value

    @staticmethod
    def is_valid_date(birthday):
        try:
            datetime.datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        self.birthday = birthday
        if phone is not None:
            self.add_phone(phone)
        if birthday is not None:
            self.set_birthday(birthday)
    
    def add_phone(self, phone: Phone):
        if phone not in self.phones:
            self.phones.append(phone)
            return f"Phone {phone} added to contact {self.name}"
        return f"{phone} already added to {self.name}"

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def change_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == str(old_phone):
                self.phones[i] = new_phone
                break
            
    def set_birthday(self, birthday):
        try:
            self.birthday = datetime.strptime(birthday, "%d.%m.%Y").date()
            return f"Birthday set for {self.name}"
        except ValueError:
            return f"Invalid birthday format. Please use dd.mm.yyyy format."
            
    def days_to_birthday(self):
        if self.birthday is None:
            return "Birthday not set"
        
        current_date = datetime.now().date()
        next_birthday = datetime(current_date.year, self.birthday.month, self.birthday.day).date()
        
        if next_birthday < current_date: 
            next_birthday = datetime(current_date.year + 1, self.birthday.month, self.birthday.day).date()
            
        days_to_bd = (next_birthday - current_date).days
        return f"Days to next birthday for {self.name}: {days_to_bd}"

    def __str__(self):
        return f"Name: {self.name}, Phones: {', '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record

    def remove_record(self, name):
        del self.data[str(name)]
        return f"{name} record deleted"

    def search_by_name(self, name):
        results = []
        for record in self.data.values():
            if str(record.name) == name:
                results.append(record)
        return results

    def change_phone_by_name(self, name, new_phone):
        results = self.search_by_name(name)
        for result in results:
            result.change_phone(result.phones[0], Phone(new_phone))

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    
    def iterator(self, n=None):
        records = list(self.data.values())
        
        if n is None: 
            yield records
        else:   
            total_records = len(records)
            current_index = 0

        while current_index < total_records:
            yield records[current_index:current_index+n]
            current_index += n
            
    def show_all(self, n=None):
        iterator = self.iterator(n)
        for chunk in iterator:
            print("\n".join(str(record) for record in chunk))
            if n is None or len(chunk) < n:
                break
            
    def load(self, file):
        try:
            with open(file, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}
            
    def save(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self.data, f)          
            
    def save_csv(self, file):
        with open(file, 'w', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(self.data)
                
            
    def search(self, query):
        search_results = []
        query = query.lower()
         
        for record in self.data.values():
            if query in str(record.name).lower():
                search_results.append(record)
            else:
                for phone in record.phones:
                    if query in str(phone).lower():
                        search_results.append(record)
                
        return search_results

def help() -> str:
    return "Available commands:\n" \
           "- hello\n" \
           "- add [name] [phone in format +380xxxxxxx]\n" \
           "- change [name] [phone]\n" \
           "- find [name]\n" \
           "- show_all\n" \
           "- show\n" \
           "- birthday [name] [date in format dd.mm.yyyy]\n" \
           "- days_to_bd [name]\n" \
           "- help \n" \
           "- del [name] \n" \
           "- search [string] (>3 symbols) \n" \
           "- bye, close, exit"


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "contact not found"
        except ValueError:
            return "invalid format, type help"
        except IndexError:
            return "Invalid input"
        except Exception:
            return help()

    return wrapper


ab = AddressBook()

def add(name: str, phone: str = None, birthday: str = None) -> str:
    try:
        record: Record = ab.get(str(name))
        if record:
            existing_phones = [str(p) for p in record.phone]
            if phone in existing_phones:
                return f"{phone} already added to {name}"
            new_phone = Phone(phone)
            return record.add_phone(new_phone)
        name_field = Name(name)
        phone_field = Phone(phone)
        birthday_field = Birthday(birthday) if birthday else None
        record = Record(name_field, phone_field, birthday_field)
        ab.add_record(record)
        return f"Contact {name} add success"
    except ValueError as e:
        return str(e)


@input_error
def find(name: str) -> str:
    results = ab.search_by_name(name)
    if results:
        return str(results[0])
    else:
        raise KeyError(f"Contact {name} not found")


@input_error
def change(name: str, new_phone: str) -> str:
    rec: Record = ab.get(str(name))
    if rec: 
        ab.change_phone_by_name(name, new_phone)
        return f"phone number for {name} updated"
    return f"no {name} in contacts"

@input_error
def show_all(*args) -> str:
    if len(args) > 0:
        n = int(args[0])
        iterator = ab.iterator(n)
        for chunk in iterator:
            # print (chunk)
            for record in chunk:
                print(record)
            choice = input("Press Enter to continue or 'q' to quit: ")
            if choice.lower() == "q":
                break
    else:
        ab.show_all()
    return ""

@input_error
def set_birthday(name: str, birthday: str) -> str:
    rec: Record = ab.get(str(name))
    if rec:
        return rec.set_birthday(birthday)
    return f"No {name} in contacts"


@input_error
def days_to_birthday(name: str) -> str:
    rec: Record = ab.get(str(name))
    if rec:
        return rec.days_to_birthday()
    return f"No {name} in contacts"


@input_error
def no_command(*args):
    return " - not valid command entered\n" \
           " - type 'help' for commands"


@input_error
def hello() -> str:
    return "How can I help you?"


@input_error
def close() -> str:
    return "Good bye!"

@input_error
def remove(name:str) -> str:
    rec: Record = ab.get(str(name))
    if rec:
        return ab.remove_record(name)
    return f"No {name} in contacts"

@input_error
def search(*args) -> str:
    if len(args) == 1 and len(args[0]) >= 3:
        query = args[0]
        results = ab.search(query)
        if results:
            return "\n".join(str(record) for record in results)
        else: 
            return "No result found by your search"
    else:
        return "Invalid search, try 3 symbols or more after search command"


commands = {
    "hello": hello,
    "hi": hello,
    "add": add,
    "+": add,
    "change": change,
    "find": find,
    "show_all": show_all,
    "show": show_all,
    "help": help,
    "bye": close,
    "close": close,
    "exit": close, 
    "birthday": set_birthday,
    "days_to_bd": days_to_birthday,
    "search": search,
    "del": remove
}

@input_error
def parser(text: str) -> tuple[callable, tuple[str]]:
    text_lower = text.lower()
    words = text_lower.split()

    if words[0] in commands:
        command = commands[words[0]]
        args = tuple(words[1:])
        return command, args

    return no_command, ()


def main():
    
    try:
    
        try:
            ab.load("ab.bin")
        except FileNotFoundError:
            print ("no file to load")
        
        while True:
            user_input = input(">>>")
            command, data = parser(user_input)

            if command == close:
                ab.save("ab.bin")
                ab.save_csv("ab.csv")
                break

            result = command(*data)
            print(result)

    except Exception as e:
        print ("Error {e}")


if __name__ == "__main__":
    main()
