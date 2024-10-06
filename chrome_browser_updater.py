import os
import platform
import subprocess
import sys
import urllib.request
import winreg

def is_64bit_windows():
    return platform.machine().endswith('64')

def get_chrome_download_url():
    base_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    return base_url

def download_chrome(url, output_path):
    print("Downloading Chrome...")
    urllib.request.urlretrieve(url, output_path)
    print("Download complete.")

def run_chrome_installer(installer_path):
    print("Running Chrome installer...")
    subprocess.run([installer_path], check=True)

def main():
    # Detect Windows version
    if is_64bit_windows():
        print("Detected 64-bit Windows")
    else:
        print("Detected 32-bit Windows")

    # Get Chrome download URL
    download_url = get_chrome_download_url()

    # Set the output path for the installer
    output_path = os.path.join(os.environ['TEMP'], 'chrome_installer.exe')

    # Download Chrome
    download_chrome(download_url, output_path)

    # Run the Chrome installer
    run_chrome_installer(output_path)

    print("Chrome installation wizard opened. Please follow the on-screen instructions to complete the installation.")

if __name__ == "__main__":
    main()
