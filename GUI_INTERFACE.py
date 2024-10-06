import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

# Global variable to store the config file path
config_file_path = None

# Function to print actions in the output area
def print_action(text):
    output_area.config(state="normal")
    output_area.insert(tk.END, text + "\n")
    output_area.config(state="disabled")

# Function to create a new config file
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

# Function to import an existing config file
def import_config():
    """Opens a window for importing an existing config file."""
    global config_file_path
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Import Config", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        config_file_path = file_path
        load_config_data(config_file_path)
        print_action(f"Config file imported from: {file_path}")

# Function to export the current config file
def export_config():
    """Opens a window for exporting the current config file."""
    global config_file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=(("Text Files", "*.txt"),))
    if file_path:
        config_file_path = file_path
        save_config_data(config_file_path)
        print_action(f"Config file exported to: {file_path}")

# Function to save the current state of the config
def save_config_state():
    """Saves the current state of the config to a file."""
    global config_file_path

    if not config_file_path:
        create_config()  # Prompt user to create a config file if none exists

    if config_file_path:
        save_config_data(config_file_path)
        print_action(f"Config state saved to: {config_file_path}")

# Function to load config data from a file
def load_config_data(file_path):
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

# Function to save config data to a file
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

# Create the main window
window = tk.Tk()
window.title("Config Manager")

# Create the input and output areas
# ... (rest of your GUI code here, including labels, entries, and buttons)

# Create the output area
output_area = tk.Text(window, state="disabled", wrap=tk.WORD, height=5)
output_area.pack(fill=tk.BOTH, expand=True)

# Run the main loop
window.mainloop()
