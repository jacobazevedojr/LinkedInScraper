from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import time
from typing import List, Set

from Employee import Employee
from Experience import Experience
from Education import Education
from LinkedInDBAccess import LinkedInDB


def ReadLinesFromFile(textFilePath):
    array = []
    with open(textFilePath, "r") as file:
        for line in file:
            array.append(line.strip())

    return array


def WriteLinesToFile(textFilePath, array):
    with open(textFilePath, "w") as file:
        for line in array:
            file.write(line + '\n')

def AppendLinesToFile(textFilePath, array):
    with open(textFilePath, "a") as file:
        for line in array:
            file.write(line + '\n')

def GetUsernameAndPassword(textFilePath):
    with open(textFilePath, "r") as file:
        username = ""
        password = ""
        for i, line in enumerate(file):
            if i == 0:
                username = line.strip()
            elif i == 1:
                password = line.strip()

        return username, password


# Change to desired driver path
DRIVER_PATH = "chromedriver.exe" # "/home/jazevedo/LinkedInScraper/chromedriver" # "C:\\Users\\jacob\\Downloads\\chromedriver_win32\\chromedriver.exe"


# Either change driver code, or create a file called "creds.txt" in the working directory
USERNAME, PASSWORD = GetUsernameAndPassword("creds.txt")
DATABASE_USERNAME, DATABASE_PASSWORD = GetUsernameAndPassword("dbcreds.txt")
DATABASE_NAME = "linkedin"
HOST = "10.33.113.250"
PORT = 3308
DATABASE = LinkedInDB(DATABASE_NAME, HOST, PORT, DATABASE_USERNAME, DATABASE_PASSWORD)

"""
LinkedInScraper

Description:
    Utilizes selenium and chrome driver to authentication the user session for LinkedIn access.
    Provides methods to extract relevant data from LinkedIn
"""

