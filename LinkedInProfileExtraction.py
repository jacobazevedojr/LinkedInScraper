from LinkedInScraper import LinkedInScraper, \
    DATABASE, USERNAME, PASSWORD, DRIVER_PATH, \
    WriteLinesToFile, ReadLinesFromFile

import schedule
import time

# Set Timeline to activate scraper
    # Scrape profiles from employeeURLs.txt until the list ends or LinkedIn blocks scraper

def scrapeProfiles():
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, DATABASE)

    for i, URL in enumerate(driver.__employeeURLsToBeScraped__):
        if URL in driver.__employeeURLsInDB__:
            print(URL, "Is already a profile in the database")
            continue

        try:
            empList = [driver.ExtractProfileAttributes(URL)]

            if empList[0] is None:
                # Write remaining employees to file
                WriteLinesToFile("employeeURLs.txt", driver.__employeeURLsToBeScraped__[i:])
                print("ERROR:", URL, "did not extract properly. There is either a bug or scraping was blocked.")
                break
            else:
                # Insert emp into database
                DATABASE.insertEmployees(empList)
        except:
            print(URL, "cannot be extracted, deleting")
            WriteLinesToFile("employeeURLs.txt", driver.__employeeURLsToBeScraped__[i+1:])
            with open("URLsWithErrors.txt", "a+") as file:
                file.write(URL + "\n")
            continue



schedule.every().day.at("00:00").do(scrapeProfiles)
schedule.every().day.at("02:00").do(scrapeProfiles)
schedule.every().day.at("22:00").do(scrapeProfiles)

print("Initial Test Run of Profile Scraper...")
scrapeProfiles()

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute


