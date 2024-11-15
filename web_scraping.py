from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prompt the user to input the URL of the faculty directory page
url = input("Enter the URL of the faculty directory page: ")

# Set up Selenium WebDriver (update the path to your WebDriver executable)
service = Service('C:/chromedriver-win64/chromedriver.exe')  # Ensure this path is correct
driver = webdriver.Chrome(service=service)
driver.get(url)

# Retry logic for loading the page content
max_retries = 3
for attempt in range(max_retries):
    try:
        logging.info(f"Attempt {attempt + 1}: Waiting for faculty directory content to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.facentry.all-list"))
)
        logging.info("Page content loaded successfully.")
        break
    except Exception as e:
        logging.error(f"Error loading page content on attempt {attempt + 1}: {e}")
        if attempt == max_retries - 1:
            logging.error("Max retries reached. Exiting.")
            driver.quit()
            exit()

# Proceed with the data extraction if the page loaded successfully
faculty_data = []

# Select elements containing faculty information
faculty_sections = driver.find_elements(By.CSS_SELECTOR, "div.facentry.all-list")
logging.info(f"Number of faculty sections found: {len(faculty_sections)}")

# Loop through each faculty section and extract the required information
for i, section in enumerate(faculty_sections, start=1):
    # Extract the faculty name
    try:
    # Locate the <div class="facdata"> and find the <h4> element within it
        name = section.find_element(By.CSS_SELECTOR, "div.facdata h4").text.strip()
    except:
        name = "N/A"
    
    # Extract the faculty position
    try:
        title = section.find_element(By.CSS_SELECTOR, "div.facdata p.facpos").text.strip()
    except:
        title = "N/A"
    
    # Extract the department title
    try:
        department = section.find_element(By.CSS_SELECTOR, "div.facdata p.depttitle").text.strip()
    except:
        department = "N/A"
    
    try:
        contact_info = section.find_element(By.CLASS_NAME, "contact")
        email = contact_info.find_element(By.CLASS_NAME, "email").text.strip()
    except:
        email = "N/A"
    try:
        phone_number = contact_info.text.split("\n")[1].strip() if "\n" in contact_info.text else "N/A"
        if not phone_number[0].isdigit():
            phone_number = "N/A"
    except:
        phone_number = "N/A"

    try:
        profile_url = section.find_element(By.CSS_SELECTOR, "h6 a[href]").get_attribute("href")
    except:
        profile_url = "N/A"
    
    # Extract areas of impact
    try:
        # Find all <p class="test"> elements within <div class="impact"> and join their text
        areas_of_impact = ", ".join([impact.text.strip() for impact in section.find_elements(By.CSS_SELECTOR, ".impact .test")])
    except:
        areas_of_impact = "N/A"
    
    # Extract research interests
    try:
    # Locate the <div class="facareas"> containing the research interests
        research_div = section.find_element(By.CLASS_NAME, "facareas")
    # Extract the text from the second <p> tag within this div (the detailed description)
        research_interests = research_div.find_elements(By.TAG_NAME, "p")[1].text.strip()
    except:
        research_interests = "N/A"

    # Add the extracted data to the list
    faculty_data.append({
        "Email": email,
        "Name": name,
        "Title": title,
        "Department": department,
        "College": "",
        "University": "",
        "Description": research_interests,
        "profile_url": profile_url,
        "Phone Number" : phone_number,
    })

# Convert to DataFrame and save to CSV
if faculty_data:
    logging.info("Faculty data extracted successfully.")
    df = pd.DataFrame(faculty_data)
    csv_filename = "cockrell_faculty_directory.csv"
    df.to_csv(csv_filename, index=False)
    logging.info(f"Data saved to '{csv_filename}'")
else:
    logging.warning("No faculty data was extracted. Please check the HTML structure or selectors.")

# Close the browser
driver.quit()