class LinkedInScraper:
    # Dev Note: 11/16/2021 WORKING
    # Initializes driver
    def __init__(self, username, password, driver_path, database: LinkedInDB):
        # Database connection and methods for inserting employee information
        self.database = database

        if self.database is None:
            return None
        else:
            self.__employeeURLsInDB__ = self.database.__loadEmployeeURLs__()

        # Stores the URL of each employee discovered in a LinkedIn query
        self.__employeeURLsToBeScraped__ = self.ExtractEmployeeURLsToBeScraped("employeeURLs.txt")

        # Contains the newly found employeeURLs
        self.newEmployeeURLs = []

        # Specifying options to help driver be more efficient
        chrome_options = webdriver.ChromeOptions()

        chrome_options.headless = True
        chrome_options.add_argument("--window-size=1920x1080")

        self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

        self.driver.get("https://linkedin.com/home")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#session_key"))).send_keys(username)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#session_password"))).send_keys(password)

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/main/section[1]/div/div/form/button"))).click()
        except TimeoutException:
            print("ERROR: Could not login properly")
            self.driver = None
            return None

        # Sometimes I am stopped for being a robot, this gives me time to prove I'm human
        # Otherwise, proceeds with program execution if element is found
        try:
            # Checking if login was successful
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#voyager-feed")))
        except TimeoutException:
            # Potentially Captcha or Pin required
            try:
                # Checking for pin prompt
                main = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "main")))

                try:
                    inputElement = main.find_element(By.NAME, "pin")

                    print("Enter pin:", end="")
                    pin = input()

                    inputElement.send_keys(pin)

                    submitButton = main.find_element(By.ID, "email-pin-submit-button")
                    submitButton.click()
                except NoSuchElementException:
                    pass


                # If prompt was successful, check for login success
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         "#voyager-feed")))
            except TimeoutException:
                print("ERROR: Captcha needed")
                return None

    def ExtractEmployeeURLsToBeScraped(self, pathToEmployeeURLsFile):
        employeeURLsToBeScraped = []

        employeeURLsInFile = ReadLinesFromFile(pathToEmployeeURLsFile)

        # Make sure we don't extract the same profile twice
        for URL in employeeURLsInFile:
            if URL not in self.__employeeURLsInDB__:
                employeeURLsToBeScraped.append(URL)

        # Rewrite text file to only contain "non-extracted" profiles
        WriteLinesToFile(pathToEmployeeURLsFile, employeeURLsToBeScraped)

        return employeeURLsToBeScraped

    """
    LinkedInScraper::AddEmployeeURLsFromSearchPage

    Description:
        Adds all unique employee URLs to the employeeURLs set
    """
    def AddEmployeeURLsFromSearchPage(self):
        main = None
        tries = 0

        self.driver.execute_script("window.scrollTo(0, 2000)")

        refresh = False
        maxTries = 3
        while main is None and tries < maxTries:
            try:
                tries += 1
                main = self.driver.find_element(By.TAG_NAME, "main")
            except NoSuchElementException:
                if tries == 1:
                    print()
                print(f"Retrying... {maxTries - tries} more times")

            # Sometimes the pages don't load properly. Refresh and try to get page one last time
            if tries == maxTries and main is None and refresh is False:
                print("Refreshing...")
                self.driver.refresh()
                self.driver.execute_script("window.scrollTo(0, 2000)")
                tries = 0
                refresh = True

        if main is None:
            return False

        if tries > 1 or refresh is True:
            print("Parsing page:", end="")

        peopleDiv = main.find_element(By.TAG_NAME, "ul")
        peopleList = peopleDiv.find_elements(By.XPATH, "./li")
        previousLink = ""

        for i, element in enumerate(peopleList):
            # Can be no more than 10 results per page
            # Need to have better break criteria than this
            if i > 9:
                break
            XPathLocation = f"./div/div/div[2]/div[1]/div[1]/div/span[1]/span/a"
            try:
                link = element.find_element(By.XPATH, XPathLocation).get_attribute("href")

                # Checks if profile is accessible (Not "LinkedIn Member")
                if link[25:27] == "in":
                    # Format link to only include profile ID
                    endLinkPosition = 0
                    for i, char in enumerate(link):
                        if char == '?':
                            endLinkPosition = i

                    URL = link[:endLinkPosition]
                    if URL not in self.__employeeURLsToBeScraped__:
                        self.__employeeURLsToBeScraped__.append(URL)
                        self.newEmployeeURLs.append(URL)
                        previousLink = link
                # Otherwise, the link has no relevance
            except NoSuchElementException:
                print(f"Inspect element at {XPathLocation}")
                print("Previously Successful:", previousLink)
                return False

        return True


    """
    LinkedInScraper::LinkedInPeopleSearch

    Description:
        After authentication, converts the query into a format recognizable to LinkedIn 
        and passes the query into LinkedIn's search engine and calls the
        AddEmployeeURLsFromSearchPage to append to employeeURLs set

    Parameters:
        query - A string entered in how you would in the LinkedIn GUI. Converted into a URL query argument
    """

    def LinkedInPeopleSearch(self, query: str, outputFilePath: str):
        print("Query:", query)
        # Convert query string to a URLQuery
        queryArr = query.split(' ')
        URLQuery = ''

        for i, searchTerm in enumerate(queryArr):
            searchTerm = searchTerm.replace('&', '%26')
            if i == 0:
                URLQuery = searchTerm
            else:
                # LinkedIn Separates Search Terms by %20 instead of whitespace
                URLQuery += ('%20' + searchTerm)

        # Navigate to webpage
        self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={URLQuery}")

        # JS Elements were not rendering without scrolling
        self.driver.execute_script("window.scrollTo(0, 2000)")

        pageButtonCount = None

        main = None
        try:
            main = self.driver.find_element(By.TAG_NAME, "main")
        except NoSuchElementException:
            print("Could not find main")
            return False

        try:
            if main.find_element(By.XPATH, "./div/div/div/section/h2").text == "No results found":
                # Remove query from file
                return True
        except NoSuchElementException:
            pass

        try:
            pageButtonCount = main.find_element(By.XPATH,
                    "./div/div/div[4]/div/div/ul/li[last()]/button/span")
        except NoSuchElementException:
            print("Element not found, trying new location")

        if pageButtonCount is None:
            try:
                pageButtonCount = main.find_element(By.XPATH,
                    "./div/div/div[5]/div/div/ul/li[last()]/button/span")
            except NoSuchElementException:
                print("Element not found, trying new location")

        if pageButtonCount is None:
            # For whatever reason, sometimes the element is located at this xpath
            try:
                pageButtonCount = main.find_element(By.XPATH,
                    "./div/div/div[4]/div/div/ul/li[last()]/button/span")
            except NoSuchElementException:
                print("Element not found, trying new location")

        if pageButtonCount is None:
            try:
                pageButtonCount = self.driver.find_element( By.XPATH,
                    "/html/body/div[5]/div[3]/div/div[2]/div/div[1]/main/div/div/div[5]/div/div/ul/li[10]/button/span")
            except NoSuchElementException:
                print("Element not found, defaulting to 0")

        if pageButtonCount is not None:
            maxPageCount = int(pageButtonCount.text)
        else:
            maxPageCount = 0

        print("Number of pages to parse:", maxPageCount)
        for page in range(1, maxPageCount + 1):
            if page == 1:
                print("Parsing page:", page, end="")
            else:
                if page % 10 == 0:
                    print("\nParsing page:", page, end="")
                else:
                    print("", page, end="")

            self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={URLQuery}&page={str(page)}")
            success = self.AddEmployeeURLsFromSearchPage()

            if not success:
                print("ERROR: Adding Employee URLs From Search Page was not successful")
                return False

        print("\nSuccessfully extracted all profiles for:", query, "\n")
        print("Appending ->", len(self.newEmployeeURLs), "new URLs to employee URL file")
        AppendLinesToFile(outputFilePath, self.newEmployeeURLs)
        # Reset to nothing
        self.newEmployeeURLs = []
        print()
        return True

    def ExtractEmployeeExperiences(self, employeeURL):
        print("Extracting experience from: ", employeeURL, sep="")

        experiences = []
        # profileurl/details/experience
        self.driver.get(employeeURL+"/details/experience")
        # All information contained within <main>
        expSection = None
        try:
            expSection = self.driver.find_element(By.TAG_NAME, "main")
        except NoSuchElementException:
            return None
        # From main: div[2]/div/div/ul

        '''
        # If experience can be expanded, click the button
        try:
            # Expand experiences
            expButtons = expSection.find_elements_by_tag_name("button")

            for expButton in expButtons:
                expButton.click()
        except NoSuchElementException:
            pass
        '''

        # Extracting Top-level <li> tags from Experience Section
        expList = None

        ul = None
        try:
            ul = WebDriverWait(expSection, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "./section/div[2]/div/div[1]/ul")))

            # print()
            # print("==================== UL ====================")
            # print(ul.text)
            # print()

            try:
                # Assuming the workers can have no more than 100 jobs
                expList = ul.find_elements(By.XPATH, "./li")
            except NoSuchElementException:
                pass

        except TimeoutException:
            print("ERROR: Could not find experience list (1)")
            return None

        for i, exp in enumerate(expList):
            # print()
            # print("==================== NEW EXP ====================")
            # print(expList[i].text)
            # print()

            # Check for type
            expSublist = None
            try:
                # This can trigger for elements with descriptions
                # (Single elements store their descriptions at the same location)
                ul = WebDriverWait(expList[i], 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ul")))
                ul2 = WebDriverWait(ul, 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ul")))

                try:
                    # Test to see if subList
                    pointForSubExp = ul2.find_element(By.XPATH, "./li[1]/span")
                    expSublist = ul2.find_elements(By.XPATH, "./li")
                except NoSuchElementException:
                    pass
            except TimeoutException:
                pass

            # List of Elements
            if expSublist:
                company = ""
                try:
                    company = exp.find_element(By.XPATH, "./div/div[2]/div[1]/a/div/span/span[1]").text
                except NoSuchElementException:
                    print("ERROR: Could not find company [1]")
                    print("Element that caused the error:")
                    print(exp.text)
                    return None

                jobType = ""
                # If this field is found, it applies to all subExp elements
                try:
                    # Comes in the format <Full-time · 7 mos>
                    jobType = exp.find_element(By.XPATH, "./div/div[2]/div[1]/a/span[1]/span[1]").text.split()[0]
                except NoSuchElementException:
                    pass

                location = ""
                try:
                    location = exp.find_element(By.XPATH, "./div/div[2]/div[1]/a/span[2]/span[1]").text
                except NoSuchElementException:
                    pass

                for subExp in expSublist:
                    experience = Experience()

                    experience.company_name = company
                    # Position
                    try:
                        experience.position = subExp.find_element(By.XPATH,
                            "./div/div[2]/div/a/div/span/span[1]").text

                    except NoSuchElementException:
                        print("ERROR: Could not find position [1]")
                        return None

                    # Type (Optional)
                    if jobType != "":
                        experience.employment_type = jobType
                    else:
                        try:
                            experience.employment_type = subExp.find_element(By.XPATH,
                                "./div/div/div[1]/ul/li[1]/div/div[2]/div/a/span[1]").text
                        except NoSuchElementException:
                            pass

                    if location != "":
                        experience.location = location
                    else:
                        # Location (Optional)
                        try:
                            experience.location = subExp.find_element(By.XPATH,
                                "./div/div[2]/div/a/span[3]/span[1]").text
                        except NoSuchElementException:
                            pass

                    # Dates
                    try:
                        dates = ""
                        try:
                            dates = subExp.find_element(By.XPATH,
                                "./div/div[2]/div/a/span/span[1]").text
                        except NoSuchElementException:
                            pass
                        if "mos" not in dates and "yrs" not in dates and "yr" not in dates and "mo" not in dates:
                            try:
                                dates = subExp.find_element(By.XPATH,
                                                            "./div/div[2]/div[1]/a/span[2]/span[1]").text
                            except NoSuchElementException:
                                pass
                        if "mos" not in dates and "yrs" not in dates and "yr" not in dates and "mo" not in dates:
                            try:
                                dates = subExp.find_element(By.XPATH,
                                                            "./div/div[2]/div[1]/a/span[1]/span[1]").text
                            except NoSuchElementException:
                                pass
                        if "mos" not in dates and "yrs" not in dates and "yr" not in dates and "mo" not in dates:
                            print("ERROR: Could not find valid date")
                            print("Here is the experience element that caused the problem:")
                            print(experience.position + " at " + experience.company_name)
                            return None
                        # Nov 2021 - Present · 2 mos
                        skipEnd = False
                        try:
                            dashInd = dates.rindex("-")
                            experience.start_date = dates[:dashInd].strip()
                        except:
                            # Date didn't have a dash because it is only a single value
                            experience.start_date = dates.split("·")[0].strip()
                            experience.end_date = None
                            skipEnd = True

                        if not skipEnd:
                            try:
                                dotInd = dates.rindex('·')
                                experience.end_date = dates[dashInd + 2:dotInd].strip()
                            except ValueError:
                                experience.end_date = dates[dashInd + 2:].strip()
                    except NoSuchElementException:
                        print("ERROR: Could not find date")
                        return None

                    experience.description = None
                    experience.media = None

                    experiences.append(experience)

            # Single Element
            else:
                experience = Experience()

                # Position
                try:
                    experience.position = exp.find_element(By.XPATH, "./div/div[2]/div/div[1]/div/span/span[1]").text
                except NoSuchElementException:
                    print("ERROR: Could not find position [2]")
                    print("Element that caused error:")
                    print(exp.text)
                    return None

                # Company and Type
                try:
                    companyAndType = exp.find_element(By.XPATH, "./div/div[2]/div/div[1]/span[1]/span[1]").text

                    try:
                        dotInd = companyAndType.rindex('·')
                        experience.company_name = companyAndType[:dotInd].strip()
                        experience.employment_type = companyAndType[dotInd + 1:].strip()
                    except ValueError:
                        experience.company_name = companyAndType

                except NoSuchElementException:
                    print("ERROR: Could not find company [3]")
                    return None

                # Location (Optional)
                try:
                    experience.location = exp.find_element(By.XPATH, "./div/div[2]/div/div[1]/span[3]/span[1]").text
                except NoSuchElementException:
                    pass

                # Dates
                try:
                    # Flag if this date does not contain a -
                    noEnd = False
                    dates = exp.find_element(By.XPATH, "./div/div[2]/div/div[1]/span[2]/span[1]").text

                    try:
                        #In case the end of the date is included by accident
                        dotInd = dates.rindex("·")
                        dates = dates[:dotInd].strip()
                    except ValueError:
                        pass

                    # Nov 2021 - Present · 2 mos
                    try:
                        dashInd = dates.rindex("-")
                    except ValueError:
                        noEnd = True
                        spaces = 0
                        for i, char in enumerate(dates):
                            if char == ' ':
                                spaces += 1
                            if spaces == 2:
                                dashInd = i
                                break

                    experience.start_date = dates[:dashInd].strip()

                    if noEnd == False:
                        try:
                            dotInd = dates.rindex('·')
                            experience.end_date = dates[dashInd + 2:dotInd].strip()
                        except ValueError:
                            experience.end_date = dates[dashInd + 2:].strip()
                    else:
                        experience.end_date = None
                except NoSuchElementException:
                    pass

                # Description (Optional)
                try:
                    experience.description = exp.find_element(By.XPATH, "./div/div[2]/div[2]/ul/li/div/ul/li/div/div/div/span[1]").text
                except NoSuchElementException:
                    pass

                experience.media = None

                experiences.append(experience)

        return experiences

    def ExtractEmployeeEducation(self, employeeURL):
        print("Extracting education from:", employeeURL)
        education = []
        self.driver.get(employeeURL + "/details/education")

        main = None
        try:
            main = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "main")))
        except TimeoutException:
            print("Could not find main")
            return None

        educationUL = None
        try:
            educationUL = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "ul")))
        except TimeoutException:
            print("Could not find education list <ul>")
            return None

        educationList = None
        try:
            educationList = educationUL.find_elements(By.XPATH, "./li")
        except NoSuchElementException:
            print("Could not find education list")
            educationList = []

        for educationElem in educationList:
            edu = Education()
            try:
                degreeLine = educationElem.find_element(By.XPATH, "./div/div[2]/div[1]/a/span[1]/span[1]").text
                degreeArr = degreeLine.split(", ")
                edu.degree = degreeArr[0]
                edu.degree_type = degreeArr[-1]
            except:
                print("Could not find degree information")
                edu.degree = ""
                edu.degree_type = ""

            try:
                edu.institution = educationElem.find_element(By.XPATH, "./div/div[2]/div[1]/a/div/span/span[1]").text
            except NoSuchElementException:
                pass

            descList = None
            try:
                ul = educationElem.find_element(By.TAG_NAME, "ul")
                descList = ul.find_elements(By.XPATH, "./child::*")
            except NoSuchElementException:
                print("Could not find description list")
                descList = []

            for elem in descList:
                string = elem.text
                grade = "Grade:"
                pos = string.find(grade)
                if pos != -1:
                    # For eliminating duplicates (some fields are stored twice in the HTML, sometimes hidden)
                    start = pos + 1 + len(grade)
                    pos2 = string[start:].find(grade)
                    if pos2 != 1:
                        edu.GPA = string[start:start + pos2].strip()
                    else:
                        edu.GPA = string[start:].strip()
                    continue

                activities = "Activities and societies:"
                pos = string.find(activities)
                if pos != -1:
                    start = pos + 1 + len(activities)
                    pos2 = string[start:].find(activities)
                    if pos2 != -1:
                        edu.activities = string[start: start + pos2].strip()
                    else:
                        edu.activities = string[start:].strip()
                    continue

                # May require additional logic if repeated
                try:
                    edu.description = elem.find_element(By.XPATH, "./div/ul/li/div/div/div/span[1]").text
                except NoSuchElementException:
                    edu.description = ""

            edu.media = None

            try:
                dates = educationElem.find_element(By.XPATH, "./div/div[2]/div[1]/a/span[2]/span[1]").text
                dateArr = dates.split(" - ")
                edu.start_date = dateArr[0]
                edu.end_date = dateArr[-1]
            except NoSuchElementException:
                edu.start_date = ""
                edu.end_date = ""

            education.append(edu)

        return education

    def ExtractEmployeeSkills(self, employeeURL):
        print("Extracting skills from:", employeeURL)
        skills = {}
        # Navigate to skills webpage
        self.driver.get(employeeURL + "/details/skills")

        time.sleep(10)

        main = None
        try:
            main = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.TAG_NAME,
                     "main")))
        except TimeoutException:
            print("Could not find main")
            return None

        #self.driver.get_screenshot_as_file('screenshot.png')

        buttonParent = None
        try:
            buttonParent = WebDriverWait(main, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH,
                     "./section/div[2]/div[1]")))
        except TimeoutException:
            print("Could not find buttons [1]")
            return {}

        buttons = None
        try:
            buttons = buttonParent.find_elements(By.XPATH, "./button")
        except NoSuchElementException:
            print("Could not find buttons [2]")
            return None

        # Iterate through skills categories (skip first "All" button if more than one button)
        if len(buttons) > 1:
            buttons = buttons[1:]

        for i, button in enumerate(buttons):
            skillCategory = button.text
            skills[skillCategory] = []
            # Click the button
            button.click()
            categoryList = None
            try:
                categoryListParent = main.find_element(By.XPATH, f"./section/div[2]/div[{3 + i}]/div/div/div[1]/ul")
                categoryList = categoryListParent.find_elements(By.XPATH, "./li")
            except NoSuchElementException:
                print("Could not extract skill category list")

            # Iterate through individual skills within category
            for skillElem in categoryList:
                try:
                    skill = skillElem.find_element(By.XPATH, "./div/div[2]/div[1]/a/div/span[1]/span[1]").text
                    skills[skillCategory].append(skill)
                except NoSuchElementException:
                    # Skill may not have a link (<a> element)
                    try:
                        skill = skillElem.find_element(By.XPATH, "./div/div[2]/div[1]/div[1]/div/span/span[1]").text
                        skills[skillCategory].append(skill)
                    except NoSuchElementException:
                        print("ERROR: Skill within category not found")
                        return None

        return skills

    def ExtractEmployeeAccomplishments(self, employeeURL):
        pass

    # Dev Note: 12/29/2021 WORKING
    def ExtractProfileAttributes(self, employeeURL: str) -> Employee:
        # Navigate to web page
        self.driver.get(employeeURL)

        print("Extracting attributes from: ", employeeURL, sep="")

        # Contains all relevant profile attributes
        main = None
        try:
            main = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "main")))
        except TimeoutException:
            print("ERROR: Could not find <main>")
            return None

        # Initialize Employee Object
        currentEmployee = Employee()

        # Last split in employeeURL
        currentEmployee.user_url_id = employeeURL.split("/")[-1]

        try:
            nameElement = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, "./section[1]/div[2]/div[2]/div[1]/div[1]/h1")))

            if nameElement:
                currentEmployee.name = nameElement.text
        except TimeoutException:
            print("Could not find name")
            return None

        try:
            currentEmployee.location = main.find_element(By.XPATH, "./section[1]/div[2]/div[2]/div[2]/span[1]").text
        except NoSuchElementException:
            pass

        # Header
        try:
            currentEmployee.header = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "./section[1]/div[2]/div[2]/div[1]/div[2]"))).text
        except TimeoutException:
            pass

        try:
            currentEmployee.about = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "./div/div/div[5]/section/div"))).text

            if currentEmployee.about[-8: 0] == "see more":
                currentEmployee.about = currentEmployee.about[:-10]
        except TimeoutException:
            pass

        print("Successfully extracted base elements for", employeeURL)
        #currentEmployee.website = None
        currentEmployee.experience = self.ExtractEmployeeExperiences(employeeURL)  # List

        if currentEmployee.experience is None:
            return None
        currentEmployee.education = self.ExtractEmployeeEducation(employeeURL)  # List

        if currentEmployee.education is None:
            return None
        currentEmployee.skills = self.ExtractEmployeeSkills(employeeURL)  # Dict

        if currentEmployee.skills is None:
            return None

        return currentEmployee

    def waitForJStoLoad(self):
        # From Stack OF; To Do
        # See https://stackoverflow.com/questions/10720325/selenium-webdriver-wait-for-complex-page-with-javascript-to-load
        pass

