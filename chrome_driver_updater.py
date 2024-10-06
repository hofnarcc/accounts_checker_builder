import requests
import zipfile
import io
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

def download_chromedriver(download_url):
    """Downloads the ChromeDriver from the specified URL."""
    response = requests.get(download_url)
    response.raise_for_status()
    return response.content

def download_file():
    """Downloads the ChromeDriver zip file based on the user-provided URL."""
    download_url = url_entry.get()

    if not download_url:
        messagebox.showerror("Error", "Please enter a valid download URL.")
        return

    try:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Download the zip file
        content = download_chromedriver(download_url)

        # Save the downloaded file to the script's directory
        downloaded_file_path = os.path.join(script_dir, "chromedriver.zip")
        with open(downloaded_file_path, "wb") as f:
            f.write(content)

        messagebox.showinfo("Success", "ChromeDriver zip file has been downloaded to the script's directory.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error downloading ChromeDriver: {e}")
        print(f"Response status code: {e.response.status_code if e.response else 'N/A'}")
        print(f"Response content: {e.response.text if e.response else 'N/A'}")
    except OSError as e:
        messagebox.showerror("Error", f"Error: Could not save the downloaded file: {e}")

def open_downloads_page():
    """Opens the ChromeDriver downloads page in the web browser."""
    webbrowser.open_new_tab("https://googlechromelabs.github.io/chrome-for-testing/#stable")

def select_zip_file():
    """Opens a file dialog to select a zip file."""
    global selected_zip_file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    selected_zip_file = filedialog.askopenfilename(
        initialdir=script_dir,  # Set the initial directory to the script's directory
        title="Select a Zip File",
        filetypes=(("Zip files", "*.zip"), ("all files", "*.*"))
    )
    if selected_zip_file:
        zip_file_label.config(text=f"Selected Zip File: {selected_zip_file}")
    else:
        zip_file_label.config(text="No Zip File Selected")

def extract_zip_file():
    """Extracts the selected zip file to the script's directory."""
    if not selected_zip_file:
        messagebox.showerror("Error", "Please select a zip file first.")
        return

    try:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Extract the zip file to the script's directory
        with zipfile.ZipFile(selected_zip_file) as zip_ref:
            zip_ref.extractall(script_dir)

        messagebox.showinfo("Success", "Zip file extracted successfully.")
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "Error: The selected file is not a valid zip file.")
    except OSError as e:
        messagebox.showerror("Error", f"Error: Could not extract zip file: {e}")

def select_file_to_move():
    """Opens a file dialog to select a file to move."""
    global selected_file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    selected_file = filedialog.askopenfilename(
        initialdir=script_dir,  # Set the initial directory to the script's directory
        title="Select a File",
        filetypes=(("All Files", "*.*"),)
    )
    if selected_file:
        file_label.config(text=f"Selected File: {selected_file}")
    else:
        file_label.config(text="No File Selected")

def move_file():
    """Moves the selected file to the user-chosen destination."""
    if not selected_file:
        messagebox.showerror("Error", "Please select a file first.")
        return

    try:
        # Get the user-chosen destination path
        destination_path = filedialog.askdirectory(
            initialdir=os.path.dirname(selected_file),
            title="Choose Destination Folder"
        )
        if not destination_path:
            return  # User canceled

        # Move the selected file to the chosen destination
        shutil.move(selected_file, destination_path)

        messagebox.showinfo("Success", "File moved successfully.")
    except OSError as e:
        messagebox.showerror("Error", f"Error: Could not move file: {e}")

# Create the main window
window = tk.Tk()
window.title("File Utility")

# URL label and entry
url_label = tk.Label(window, text="Click the link below & find the download link for the chromedriver:")
url_label.pack()

url_label = tk.Label(window, text="https://googlechromelabs.github.io/chrome-for-testing/#stable", fg="blue", cursor="hand2")
url_label.pack()
url_label.bind("<Button-1>", lambda event: open_downloads_page())

# Download URL label and entry
url_label = tk.Label(window, text="Enter ChromeDriver Download URL:")
url_label.pack()

url_entry = tk.Entry(window, width=150)
url_entry.pack()

# Download button
download_button = tk.Button(window, text="Provide the link & Download the latest chromedriver for the win64 platform", command=download_file)
download_button.pack()

# Zip file selection section
zip_file_label = tk.Label(window, text="No Zip File Selected")
zip_file_label.pack()

select_zip_button = tk.Button(window, text="Select /win64/chromedriver-win64.zip file to extract", command=select_zip_file)
select_zip_button.pack()

extract_zip_button = tk.Button(window, text="Extract Zip File", command=extract_zip_file)
extract_zip_button.pack()

# File selection section
file_label = tk.Label(window, text="No File Selected")
file_label.pack()

select_file_button = tk.Button(window, text="Select the new chromedriver.exe File to move it in the same directory as where the script is being executed", command=select_file_to_move)
select_file_button.pack()

move_file_button = tk.Button(window, text="Move File", command=move_file)
move_file_button.pack()

window.mainloop()