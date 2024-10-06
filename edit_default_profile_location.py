import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess

def edit_default_profile_location(new_location, script_paths):
    """
    Edits the 'user_data_dir' line in the specified scripts.

    Args:
        new_location (str): The new location for the user data directory.
        script_paths (list): A list of paths to the scripts to modify.
    """

    for script_path in script_paths:
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()

            # Properly escape special characters in the new location
            escaped_location = new_location.replace("\\", "\\\\") 

            # Replace the 'user_data_dir' line with the new location
            new_content = re.sub('user_data_dir = r".*?"', f'user_data_dir = r"{escaped_location}"', script_content)

            with open(script_path, 'w') as f:
                f.write(new_content)

            print(f"Modified 'user_data_dir' in {script_path}")

        except FileNotFoundError:
            print(f"Error: Script not found at {script_path}")

def reset_to_default():
    """
    Resets the user data directory to the default location:
    C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1
    """
    new_location = r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data\Profile 1"
    edit_default_profile_location(new_location, script_paths)
    messagebox.showinfo("Success", "User data directory reset to default.")

def update_location():
    """
    Updates the user data directory to the location provided in the entry field.
    """
    new_location = entry_location.get()
    edit_default_profile_location(new_location, script_paths)
    messagebox.showinfo("Success", "User data directory updated.")

def open_profile_directory():
    """
    Opens the default Chrome profile directory.
    """
    profile_path = r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data"
    try:
        os.startfile(profile_path)  # Use os.startfile to open the directory
    except FileNotFoundError:
        messagebox.showerror("Error", "Watch the instruction videos again. You need to create a Google Chrome browser profile first.")

def browse_directory():
    """
    Opens a file dialog to choose the new user data directory.
    """
    directory = filedialog.askdirectory(initialdir=r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data")
    if directory:
        entry_location.delete(0, tk.END)
        entry_location.insert(0, directory)

# Script paths (Make sure these are correct!)
script_paths = [
    "CONFIG_classic.py",
    "check_account.py",
    "CONFIG_modern.py",
    "check_account_modern.py"
]

# GUI setup
window = tk.Tk()
window.title("Edit Google Chrome User Data Profile Directory")

# Label and Entry for new location
ttk.Label(window, text="Enter the new Google Chrome User Data Profile Directory location:").grid(column=0, row=0, padx=10, pady=10, columnspan=2)
entry_location = ttk.Entry(window, width=70)
entry_location.grid(column=0, row=1, padx=10, pady=10, columnspan=2)

# Default value for entry
entry_location.insert(0, r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data\Profile 1")

# Buttons
ttk.Button(window, text="Browse", command=browse_directory).grid(column=0, row=2, pady=10, columnspan=2)
ttk.Button(window, text="Update Location", command=update_location).grid(column=0, row=4, pady=10, columnspan=2)

# Instructions
ttk.Label(window, text="Instructions:").grid(column=0, row=5, padx=10, pady=10, columnspan=2)
ttk.Label(window, text="1.  Click on Browse").grid(column=0, row=6, padx=10, pady=2, columnspan=2)
ttk.Label(window, text="2.  Select the Google Chrome User Profile folder you want to use").grid(column=0, row=7, padx=10, pady=2, columnspan=2)
ttk.Label(window, text="3.  Click on 'Update Location'").grid(column=0, row=8, padx=10, pady=2, columnspan=2)

window.mainloop()
