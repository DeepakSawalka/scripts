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
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.views-row"))
)
        logging.info("Page content loaded successfully.")
        break
    except Exception as e:
        logging.error(f"Error loading page content on attempt {attempt + 1}: {e}")
        if attempt == max_retries - 1:
            logging.error("Max retries reached. Exiting.")
            driver.quit()
            exit()


faculty_data = []
faculty_sections = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
logging.info(f"Number of faculty sections found: {len(faculty_sections)}")

for section in faculty_sections:
    # Extract the faculty name and profile URL
    try:
        name = section.find_element(By.CSS_SELECTOR, "h3.utprof__title a").text.strip()
        profile_url = section.find_element(By.CSS_SELECTOR, "h3.utprof__title a").get_attribute("href")
    except:
        name = "N/A"
        profile_url = "N/A"

    # Add only the basic information initially
    faculty_data.append({
        "Email": "N/A",
        "Name": name,
        "Title": "N/A",
        "Department": "N/A",
        "College": "College of Liberal Arts",
        "University": "University of Texas at Austin",
        "Description": "N/A",
        "profile_url": profile_url,
        "Phone Number" : "N/A",
    })

# Step 2: Visit each profile URL and extract additional information
for faculty in faculty_data:
    profile_url = faculty["profile_url"]
    if profile_url != "N/A":
        try:
            # Navigate to the profile page
            driver.get(profile_url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Extract additional information on the profile page
            try:
                h3_elements = driver.find_elements(By.CSS_SELECTOR, "h3.field__item")
                title = h3_elements[1].text.strip() if len(h3_elements) > 1 else "N/A"
                faculty["Title"] = title
            except:
                faculty["Title"] = "N/A"
            
            try:
                department = driver.find_element(By.CSS_SELECTOR, "div.field__items span.field__item").text.strip()
                faculty["Department"] = department
            except:
                faculty["Department"] = "N/A"
            
            try:
                email = driver.find_element(By.CSS_SELECTOR, "div.utprof__email-address div.field__item a").text.strip()
                faculty["Email"] = email
            except:
                faculty["Email"] = "N/A"
            
            try:
                phone_number = driver.find_element(By.CSS_SELECTOR, "div.utprof__ph-number div.field__item a").text.strip()
                if not phone_number[0].isdigit():
                    phone_number = "N/A"
                faculty["Phone Number"] = phone_number
            except:
                faculty["Phone Number"] = "N/A"

            try:
                # Locate the parent container where the relevant <p> tag resides
                parent_div = driver.find_element(By.CLASS_NAME, "utprof__content")
                # Find all <p> tags within this container
                p_elements = parent_div.find_elements(By.TAG_NAME, "p")
                # Check if the second <p> tag exists and has meaningful content
                if len(p_elements) > 1 and p_elements[1].text.strip():
                    description = p_elements[1].text.strip()
                else:
                    description = "N/A"
                faculty["Description"] = description
            except:
                faculty["Description"] = "N/A"


        except Exception as e:
            logging.warning(f"Could not retrieve information for profile {profile_url}: {e}")

# Convert to DataFrame and save to CSV
if faculty_data:
    logging.info("Faculty data extracted successfully.")
    df = pd.DataFrame(faculty_data)
    csv_filename = "clglblarts_faculty_directory.csv"
    df.to_csv(csv_filename, index=False)
    logging.info(f"Data saved to '{csv_filename}'")
else:
    logging.warning("No faculty data was extracted. Please check the HTML structure or selectors.")

# Close the browser
driver.quit()

