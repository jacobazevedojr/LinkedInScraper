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
        empList = [driver.ExtractProfileAttributes(URL)]

        if empList[0] is None:
            # Write remaining employees to file
            WriteLinesToFile("employeeURLs.txt", driver.__employeeURLsToBeScraped__[i:])
            print("ERROR:", URL, "did not extract properly. There is either a bug or scraping was blocked.")
            break
        else:
            # Insert emp into database
            DATABASE.InsertEmployees(empList)

'''
schedule.every().day.at("00:00").do(scrapeProfiles)

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute
'''

driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, DATABASE)


emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/josh-braida-358a5476")
print(emp)
DATABASE.InsertEmployees([emp])

emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/anushanandam")
print(emp)
DATABASE.InsertEmployees([emp])


emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/helly-patel-b3a804129")
print(emp)
DATABASE.InsertEmployees([emp])


emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/akshaysathiya")
print(emp)
DATABASE.InsertEmployees([emp])


emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/girishrawat")
print(emp)
DATABASE.InsertEmployees([emp])

