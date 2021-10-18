from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
import time
from typing import List

from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Change to desired driver path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

DRIVER_PATH = "C:\\Users\\jacob\\Desktop\\Senior Thesis\\chromedriver.exe"

# Either change driver code, or create a file called "creds.txt" in the working directory
def GetUsernameAndPassword(textFilePath):
    with open(textFilePath, "r") as file:
        username = ""
        password = ""
        for i, line in enumerate(file):
            if i == 0:
                username = line
            elif i == 1:
                password = line

        return username, password
    return None, None

USERNAME, PASSWORD = GetUsernameAndPassword("creds.txt")

class Experience:
    def __init__(self):
        self.position = None
        self.company_name = None
        self.employment_type = None
        self.location = None
        self.description = None
        self.media = None
        self.start_date = None
        self.end_date = None

    def __str__(self):
        date = ""
        if self.start_date and self.end_date is not None:
            date = self.start_date + " - " + self.end_date
        else:
            date = "ERROR"
        return f"     Position: {self.position} \n     Company Name: {self.company_name} \n     Employment Type: {self.employment_type} \n     Location: {self.location}\n     Dates: {date}\n     \n"

class Education:
    def __init__(self):
        self.degree = None
        self.degree_type = None
        self.institution = None
        self.GPA = None
        self.activities = None
        self.description = None
        self.media = None
        self.start_date = None
        self.end_date = None

    def __str__(self):
        date = "ERROR"
        if self.start_date and self.end_date is not None:
            date = self.start_date + " - " + self.end_date

        return f"     Degree: {self.degree}\n     Degree Type: {self.degree_type}\n     Institution: {self.institution}\n     GPA: {self.GPA}\n     Activities: {self.activities}\n     Dates: {dates}"

class Skill:
    def __init__(self):
        self.skill = None
        self.category = None
        self.endorsement_profile_urls = None # List


class Publication:
    def __init__(self):
        self.title = None
        self.publisher = None
        self.publication_date = None
        self.description = None
        self.author_names = None # List

class Patent:
    def __init__(self):
        self.patent_title = None
        self.patent_office = None
        self.patent_num = None
        self.status = None
        self.issue_date = None
        self.patent_url = None
        self.description = None
        self.inventor_names = None # List

class Course:
    def __init__(self):
        self.course_name = None
        self.course_num = None
        self.associated = None

class Project:
    def __init__(self):
        self.project_name = None
        self.start_date = None
        self.end_date = None
        self.associated = None
        self.project_url = None
        self.description = None
        self.creator_names = None # List

class Honor_And_Award:
    def __init__(self):
        self.title = None
        self.associated = None
        self.issuer = None
        self.issue_date = None
        self.description = None

class Test_Score:
    def __init__(self):
        self.title = None
        self.associated = None
        self.score = None
        self.issue_date = None
        self.description = None

class Language:
    def __init__(self):
        self.language = None
        self.proficiency = None

class Organization:
    def __init__(self):
        self.org_name = None
        self.position = None
        self.associated = None
        self.start_date = None
        self.end_date = None
        self.description = None

class Accomplishments:
    def __init__(self):
        self.publication = None # List
        self.patent = None # List
        self.course = None # List
        self.project = None # List
        self.honor_and_award = None # List
        self.test_score = None # List
        self.language = None # List
        self.organization = None # List

class Employee:
    def __init__(self):
        self.experience = None # List
        self.education = None # List
        self.skills = None # List
        self.accomplishments = None # List

        self.user_url_id = None
        self.name = None
        self.location = None
        self.header = None
        self.about = None
        self.website = None

    def __str__(self):
        exp = ""
        for x in self.experience:
            exp += (str(x) + '\n')

        edu = ""
        for x in self.education:
            edu + (str(x) + '\n')

        skil = ""
        for x in self.skills:
            skil + (str(x) + '\n')

        acom = ""
        for x in self.accomplishments:
            acom + (str(x) + '\n')

        print("Length of Exp Vector:", len(self.experience))

        return f"Name: {self.name} \nHeader: {self.header} \nLocation: {self.location} \nAbout: {self.about} \n\nExperience: \n{exp} \n\nEducation: \n{edu}\n\nSkills: \n{skil}\n\nAccomplishments: {acom}"

