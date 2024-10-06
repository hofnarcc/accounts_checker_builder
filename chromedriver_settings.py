# Import necessary modules
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set the path to chromedriver.exe
chromedriver_path = ChromeDriverManager().install()  # Use webdriver-manager to download ChromeDriver
# OR
# chromedriver_path = os.path.abspath(r"C:\Path\To\chromedriver.exe")
