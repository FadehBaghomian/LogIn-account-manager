import tkinter as tk
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet
import os
import json
import re

# Generate a key and instantiate a Fernet instance
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def initialize():
    if not os.path.exists("secret.key"):
        generate_key()

    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)

    if not os.path.exists("passwords.json"):
        with open("passwords.json", "w") as f:
            json.dump({}, f)

def encrypt_message(message: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message.decode()

def decrypt_message(encrypted_message: str, key: bytes) -> str:
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())
    return decrypted_message.decode()

def add_user(username: str, password: str, key: bytes):
    with open("users.json", "r") as f:
        users = json.load(f)

    if username in users:
        return False

    encrypted_password = encrypt_message(password, key)
    users[username] = encrypted_password

    with open("users.json", "w") as f:
        json.dump(users, f)
    return True

def authenticate_user(username: str, password: str, key: bytes) -> bool:
    with open("users.json", "r") as f:
        users = json.load(f)

    if username in users:
        encrypted_password = users[username]
        decrypted_password = decrypt_message(encrypted_password, key)
        return password == decrypted_password
    return False

def add_password(username: str, account: str, password: str, key: bytes):
    with open("passwords.json", "r") as f:
        passwords = json.load(f)

    if username not in passwords:
        passwords[username] = {}

    encrypted_password = encrypt_message(password, key)
    passwords[username][account] = encrypted_password

    with open("passwords.json", "w") as f:
        json.dump(passwords, f)

def get_password(username: str, account: str, key: bytes) -> str:
    with open("passwords.json", "r") as f:
        passwords = json.load(f)

    if username in passwords and account in passwords[username]:
        encrypted_password = passwords[username][account]
        return decrypt_message(encrypted_password, key)
    else:
        return None

def list_accounts(username: str):
    with open("passwords.json", "r") as f:
        passwords = json.load(f)

    if username in passwords:
        return passwords[username].keys()
    else:
        return []

def delete_account(username: str, account: str):
    with open("passwords.json", "r") as f:
        passwords = json.load(f)

    if username in passwords and account in passwords[username]:
        del passwords[username][account]

        with open("passwords.json", "w") as f:
            json.dump(passwords, f)
        return True
    else:
        return False

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

class PasswordManagerApp(tk.Tk):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.title("Password Manager")
        self.geometry("400x300")

        self.label = tk.Label(self, text="Log In or Make Account", font=("Arial", 20))
        self.label.pack(pady=10)

        self.username = None

        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(pady=10)

        self.login_button = tk.Button(self.menu_frame, text="Log In", command=self.login_screen)
        self.login_button.pack(pady=5)

        self.register_button = tk.Button(self.menu_frame, text="Make Account", command=self.register_screen)
        self.register_button.pack(pady=5)

        self.login_frame = tk.Frame(self)
        self.register_frame = tk.Frame(self)
        self.main_frame = tk.Frame(self)

        self.create_login_frame()
        self.create_register_frame()

    def create_login_frame(self):
        self.username_label = tk.Label(self.login_frame, text="Username")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Password")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.back_button = tk.Button(self.login_frame, text="Back", command=self.show_main_menu)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=5)

    def create_register_frame(self):
        self.username_label = tk.Label(self.register_frame, text="Username")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.register_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.register_frame, text="Password")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.register_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.register_button = tk.Button(self.register_frame, text="Register", command=self.register)
        self.register_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.back_button = tk.Button(self.register_frame, text="Back", command=self.show_main_menu)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=5)

    def show_main_menu(self):
        self.label.config(text="Log In or Make Account")
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.menu_frame.pack(pady=10)

    def login_screen(self):
        self.label.config(text="Enter Member Credentials")
        self.menu_frame.pack_forget()
        self.login_frame.pack(pady=10)

    def register_screen(self):
        self.label.config(text="Registration")
        self.menu_frame.pack_forget()
        self.register_frame.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if authenticate_user(username, password, self.key):
            self.username = username
            messagebox.showinfo("Success", "Logged in successfully!")
            self.login_frame.pack_forget()
            self.main_frame.pack(pady=10)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if is_valid_password(password):
            if add_user(username, password, self.key):
                messagebox.showinfo("Success", "User registered successfully!")
                self.register_frame.pack_forget()
                self.login_screen()
            else:
                messagebox.showerror("Error", "Username already exists")
        else:
            messagebox.showerror("Error", "Password must be at least 8 characters long and contain at least one special character")

    def add_password(self):
        account = simpledialog.askstring("Account", "Enter the account name:")
        while True:
            password = simpledialog.askstring("Password", "Enter the password:", show='*')
            if password and is_valid_password(password):
                add_password(self.username, account, password, self.key)
                messagebox.showinfo("Success", "Password added successfully!")
                break
            else:
                messagebox.showerror("Error", "Password must be at least 8 characters long and contain at least one special character.")

    def retrieve_password(self):
        account = simpledialog.askstring("Account", "Enter the account name:")
        if account:
            password = get_password(self.username, account, self.key)
            if password:
                messagebox.showinfo("Password", f"The password for {account} is {password}")
            else:
                messagebox.showerror("Error", "Account not found!")

    def list_accounts(self):
        accounts = list(list_accounts(self.username))
        if accounts:
            accounts_list = "\n".join(accounts)
            messagebox.showinfo("Stored Accounts", f"Stored accounts:\n{accounts_list}")
        else:
            messagebox.showinfo("No Accounts", "No accounts found!")

    def delete_account(self):
        account = simpledialog.askstring("Account", "Enter the account name:")
        if account:
            if delete_account(self.username, account):
                messagebox.showinfo("Success", f"Account {account} deleted successfully!")
            else:
                messagebox.showerror("Error", "Account not found!")

if __name__ == "__main__":
    initialize()
    key = load_key()

    app = PasswordManagerApp(key)
    app.mainloop()


