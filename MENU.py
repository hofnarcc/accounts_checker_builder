import tkinter as tk
from tkinter import messagebox
import webbrowser
import subprocess
import sys
import platform
import threading
import logging
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("application.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def open_html_file():
    """Open the info.html file in the default browser."""
    try:
        webbrowser.open("info.html")
        logging.info("Opened info.html in the default browser.")
    except Exception as e:
        logging.error(f"Failed to open info.html: {e}")
        messagebox.showerror("Error", f"Failed to open info.html: {e}")

def check_python_version():
    """
    Checks if Python 3.11.8 is installed.
    If not, prompts the user to download it.
    """
    python_version = platform.python_version()
    if python_version != "3.11.8":
        logging.warning(f"Python 3.11.8 is required. You have {python_version} installed.")
        message = (
            f"Python 3.11.8 is required.\nYou have {python_version} installed.\n"
            "Please download Python 3.11.8 from: https://www.python.org/downloads/"
        )
        messagebox.showerror("Python Version Mismatch", message)
        sys.exit(1)
    logging.info("Python version is 3.11.8.")

def install_or_upgrade_package(package_name):
    """
    Attempts to install or upgrade a package using pip.
    If installation fails, tries to upgrade. If both fail, tries with --user option.

    Args:
        package_name (str): Package to install or upgrade.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logging.info(f"{package_name} package installed successfully.")
    except subprocess.CalledProcessError:
        logging.warning(f"Failed to install {package_name}. Attempting to upgrade.")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
            logging.info(f"{package_name} package upgraded successfully.")
        except subprocess.CalledProcessError:
            logging.warning(f"Failed to install/upgrade {package_name}. Trying with --user option.")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package_name, "--user", "--no-warn-script-location"
                ])
                logging.info(f"{package_name} package installed for current user with --user option.")
            except subprocess.CalledProcessError:
                logging.error(f"Failed to install {package_name} with --user option.")
                messagebox.showerror("Installation Error", f"Failed to install {package_name}.")

def check_package_installed_upgraded(package_name):
    """
    Checks if a package is installed and up-to-date. If not, attempts to install/upgrade.

    Args:
        package_name (str): Package to check.
    """
    try:
        output = subprocess.check_output([sys.executable, "-m", "pip", "show", package_name]).decode("utf-8")
        name_line = output.splitlines()[0]
        version_line = output.splitlines()[1]
        logging.info(f"{name_line}\n{version_line}")
    except subprocess.CalledProcessError:
        logging.info(f"{package_name} not found. Attempting to install.")
        install_or_upgrade_package(package_name)

def run_script(script_name):
    """Run a script asynchronously."""
    try:
        subprocess.Popen(["python", script_name, "--no-warn-script-location"])
        logging.info(f"Executed script: {script_name}")
    except Exception as e:
        logging.error(f"Error executing script: {script_name}. Exception: {e}")
        messagebox.showerror("Script Error", f"Error executing script: {script_name}\nException: {e}")

def create_button(root, text, script_name, row, column):
    """Create a styled button to run a script."""
    button = tk.Button(
        root,
        text=text,
        command=partial(run_script, script_name),
        bg="#2e2e2e",
        fg="#ffffff",
        font=("Helvetica", 10, "bold"),
        relief=tk.RAISED,
        padx=10,
        pady=5
    )
    button.grid(row=row, column=column, padx=10, pady=10, sticky="ew")

def check_requirements():
    """Check Python version and required packages."""
    check_python_version()
    packages = [
        "tk", "selenium", "webdriver-manager",
        "requests", "undetected-chromedriver", "colorama",
        "pyautogui", "Pillow"
    ]

    threads = []
    for package in packages:
        thread = threading.Thread(target=check_package_installed_upgraded, args=(package,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    logging.info("All required packages are up to date.")
    messagebox.showinfo("Setup Complete", "All required packages are up to date! Starting Menu...")

def main_gui():
    """Main GUI Function."""
    root = tk.Tk()
    root.title("Main Menu - [ THIS TOOL IS 100% CREATED BY AI: https://t.me/hofnar05_Worm_GPT ]")
    root.geometry("1190x400")
    root.configure(bg="#1e1e1e")

    # Configure grid
    for i in range(7):
        root.grid_rowconfigure(i, weight=1)
    for j in range(2):
        root.grid_columnconfigure(j, weight=1)

    # Info & Instructions Button
    info_button = tk.Button(
        root,
        text="INFO & INSTRUCTIONS",
        command=open_html_file,
        bg="#4a90e2",
        fg="#ffffff",
        font=("Helvetica", 12, "bold"),
        relief=tk.RAISED,
        padx=10,
        pady=5
    )
    info_button.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

    # Script Buttons
    scripts = [
        ("CONFIG CLASSIC", "CONFIG_classic.py", 1, 0),
        ("CLASSIC - ACCOUNTS CHECKER", "check_account.py", 2, 0),
        ("CONFIG MODERN [DESIGNED FOR MODERN WEBINTERFACE]", "CONFIG_modern.py", 3, 0),
        ("V1 - ACCOUNTS CHECKER [DESIGNED FOR MODERN WEBINTERFACE]", "check_account_modern.py", 4, 0),
        ("V2 - ACCOUNTS CHECKER [DESIGNED FOR MODERN WEBINTERFACE]", "check_account_modern2.py", 5, 0),
        ("V3 - ACCOUNTS CHECKER => ULTIMATE CAPTURE EDITION <= [DESIGNED FOR MODERN WEBINTERFACE] v1.6.7", "ULTIMATE-CHECKER.py", 6, 0),
        ("COMBO CLEANER", "combo_stripper.py", 1, 1),
        ("COMBO SORTER", "ComboToolz.py", 2, 1),
        ("CHROME BROWSER (UPDATER)", "chrome_browser_updater.py", 3, 1),
        ("CHROME DRIVER (UPDATER)", "chrome_driver_updater.py", 4, 1),
        ("EDIT DEFAULT CHROME PROFILE LOCATION", "edit_default_profile_location.py", 5, 1)
    ]

    for text, script, row, column in scripts:
        create_button(root, text, script, row, column)

    # Start the GUI event loop
    root.mainloop()

def main():
    """Main entry point of the application."""
    try:
        check_requirements()
        main_gui()
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
        messagebox.showerror("Critical Error", f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()