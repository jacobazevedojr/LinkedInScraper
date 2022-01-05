from LinkedInDBAccess import LinkedInDB
from LinkedInScraper import LinkedInScraper, GetUsernameAndPassword, WriteEmployeeURLsToFile

from Employee import Employee

# Change to desired driver path
DRIVER_PATH = "C:\\Users\\jacob\\Desktop\\Senior Thesis\\chromedriver.exe"

# Either change driver code, or create a file called "creds.txt" in the working directory
USERNAME, PASSWORD = GetUsernameAndPassword("creds.txt")
DATABASE_USERNAME, DATABASE_PASSWORD = GetUsernameAndPassword("dbcreds.txt")
DATABASE = LinkedInDB("linkedin", "10.33.113.250", 3308, DATABASE_USERNAME, DATABASE_PASSWORD)

def MakeQueryCombinations(companies, positions, locations):
    queries = []
    for company in companies:
        for position in positions:
            for location in locations:
                queries.append(company + " " + position + " " + location)
    return queries

def LoadQueries():
    queries = []
    with open("queries.txt", "r") as file:
        for line in file:
            queries.append(line)
    return queries

def WriteQueries(queries):
    with open("queries.txt", "w") as file:
        for query in queries:
            if len(query.strip()) > 0:
                file.write(query + "\n")

# Driver Code
if USERNAME and PASSWORD != "":
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, DATABASE)

    companies = ["Microsoft", "Tesla", "Facebook", "Apple", "Amazon", "Netflix", "Oracle", "IBM", "SAP", "Paypal",
                 "Salesforce", "Adobe", "VMWare", "Intuit", "Workday", "Palo Alto Networks", "Autodesk", "Zoom",
                 "Splunk", "Twilio", "DocuSign", "Palantir", "Samsung", "Dell", "Meta", "Sony", "Intel", "HP",
                 "Uber", "Lyft", "eBay", "Spotify", "Twitter", "Zillow", "Airbnb", "Stripe", "DoorDash", "Snap",
                 "Dropbox", "Pinterest"]
    positions = ["Software Engineer", "Software Developer", "Software Development Engineer", "SWE", "SDE",
                 "Software Engineer I", "Software Engineer II", "Software Engineer III",
                 "Senior Software Engineer", "Principal Engineer", "Engineering Manager",
                 "Director of Engineering", "VP of Engineering", "Software Architect", "Software Programmer",
                 "QA Engineer", "Senior QA Engineer", "Technical Lead", "Senior Technical Lead",
                 "Senior Software Architect", "Technical Manager", "Senior Technical Manager"]
    locations = ["San Francisco, CA", "San Francisco Bay Area", "San Jose, CA", "Silicon Valley", "Los Angeles, CA",
                 "San Diego, CA", "Silicon Beach", "Seattle, WA", "Redmond, WA", "New York City, NY", "New York",
                 "Boston, MA", "Austin, TX", "Dallas, TX", "Houston, TX", "Dallas-Ft. Worth, TX", "Washington D.C.",
                 "Chicago, IL", "Huntsville, AL", "Boulder, CO", "Denver, CO", "Cleveland, OH", "Columbus, OH",
                 "Atlanta, GA", "Remote", "Raleigh, NC", "Charlotte, NC", "Durham-Chapel Hill, NC", "Baltimore, MD",
                 "Madison, WI", "Trenton, NJ", "Provo, UT", "Las Vegas, NV", "Salt Lake City, UT", "Saint Louis, MO",
                 "Detriot, MI", "Nashville, TN", "Arlington, VI", "Phoenix, AZ", "Orlando, FL", "Miami, FL",
                 "Jacksonville, FL"]

    queries = MakeQueryCombinations(companies, positions, locations)
    WriteQueries(queries)

    '''
    queries = LoadQueries()

    lastQueryIndex = 0
    for i, query in enumerate(queries):
        success = driver.LinkedInPeopleSearch(query)
        if not success:
            lastQueryIndex = i
            break

    # Eliminate all successful queries from previous run
    WriteQueries(queries[lastQueryIndex:])
    '''

    #driver.BatchLinkedInPeopleSearch(queries)
    #WriteEmployeeURLsToFile("employeeURLs.txt", driver.employeeURLs)