"""
LinkedInScraper

Description:
    Utilizes selenium and chrome driver to authentication the user session for LinkedIn access.
    Provides methods to extract relevant data from LinkedIn
"""
class LinkedInScraper:
    # Initializes driver
    def __init__(self, username, password, driver_path):
        # Stores the URL of each employee discovered in a LinkedIn query
        self.employeeURLs = set()
        # self.employeeURLs = LoadEmployeeURLs() should access DB and reload the dictionary of employeeURLs (so new searches don't duplicate)

        # Specifying options to help driver be more efficient
        chrome_options = webdriver.ChromeOptions()

        # chrome_options.headless = True
        # chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)

        self.driver.get("https://linkedin.com/home")

        login = self.driver.find_element_by_xpath("/html/body/main/section[1]/div[2]/form/div[2]/div[1]/input").send_keys(USERNAME)
        password = self.driver.find_element_by_xpath("/html/body/main/section[1]/div[2]/form/div[2]/div[2]/input").send_keys(PASSWORD)
        submit = self.driver.find_element_by_xpath("/html/body/main/section[1]/div[2]/form/button").click()

        # Sometimes I am stopped for being a robot, this gives me time to prove I'm human
        time.sleep(10)

        # Login Validation
        # try:
        #     time.sleep(1)
        #     account_button = self.driver.find_element_by_id("ember32")
        #     print("Successful Login")
        # except NoSuchElementException:
        #     print("Login Unsuccessful")
        #     self.driver = None

    """
    LinkedInScraper::AddEmployeeURLsFromSearchPage
    
    Description:
        Adds all unique employee URLs to the employeeURLs set
    """
    def AddEmployeeURLsFromSearchPage(self):
        main = None
        tries = 0

        while(main is None and tries < 5):
            try:
                tries += 1
                main = self.driver.find_element_by_tag_name("main")
            except:
                print(f"Couldn't find element, retrying... {5 - tries} more times")

        peopleDiv = main.find_element_by_xpath("./div/div/div[2]")
        peopleList = peopleDiv.find_elements_by_tag_name("li")
        for i, element in enumerate(peopleList):
            # Can be no more than 10 results per page
            # Need to have better break criteria than this
            if i > 9:
                break
            print(peopleList[i].text)
            XPathLocation = f"./div/div/div[2]/div[1]/div[1]/div/span[1]/span/a[@href]"
            try:
                link = element.find_element_by_xpath(XPathLocation).get_attribute("href")
                print(link)

                # Checks if profile is accessible (Not "LinkedIn Member")
                print("Link Check:", link[25:27])
                if link[25:27] == "in":
                    # Format link to only include profile ID
                    endLinkPosition = 0
                    for i, char in enumerate(link):
                        if char == '?':
                            endLinkPosition = i

                    self.employeeURLs.add(link[:endLinkPosition])
                # Otherwise, the link has no relevance
            except NoSuchElementException:
                print(f"Inspect element at {XPathLocation}")
                time.sleep(5)

            print("*****************************************")

    """
    LinkedInScraper::LinkedInPeopleSearch
    
    Description:
        After authentication, converts the query into a format recognizable to LinkedIn 
        and passes the query into LinkedIn's search engine and calls the
        AddEmployeeURLsFromSearchPage to append to employeeURLs set
        
    Parameters:
        query - A string entered in how you would in the LinkedIn GUI. Converted into a URL query argument
    """
    def LinkedInPeopleSearch(self, query: str):
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
        time.sleep(10)

        pageButtonCount = None

        try:
            main = self.driver.find_element_by_tag_name("main")
            div1 = main.find_element_by_tag_name("div")
            div2 = div1.find_element_by_tag_name("div")
            div3 = div2.find_elements_by_tag_name("div")
            div4 = div3[4].find_element_by_tag_name("div")
            div5 = div4.find_element_by_tag_name("div")
            ul = div5.find_element_by_tag_name("ul")
            list = ul.find_elements_by_tag_name("li")
            span = list[-1].find_elements_by_tag_name("span")
            pageButtonCount = span
        except NoSuchElementException:
            print("Element not found, trying new location")

        try:
            pageButtonCount = self.driver.find_element_by_xpath("/html/body/div[6]/div[3]/div/div[2]/div/div[1]/main/div/div/div[5]/div/div/ul/li[last()]/button/span")
        except NoSuchElementException:
            print("Element not found, trying new location")

        # For whatever reason, sometimes the element is located at this xpath
        try:
            pageButtonCount = self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div[2]/div/div[1]/main/div/div/div[4]/div/div/ul/li[last()]/button/span")
        except NoSuchElementException:
            print("Element not found, trying new location")

        try:
            pageButtonCount = self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div[2]/div/div[1]/main/div/div/div[5]/div/div/ul/li[10]/button/span")
        except NoSuchElementException:
            print("Element not found, defaulting to 0")

        # In this case (is None), there are either no pages or less than 10 pages which changes the format of the list
        maxPageCount = 0
        if pageButtonCount is not None:
            maxPageCount = int(pageButtonCount.text)

        for page in range(maxPageCount):
            self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={URLQuery}&page={str(page)}")
            self.AddEmployeeURLsFromSearchPage()

        print("Done")

        for URL in self.employeeURLs:
            print("Link:", URL)

    def ExtractEmployeeExperiences(self, main) -> List[Experience]:
        experiences = []

        expSection = None

        print("Starting Exp Extraction...")
        try:
            expSection = WebDriverWait(main, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#experience-section")))
        except TimeoutException:
            print("Could not find experience section")

        if expSection is None:
            return None

        # print()
        # print("==================== EXP SECTION ====================")
        # print(expSection.text)
        # print()

        print("Exp Expansion (Opt)...")
        # If experience can be expanded, click the button
        try:
            # Expand experiences
            expButtons = expSection.find_elements_by_tag_name("button")

            for expButton in expButtons:
                expButton.click()
        except NoSuchElementException:
            print("Could not find button to expand experience")

        print("Extracting <li> tags...")
        # Extracting Top-level <li> tags from Experience Section
        expList = None

        ul = None
        try:
            ul = WebDriverWait(expSection, 5).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "ul")))

            # print()
            # print("==================== UL ====================")
            # print(ul.text)
            # print()

            try:
                # Assuming the workers can have no more than 100 jobs
                expList = ul.find_elements_by_xpath("./li")
            except NoSuchElementException:
                print("Could not find list element")

        except TimeoutException:
            print("Could not find experience list (1)")
            return None

        print("Iterating through Experience List...")
        for i, exp in enumerate(expList):
            print()
            # print()
            # print("==================== NEW EXP ====================")
            # print(expList[i].text)
            # print()

            # Check for type
            expSublist = None
            try:
                ul = WebDriverWait(expList[i], 5).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ul")))

                try:
                    expSublist = ul.find_elements_by_tag_name("li")
                except NoSuchElementException:
                    print("ERROR: Could not extract elements from experience sublist")
                    return None
            except TimeoutException:
                print("Could not find experience sublist")

            # List of Elements
            if expSublist:
                company = ""
                try:
                    company = exp.find_element_by_xpath("./section/div/a/div/div[2]/h3/span[2]").text
                except:
                    print("ERROR: Could not find company")
                    return None

                for subExp in expSublist:
                    experience = Experience()

                    experience.company_name = company
                    # Position
                    try:
                        experience.position = subExp.find_element_by_xpath("./div/div/div/div/div/div/h3/span[2]").text
                    except NoSuchElementException:
                        print("ERROR: Could not find position")
                        return None

                    # Type
                    try:
                        experience.employment_type = subExp.find_element_by_xpath("./div/div/div/div/div/div/h4[1]").text
                    except NoSuchElementException:
                        print("ERROR: Could not find company")
                        return None

                    # Location (Optional)
                    try:
                        experience.location = subExp.find_element_by_xpath("./div/div/div/div/div/div/h4[2]/span[2]").text
                    except NoSuchElementException:
                        print("Could not find location")

                    # Dates
                    try:
                        dates = subExp.find_element_by_xpath("./div/div/div/div/div/div/div/h4[1]/span[2]").text.split('–')
                        experience.start_date = dates[0].strip()
                        experience.end_date = dates[-1].strip()
                    except NoSuchElementException:
                        print("Could not find location")

                    experience.description = None
                    experience.media = None

                    experiences.append(experience)

            # Single Element
            else:
                experience = Experience()

                # div[2] starting point
                div = None
                try:
                    div = WebDriverWait(expList[i], 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "./section/div/div/a/div[2]")))

                except TimeoutException:
                    print("Could not find experience sublist")

                # Position
                try:
                    experience.position = div.find_element_by_tag_name("h3").text
                except NoSuchElementException:
                    print("ERROR: Could not find position")
                    return None

                # Company and Type
                try:
                    p = div.find_element_by_xpath("./p[2]")

                    span = None
                    try:
                        span = p.find_element_by_tag_name("span")
                    except NoSuchElementException:
                        print("Cannot find job type")

                    companyAndType = p.text
                    if span:
                        spaceInd = companyAndType.rindex(' ')
                        experience.company_name = companyAndType[:spaceInd]
                        experience.employment_type = companyAndType[spaceInd + 1:]
                    else:
                        experience.company_name = companyAndType

                except NoSuchElementException:
                    print("ERROR: Could not find company")
                    return None

                # Location (Optional)
                try:
                    experience.location = div.find_element_by_xpath("./h4/span[2]").text
                except NoSuchElementException:
                    print("Could not find location")

                # Dates
                try:
                    dates = div.find_element_by_xpath("./div/h4[1]/span[2]").text.split('–')
                    experience.start_date = dates[0].strip()
                    experience.end_date = dates[-1].strip()
                except NoSuchElementException:
                    print("Could not find location")

                # Description (Optional)
                try:
                    experience.description = expList[i].find_element_by_xpath("./section/div/div/div/div").text
                except NoSuchElementException:
                    print("Could not find location")

                experience.media = None

                experiences.append(experience)

        print()
        for e in experiences:
            print(str(e))
        return experiences

    def ExtractEmployeeEducation(self):
        education = []

        edList = None
        try:
            edList = self.driver.find_elements_by_xpath(
                "/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[6]/span/div/section/div[2]/section/ul/li")
        except NoSuchElementException:
            pass

        if edList is not None:
            for i, eduElem in enumerate(edList):
                print("i + 1 =", i + 1)
                edu = Education()

                if len(edList) == 1:
                    edu.degree = self.driver.find_element_by_xpath(
                        f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[6]/span/div/section/div[2]/section/ul/li/div/div/a/div[2]/div/p[1]/span[2]").text
                    edu.degree_type = self.driver.find_element_by_xpath(
                        f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[6]/span/div/section/div[2]/section/ul/li/div/div/a/div[2]/div/p[2]/span[2]").text
                    edu.institution = self.driver.find_element_by_xpath(
                        f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[6]/span/div/section/div[2]/section/ul/li/div/div/a/div[2]/div/h3").text

                    try:
                        edu.GPA = self.driver.find_element_by_xpath(
                            f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[6]/span/div/section/div[2]/section/ul/li/div/div/a/div[2]/div/p[3]/span[2]").text
                    except NoSuchElementException:
                        pass

                    try:
                        edu.activities = self.driver.find_element_by_css_selector(f"span.activities-societies").text
                    except NoSuchElementException:
                        pass

                    edu.description = None
                    edu.media = None

                    dateElem = ""
                    try:
                        dateElem = self.driver.find_element_by_xpath(
                            f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li/div/div/a/div[2]/p[1]/span[2]").text
                    except NoSuchElementException:
                        pass
                else:
                    edu.degree = self.driver.find_element_by_xpath(f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li[{i + 1}]/div/div/a/div[2]/div/p[2]/span[2]").text
                    edu.degree_type = self.driver.find_element_by_xpath(f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li[{i + 1}]/div/div/a/div[2]/div/p[1]/span[2]").text
                    edu.institution = self.driver.find_element_by_xpath(f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li[{i + 1}]/div/div/a/div[2]/div/h3").text
                    edu.GPA = self.driver.find_element_by_xpath(f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li[{i + 1}]/div/div/a/div[2]/div/p[3]/span[2]").text
                    edu.activities = self.driver.find_element_by_css_selector(f"span.activities-societies").text
                    edu.description = None
                    edu.media = None

                    dateElem = self.driver.find_element_by_xpath(f"/html/body/div[6]/div[3]/div/div/div/div/div[3]/div/div/main/div/div/div[5]/span/div/section/div[2]/section/ul/li[{i + 1}]/div/div/a/div[2]/p[1]/span[2]").text

                dates = dateElem.split('–')
                edu.start_date = dates[0].strip()
                edu.end_date = dates[-1].strip()

                education.append(edu)

        return education

    def ExtractEmployeeSkills(self):
        return None

    def ExtractEmployeeAccomplishments(self):
        return None

    def ExtractProfileAttributes(self, employeeURL: str) -> Employee:
        # Navigate to web page
        self.driver.get(employeeURL)

        # Contains all relevant profile attributes
        main = None

        try:
            main = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "main")))
        except TimeoutException:
            print("Could not find <main>")

        # If main cannot be found, no profile elements can be extracted
        if main is None:
            return None

        # Initialize Employee Object
        currentEmployee = Employee()

        # Last split in employeeURL
        currentEmployee.user_url_id = employeeURL.split("/")[-1]

        try:
            nameElement = WebDriverWait(main, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div/section/div[2]/div[2]/div[1]/div[1]/h1")))

            if nameElement:
                currentEmployee.name = nameElement.text
        except TimeoutException:
            print("Could not find name")


        try:
            currentEmployee.location = main.find_element_by_xpath("//div/section/div[2]/div[2]/div[2]/span[1]").text
        except NoSuchElementException:
            print("Couldn't extract employee location")

        # Header
        try:
            currentEmployee.header = WebDriverWait(main, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div/section/div[2]/div[2]/div[1]/div[2]"))).text
        except TimeoutException:
            print("Cannot find header")

        try:
            currentEmployee.about = WebDriverWait(main, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div/div/div[5]/section/div"))).text

            if currentEmployee.about[-8: 0] == "see more":
                currentEmployee.about = currentEmployee.about[:-10]
        except TimeoutException:
            print("Cannot find about")

        currentEmployee.website = None

        currentEmployee.experience = self.ExtractEmployeeExperiences(main) # List
        #currentEmployee.education = self.ExtractEmployeeEducation() # List
        print("----------------------------------------------------")
        currentEmployee.skills = self.ExtractEmployeeSkills() # List
        currentEmployee.accomplishments = self.ExtractEmployeeAccomplishments() # List

        return currentEmployee

# Driver Code
if (USERNAME and PASSWORD != ""):
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH)
    #driver.LinkedInPeopleSearch("Microsoft")
    URL = "https://www.linkedin.com/in/josh-braida-358a5476/"
    emp = driver.ExtractProfileAttributes(URL)
