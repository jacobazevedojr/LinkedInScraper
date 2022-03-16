from LinkedInScraper import LinkedInScraper, \
    DATABASE, USERNAME, PASSWORD, DRIVER_PATH, \
    WriteLinesToFile, ReadLinesFromFile

import schedule
import time

# Set Timeline to activate scraper
    # Scrape profiles from employeeURLs.txt until the list ends or LinkedIn blocks scraper

def scrapeProfiles():
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, DATABASE)

    previousFail = ""
    scrapingFailed = 0
    successfulScrapes = 0
    maxFailedScrapes = 5
    for i, URL in enumerate(driver.__employeeURLsToBeScraped__):
        if URL in driver.__employeeURLsInDB__:
            print(URL, "Is already a profile in the database")
            continue

        try:
            empList = [driver.ExtractProfileAttributes(URL)]

            # Scraping has failed in some way (but an exception is not thrown)
            if empList[0] is None:
                print("ERROR:", URL, "did not extract properly. There is either a bug or scraping was blocked.")
                # If a URL has failed twice, remove it from the list (doesn't account for blocked scraping,
                # but losing one datapoint is ok)
                if previousFail == URL:
                    successfulScrapes = i + 1
                    scrapingFailed += 1
                    continue
                previousFail == URL

                # If scraping has failed 5 times in a row, stop scraping and eliminate from list
                # This is to account for blocked scraping
                # This makes an assumption that 5 broken URLs in a row is unlikely
                if scrapingFailed > maxFailedScrapes - 1:
                    successfulScrapes = i
                    break
            else:
                # Insert emp into database
                scrapingFailed = 0
                DATABASE.insertEmployees(empList)
                successfulScrapes = i
        except:
            print(URL, "cannot be extracted, deleting")
            WriteLinesToFile("employeeURLs.txt", driver.__employeeURLsToBeScraped__[i+1:])
            with open("URLsWithErrors.txt", "a+") as file:
                file.write(URL + "\n")
            continue

    # Rewrite file to chop off all successfully scraped files
    WriteLinesToFile("employeeURLs.txt", driver.__employeeURLsToBeScraped__[successfulScrapes:])
    print(successfulScrapes, "profiles, successfully extracted")


schedule.every().day.at("00:00").do(scrapeProfiles)
schedule.every().day.at("02:00").do(scrapeProfiles)
schedule.every().day.at("22:00").do(scrapeProfiles)

print("Initial Test Run of Profile Scraper...")
scrapeProfiles()

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute


