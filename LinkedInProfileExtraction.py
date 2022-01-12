from LinkedInScraper import LinkedInScraper, WriteEmployeeURLsToFile, \
    DATABASE, USERNAME, PASSWORD, DRIVER_PATH
from Employee import Employee
from LinkedInDBAccess import LinkedInDB

import schedule
import time

# Set Timeline to activate scraper
    # Scrape profiles from employeeURLs.txt until the list ends or LinkedIn blocks scraper

def scrapeProfiles():
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, DATABASE)

    for i, URL in enumerate(driver.__employeeURLs__):
        empList = [driver.ExtractProfileAttributes(URL)]

        if empList[0] is None:
            # Write remaining employees to file
            WriteEmployeeURLsToFile("employeeURLs.txt", driver.__employeeURLs__[i:])
            print("ERROR:", URL, "did not extract properly. There is either a bug or scraping was blocked.")
            break
        else:
            # Insert emp into database
            DATABASE.InsertEmployees(empList)


schedule.every().day.at("24:00").do(scrapeProfiles, 'Beginning Scraping of LinkedIn Profiles')

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute