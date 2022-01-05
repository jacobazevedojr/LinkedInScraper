from LinkedInDBAccess import LinkedInDB
from LinkedInScraper import LinkedInScraper, WriteEmployeeURLsToFile, \
    DATABASE, USERNAME, PASSWORD, DRIVER_PATH

from Employee import Employee

def MakeQueryCombinations(companies, positions, locations):
    queries = []
    for company in companies:
        for position in positions:
            for location in locations:
                queries.append(company + " " + position + " " + location)
    return queries


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

    print("Number of Queries:", len(queries))

    emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/josh-braida-358a5476")
    print(emp)

    emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/anushanandam")
    print(emp)

    emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/helly-patel-b3a804129")
    print(emp)

    emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/akshaysathiya")
    print(emp)

    emp = driver.ExtractProfileAttributes("https://www.linkedin.com/in/girishrawat")
    print(emp)


    #driver.BatchLinkedInPeopleSearch(queries)
    #WriteEmployeeURLsToFile("employeeURLs.txt", driver.employeeURLs)