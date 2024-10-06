import tkinter as tk
import webbrowser
import subprocess
import sys
import platform
import threading

def open_html_file():
    # Open the info.html file in the default browser
    webbrowser.open("info.html")

print(f"=============================================================================|")
print(f"=============================================================================|")
print(f"Checking if Python has all required packages installed")
print(f"=============================================================================|")
print(f"=============================================================================|")

def check_python_version():
    """
    Checks if Python 3.11.8 is installed.
    If not, prompts the user to download it.
    """
    python_version = platform.python_version()
    if python_version != "3.11.8":
        print(f"Python 3.11.8 is required. You have {python_version} installed.")
        print("Please download Python 3.11.8 from: https://www.python.org/downloads/")
        sys.exit(1)

def install_or_upgrade_package(package_name):
    """
    Attempts to install or upgrade a package using pip.
    If installation fails, tries to upgrade. If both fail, tries with --user option.

    Args:
        package_name (str): Package to install or upgrade.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} package installed successfully.")
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
            print(f"{package_name} package upgraded successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install/upgrade {package_name} for all users. Trying with --user option.")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--user", "--no-warn-script-location"])
                print(f"{package_name} package installed for current user with --user option.")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package_name} with --user option.")

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
        print(f"{name_line}\n{version_line}")
    except subprocess.CalledProcessError:
        install_or_upgrade_package(package_name)

# Check Python version
check_python_version()

# Packages to install/upgrade
packages = ["tk", "web-browser", "selenium", "webdriver-manager", "requests", "undetected-chromedriver", "colorama", "selenium-wire"]

# Check and install/upgrade each package
for package in packages:
    check_package_installed_upgraded(package)

print(f"=============================================================================|")
print(f"=============================================================================|")
print(f"All required packages are up to date! Starting Menu..")
print(f"=============================================================================|")
print(f"=============================================================================|")

def run_script(script_name):
    """Run a script in a separate thread, adding the --no-warn-script-location option."""
    try:
        thread = threading.Thread(target=subprocess.run, args=(["python", script_name, "--no-warn-script-location"],))
        thread.start()
    except FileNotFoundError:
        print(f"Error: Script '{script_name}' not found.")

def create_button(root, text, script_name, row, column):
    """Create a button to run a script."""
    button = tk.Button(root, text=text, command=lambda: run_script(script_name))
    button.grid(row=row, column=column, padx=10, pady=10, sticky="ew")

# Main GUI Function
def main():
    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("510x300")

    # Add a button to open the info.html file
    info_button = tk.Button(root, text="Info", command=open_html_file)
    info_button.grid(row=0, column=0, padx=10, pady=10)

    create_button(root, "CONFIG CLASSIC", "CONFIG_classic.py", 1, 0)
    create_button(root, "CLASSIC - ACCOUNTS CHECKER", "check_account.py", 2, 0)
    create_button(root, "CONFIG MODERN", "CONFIG_modern.py", 3, 0)
    create_button(root, "MODERN - ACCOUNTS CHECKER", "check_account_modern.py", 4, 0)
    create_button(root, "MODERN - ACCOUNTS CHECKER v1.6.2", "check_account_modern2.py", 5, 0)

    create_button(root, "COMBO CLEANER", "combo_stripper.py", 1, 1)

    create_button(root, "CHROME BROWSER (UPDATER)", "chrome_browser_updater.py", 2, 1)
    create_button(root, "CHROME DRIVER (UPDATER)", "chrome_driver_updater.py", 3, 1)
    create_button(root, "EDIT DEFAULT CHROME PROFILE LOCATION", "edit_default_profile_location.py", 4, 1)
    root.mainloop()

if __name__ == "__main__":
    main()
