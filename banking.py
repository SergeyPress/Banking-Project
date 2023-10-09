from random import randrange
from sys import exit
import sqlite3

connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
connection.commit()
login_account_number = 0


class Customer:
    def __init__(self):
        self.card_number = str(400000) + ''.join([str(randrange(0, 10)) for _ in range(9)])
        self.pin_code = ''.join([str(randrange(0, 10)) for _ in range(4)])
        self.balance = 0


def print_menu():
    print('1. Create an account\n2. Log into account\n0. Exit')


def last_number(card_number_without_last):
    list_sum = 0
    last_digit = 0
    counter = 1
    card_list = list(card_number_without_last)
    for numbers in card_list:
        numbers = int(numbers)
        if counter % 2 != 0:
            numbers *= 2
        if numbers > 9:
            numbers -= 9
        list_sum += numbers
        counter += 1
    card_number_sum = list_sum
    while card_number_sum % 10 != 0:
        last_digit += 1
        card_number_sum = list_sum + last_digit
    return str(last_digit)


def pass_luhn(card_number):
    list_sum = 0
    last_digit = card_number[-1]
    counter = 1
    card_number = list(card_number)
    del card_number[-1]
    card_number_without_last = card_number
    for numbers in card_number_without_last:
        numbers = int(numbers)
        if counter % 2 != 0:
            numbers *= 2
        if numbers > 9:
            numbers -= 9
        list_sum += numbers
        counter += 1
    if (list_sum + int(last_digit)) % 10 == 0:
        return True
    else:
        return False


def sql_execution(command):
    cursor.execute(command)
    return connection.commit()


def sql_fetchone(select_command):
    cursor.execute(select_command)
    return cursor.fetchone()


def sql_fetchall(select_command):
    cursor.execute(select_command)
    return cursor.fetchall()


def account_creation():
    user = Customer()
    user.card_number = user.card_number + last_number(user.card_number)
    print(f'Your card has been created\nYour card number:\n{user.card_number}\nYour card PIN:\n{user.pin_code}')
    cursor.execute('INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);', (user.card_number, user.pin_code, user.balance))
    connection.commit()
    print_menu()
    user_choice(int(input()))


def login():
    print('Enter your card number:')
    input_number = input()
    print('Enter your PIN:')
    input_pin = input()
    login_check(input_number, input_pin)


def user_choice(option):
    if option == 1:
        account_creation()
    elif option == 2:
        login()
    elif option == 0:
        print('Bye!')
        cursor.close()
        exit()
    else:
        print_menu()
        user_choice(int(input()))


def login_check(card, pin):
    cursor.execute('''SELECT
        id,
        number,
        pin,
        balance
    FROM
        card
    WHERE 
        number = ?
        AND pin = ?
        ;''', (str(card), str(pin)))
    result = cursor.fetchone()
    if result is None:
        print('Wrong card number or PIN!')
        print_menu()
        user_choice(int(input()))
    else:
        print('You have successfully logged in!')
        print_login_menu()
        user_choice_login(int(input()), card, pin)


def print_login_menu():
    print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')


def user_choice_login(variant, card, pin):
    cursor.execute('''SELECT
        balance
    FROM
        card
    WHERE 
        number = ?
        AND pin = ?
        ;''', (str(card), str(pin)))
    if variant == 1:
        print(f'Balance: {cursor.fetchone()[0]}')
        print_login_menu()
        user_choice_login(int(input()), card, pin)
    elif variant == 2:
        print('Enter income:')
        cursor.execute('UPDATE card SET balance = balance + (?) WHERE number = (?) AND pin = (?)', (int(input()), card, pin))
        connection.commit()
        print("Income was added!")
        print_login_menu()
        user_choice_login(int(input()), card, pin)
    elif variant == 3:
        print('Transfer:\nEnter card number')
        card_input = input()
        cursor.execute('SELECT COUNT(*) FROM card WHERE number = (?);', (card_input, ))
        connection.commit()
        if card == card_input:
            print("You can't transfer money to the same account!")
            print_login_menu()
            user_choice_login(int(input()), card, pin)
        elif pass_luhn(card_input) is False:
            print('Probably you made a mistake in the card number. Please try again!')
            print_login_menu()
            user_choice_login(int(input()), card, pin)
        elif cursor.fetchone()[0] == 0:
            print('Such a card does not exist.')
            print_login_menu()
            user_choice_login(int(input()), card, pin)
        else:
            print('Enter how much money you want to transfer:')
            transfer_amount = int(input())
            cursor.execute('''SELECT
                balance
            FROM
                card
            WHERE 
                number = ?
                AND pin = ?;''', (str(card), str(pin)))
            balance = cursor.fetchone()[0]
            if transfer_amount > balance:
                print('Not enough money!')
                print_login_menu()
                user_choice_login(int(input()), card, pin)
            else:
                cursor.execute('UPDATE card SET balance = balance + (?) WHERE number = (?)', (transfer_amount, card_input))
                connection.commit()
                cursor.execute('UPDATE card SET balance = balance - (?) WHERE number = (?)', (transfer_amount, card))
                connection.commit()
                print('Income was added!')
                print_login_menu()
                user_choice_login(int(input()), card, pin)
    elif variant == 4:
        cursor.execute('DELETE FROM card WHERE number = (?) AND pin = (?)', (card, pin))
        connection.commit()
        print('The account has been closed!')
        print_menu()
        user_choice(int(input()))
    elif variant == 5:
        print('You have successfully logged out!')
        print_menu()
        user_choice(int(input()))
    elif variant == 0:
        print('Bye!')
        cursor.close()
        exit()
    else:
        print_menu()
        user_choice(int(input()))


print_menu()
user_choice(int(input()))