'''
testEmployee = Employee()

testEmployee.user_url_id = "https://www.linkedin.com/in/jacobazevedojr/"
testEmployee.name = "Jacob Azevedo Jr."
testEmployee.location = "San Francisco Bay Area"
testEmployee.header = "This is a test header for Jacob Azevedo"
testEmployee.about = "This is a test about for Jacob Azevedo"
testEmployee.website = None

testEmployee.experience = []
testEmployee.experience.append(Experience())
testEmployee.experience[0].position = "Software Engineer"
testEmployee.experience[0].company_name = "Microsoft"
testEmployee.experience[0].employment_type = "Full-Time"
testEmployee.experience[0].location = "Seattle, WA"
testEmployee.experience[0].description = "This is a job description"
testEmployee.experience[0].media = None
testEmployee.experience[0].start_date = "May 2021"
testEmployee.experience[0].end_date = "Aug 2021"

testEmployee.education = []
testEmployee.education.append(Education())
testEmployee.education[0].degree = "Computer Science"
testEmployee.education[0].degree_type = "Bachelor of Science"
testEmployee.education[0].institution = "California State University, Long Beach"
testEmployee.education[0].GPA = "3.92"
testEmployee.education[0].activities = ""
testEmployee.education[0].description = ""
testEmployee.education[0].media = None
testEmployee.education[0].start_date = "2020"
testEmployee.education[0].end_date = "2022"

testEmployee.skills = {"Main": ["C++", "Python (Programming Language)", "Java"]}
'''