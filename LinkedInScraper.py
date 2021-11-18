from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import time
from typing import List, Set

from LinkedInDBAccess import InsertToLinkedInDB

# Change to desired driver path
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


USERNAME, PASSWORD = GetUsernameAndPassword("creds.txt")
DATABASE_USERNAME, DATABASE_PASSWORD = GetUsernameAndPassword("dbcreds.txt")


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
        return f"     Position: {self.position}\n     Company Name: {self.company_name}\n     Employment Type: {self.employment_type}\n     Location: {self.location}\n     Dates: {date}\n"


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

        return f"     Degree: {self.degree}\n     Degree Type: {self.degree_type}\n     Institution: {self.institution}\n     GPA: {self.GPA}\n     Activities: {self.activities}\n     Dates: {date}"

    def __toDict__(self):
        return {'degree': self.degree, 'degree_type': self.degree_type, 'institution': self.institution, 'GPA': self.GPA, 'activities': self.activities, 'description': self.description, 'start_date': self.start_date, 'end_date': self.end_date}


class Skill:
    def __init__(self):
        self.skill = None
        self.endorsement_profile_urls = None  # List

    def __str__(self):
        return f"          Skill: {self.skill}\n"


class Publication:
    def __init__(self):
        self.title = None
        self.publisher = None
        self.publication_date = None
        self.description = None
        self.author_names = None  # List


class Patent:
    def __init__(self):
        self.patent_title = None
        self.patent_office = None
        self.patent_num = None
        self.status = None
        self.issue_date = None
        self.patent_url = None
        self.description = None
        self.inventor_names = None  # List


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
        self.creator_names = None  # List


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
        self.skills = None # Dict
        self.accomplishments = None # List

        self.user_url_id = None
        self.name = None
        self.location = None
        self.header = None
        self.about = None
        self.website = None

    def __str__(self):

        exp = ""
        skill = ""
        edu = ""
        acom = ""

        if self.experience:
            for x in self.experience:
                exp += (str(x) + '\n')

        if self.education:
            for x in self.education:
                edu += (str(x) + '\n')

        if self.skills:
            for key in self.skills:
                skill += ("     " + key + '\n')
                for skl in self.skills[key]:
                    skill += (str(skl) + '\n')

        if self.accomplishments:
            for x in self.accomplishments:
                acom += (str(x) + '\n')

        return f"Name: {self.name}\nHeader: {self.header}\nLocation: {self.location}\nAbout:\n     {self.about}\nExperience:\n{exp}Education:\n{edu}\nSkills:\n{skill}Accomplishments:\n{acom}"

    def __toDict__(self):
        empDict = {}
        # Value is a dictionary of attribute values
        empDict['employee'] = {'user_url': self.user_url_id, 'user_name': self.name, 'location': self.location, 'header': self.header, 'about': self.about}
        # Value is a list of dictionaries of attribute values
        empDict['education'] = [x.__toDict__ for x in self.education]
        # Value is a dictionary of category-skill List pairs
        empDict['skills'] = self.skills
        # Value is a dictionary of category-accomplishment List pairs
        empDict['accomplishments'] = self.accomplishments

"""
LinkedInScraper

Description:
    Utilizes selenium and chrome driver to authentication the user session for LinkedIn access.
    Provides methods to extract relevant data from LinkedIn
"""
class LinkedInScraper:
    # Initializes driver
    def __init__(self, username, password, driver_path, database):
        # Database connection and methods for inserting employee information
        self.database = database

        # Stores the URL of each employee discovered in a LinkedIn query
        self.employeeURLs = self.__LoadEmployeeURLs__()

        # Specifying options to help driver be more efficient
        chrome_options = webdriver.ChromeOptions()

        #chrome_options.headless = True
        #chrome_options.add_argument("--window-size=1920x1080")

        self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)

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
            return

        # Sometimes I am stopped for being a robot, this gives me time to prove I'm human
        # Otherwise, proceeds with program execution if element is found
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#voyager-feed")))
        except TimeoutException:
            print("ERROR: Captcha needed")

    """
    LinkedInScraper::__LoadEmployeeURLs__
    
    Description:
        Accesses the database and returns the set of employee profiles previously parsed
    """
    def __LoadEmployeeURLs__(self) -> Set:
        return set()

    """
    LinkedInScraper::AddEmployeeURLsFromSearchPage
    
    Description:
        Adds all unique employee URLs to the employeeURLs set
    """
    def AddEmployeeURLsFromSearchPage(self):
        main = None
        tries = 0

        while main is None and tries < 5:
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

        try:
            expSection = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#experience-section")))
        except TimeoutException:
            print("ERROR: Could not find experience section")

        if expSection is None:
            return [-1]

        # print()
        # print("==================== EXP SECTION ====================")
        # print(expSection.text)
        # print()

        # If experience can be expanded, click the button
        try:
            # Expand experiences
            expButtons = expSection.find_elements_by_tag_name("button")

            for expButton in expButtons:
                expButton.click()
        except NoSuchElementException:
            pass

        # Extracting Top-level <li> tags from Experience Section
        expList = None

        ul = None
        try:
            ul = WebDriverWait(expSection, 2).until(
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
                pass

        except TimeoutException:
            print("ERROR: Could not find experience list (1)")
            return [-1]

        for i, exp in enumerate(expList):
            # print()
            # print("==================== NEW EXP ====================")
            # print(expList[i].text)
            # print()

            # Check for type
            expSublist = None
            try:
                ul = WebDriverWait(expList[i], 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ul")))

                try:
                    expSublist = ul.find_elements_by_tag_name("li")
                except NoSuchElementException:
                    print("ERROR: Could not extract elements from experience sublist")
                    return [-1]
            except TimeoutException:
                pass

            # List of Elements
            if expSublist:
                company = ""
                try:
                    company = exp.find_element_by_xpath("./section/div/a/div/div[2]/h3/span[2]").text
                except:
                    print("ERROR: Could not find company")
                    return [-1]

                for subExp in expSublist:
                    experience = Experience()

                    experience.company_name = company
                    # Position
                    try:
                        experience.position = subExp.find_element_by_xpath("./div/div/div/div/div/div/h3/span[2]").text
                    except NoSuchElementException:
                        print("ERROR: Could not find position")
                        return [-1]

                    # Type
                    try:
                        experience.employment_type = subExp.find_element_by_xpath("./div/div/div/div/div/div/h4[1]").text
                    except NoSuchElementException:
                        print("ERROR: Could not find company")
                        return [-1]

                    # Location (Optional)
                    try:
                        experience.location = subExp.find_element_by_xpath("./div/div/div/div/div/div/h4[2]/span[2]").text
                    except NoSuchElementException:
                        pass

                    # Dates
                    try:
                        dates = subExp.find_element_by_xpath("./div/div/div/div/div/div/div/h4[1]/span[2]").text.split('–')
                        experience.start_date = dates[0].strip()
                        experience.end_date = dates[-1].strip()
                    except NoSuchElementException:
                        pass

                    experience.description = None
                    experience.media = None

                    experiences.append(experience)

            # Single Element
            else:
                experience = Experience()

                # div[2] starting point
                div = None
                try:
                    div = WebDriverWait(expList[i], 2).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "./section/div/div/a/div[2]")))

                except TimeoutException:
                    pass

                # Position
                try:
                    experience.position = div.find_element_by_tag_name("h3").text
                except NoSuchElementException:
                    print("ERROR: Could not find position")
                    return [-1]

                # Company and Type
                try:
                    p = div.find_element_by_xpath("./p[2]")

                    span = None
                    try:
                        span = p.find_element_by_tag_name("span")
                    except NoSuchElementException:
                        pass

                    companyAndType = p.text
                    if span:
                        spaceInd = companyAndType.rindex(' ')
                        experience.company_name = companyAndType[:spaceInd]
                        experience.employment_type = companyAndType[spaceInd + 1:]
                    else:
                        experience.company_name = companyAndType

                except NoSuchElementException:
                    print("ERROR: Could not find company")
                    return [-1]

                # Location (Optional)
                try:
                    experience.location = div.find_element_by_xpath("./h4/span[2]").text
                except NoSuchElementException:
                    pass

                # Dates
                try:
                    dates = div.find_element_by_xpath("./div/h4[1]/span[2]").text.split('–')
                    experience.start_date = dates[0].strip()
                    experience.end_date = dates[-1].strip()
                except NoSuchElementException:
                    pass

                # Description (Optional)
                try:
                    experience.description = expList[i].find_element_by_xpath("./section/div/div/div/div").text
                except NoSuchElementException:
                    pass

                experience.media = None

                experiences.append(experience)

        return experiences

    def ExtractEmployeeEducation(self, main):
        education = []

        eduSection = None

        try:
            eduSection = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "#education-section")))
        except TimeoutException:
            pass

        # If education can be expanded, click the button
        try:
            # Expand experiences
            eduButtons = eduSection.find_elements_by_tag_name("button")

            for expButton in eduButtons:
                expButton.click()
        except NoSuchElementException:
            pass

        # Extracting Top-level <li> tags from Education Section
        eduList = None

        ul = None
        try:
            ul = WebDriverWait(eduSection, 2).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "ul")))

            # print()
            # print("==================== UL ====================")
            # print(ul.text)
            # print()

            try:
                # Assuming the workers can have no more than 100 jobs
                eduList = ul.find_elements_by_xpath("./li")
            except NoSuchElementException:
                pass

        except TimeoutException:
            print("ERROR: Could not find education list (1)")
            return None

        for edu in eduList:
            # Check for type
            eduSublist = None
            try:
                ul = WebDriverWait(edu, 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ul")))

                try:
                    eduSublist = ul.find_elements_by_tag_name("li")
                except NoSuchElementException:
                    print("ERROR: Could not extract elements from education sublist")
                    return None
            except TimeoutException:
                pass

            # Nested education
            if eduSublist:
                # Have not discovered how to implement yet
                # Doesn't look like sublists exist in education
                pass
            # Single Element
            else:
                ed = Education()

                # Degree
                try:
                    ed.degree = edu.find_element_by_xpath("./div/div/a/div[2]/div/p[2]/span[2]").text
                except NoSuchElementException:
                    print("ERROR: Cannot find degree")
                    return None

                # Degree Type
                try:
                    ed.degree_type = edu.find_element_by_xpath("./div/div/a/div[2]/div/p[1]/span[2]").text
                except NoSuchElementException:
                    print("ERROR: Cannot find degree type")
                    return None

                # Institution
                try:
                    ed.institution = edu.find_element_by_xpath("./div/div/a/div[2]/div/h3").text
                except NoSuchElementException:
                    print("ERROR: Cannot find institution")

                # GPA
                try:
                    ed.GPA = edu.find_element_by_xpath("./div/div/a/div[2]/div/p[3]/span[2]").text
                except NoSuchElementException:
                    pass

                # Activities
                try:
                    ed.activities = edu.find_element_by_xpath("./div/div/a/div[2]/p[2]/span[2]").text
                except NoSuchElementException:
                    pass

                # Description
                try:
                    ed.description = edu.find_element_by_xpath("./div/div/div/p").text
                except NoSuchElementException:
                    pass

                # Media
                try:
                    ed.media = None
                except NoSuchElementException:
                    pass

                # Dates
                try:
                    dateElem = edu.find_element_by_xpath("./div/div/a/div[2]/p[1]/span[2]").text
                    dates = dateElem.split('–')
                    ed.start_date = dates[0].strip()
                    ed.end_date = dates[-1].strip()
                except NoSuchElementException:
                    pass

                education.append(ed)

        return education

    def ExtractEmployeeSkills(self, main):
        skills = {}

        skill_ol = None
        tries = 0
        # These elements were not rendering because you have to scroll to them first
        while skill_ol is None and tries < 3:
            self.driver.execute_script("window.scrollTo(0, 2000)")
            tries += 1

            # Expand Skills (if exists)
            try:
                skill_ol = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "ol")))
            except TimeoutException:
                pass

        if skill_ol is None:
            return None

        try:
            section = skill_ol.find_element_by_xpath("./parent::*")
            div = section.find_element_by_xpath("./div[2]")
            buttons = div.find_elements_by_tag_name("button")

            for button in buttons:
                button.click()
        except NoSuchElementException:
            pass

        # Extracting Main Skills
        # print(section.text)
        try:
            skillList = skill_ol.find_elements_by_xpath("./child::*")

            mainCat = "Main"
            skills[mainCat] = []

            for skl in skillList:
                ski = Skill()
                ski.skill = skl.find_element_by_xpath("./div/div[2]/p").text
                skills[mainCat].append(ski)
        except NoSuchElementException:
            print("ERROR: No main skills found")
            return None

        #Extracting Expanded Skills
        try:
            expandedSkillElem = main.find_element_by_css_selector("#skill-categories-expanded")

            expandedSkillList = expandedSkillElem.find_elements_by_xpath("./child::*")

            for categoryElem in expandedSkillList:
                category = categoryElem.find_element_by_tag_name("h3").text
                skills[category] = []
                categorySkillList = categoryElem.find_elements_by_tag_name("li")
                for categorySkill in categorySkillList:
                    skl = Skill()
                    skl.skill = categorySkill.find_element_by_xpath("./div/div[2]/p").text
                    skills[category].append(skl)
        except NoSuchElementException:
            pass

        return skills

    def ExtractEmployeeAccomplishments(self, main):
        accomplishments = {}

        # Have to scroll down to hit accomplishments similarly to skills

        accompIndicator = None
        tries = 0
        # These elements were not rendering because you have to scroll to them first
        while accompIndicator is None and tries < 3:
            self.driver.execute_script("window.scrollTo(0, 2000)")
            tries += 1

            try:
                accompIndicator = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME,
                         "NEED TO INITIALIZE THIS")))
            except TimeoutException:
                pass

        if accompIndicator is None:
            return None

        categoryList = None
        for category in categoryList:
            if category not in accomplishments:
                accomplishments[category] = []

            accomplishmentList = None
            for accomplishment in accomplishmentList:
                accomplishments[category].append(accomplishment)

        return accomplishments

    def ExtractProfileAttributes(self, employeeURL: str) -> Employee:
        # Navigate to web page
        self.driver.get(employeeURL)

        print("Extracting attributes from: ", employeeURL, "\n", sep="")

        # Contains all relevant profile attributes
        main = None
        try:
            main = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME,
                     "main")))
        except TimeoutException:
            print("ERROR: Could not find <main>")

        # If main cannot be found, no profile elements can be extracted
        if main is None:
            return -1

        # Initialize Employee Object
        currentEmployee = Employee()

        # Last split in employeeURL
        currentEmployee.user_url_id = employeeURL.split("/")[-1]

        try:
            nameElement = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div/section/div[2]/div[2]/div[1]/div[1]/h1")))

            if nameElement:
                currentEmployee.name = nameElement.text
        except TimeoutException:
            pass

        try:
            currentEmployee.location = main.find_element_by_xpath("//div/section/div[2]/div[2]/div[2]/span[1]").text
        except NoSuchElementException:
            pass

        # Header
        try:
            currentEmployee.header = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div/section/div[2]/div[2]/div[1]/div[2]"))).text
        except TimeoutException:
            pass

        try:
            currentEmployee.about = WebDriverWait(main, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//div/div/div[5]/section/div"))).text

            if currentEmployee.about[-8: 0] == "see more":
                currentEmployee.about = currentEmployee.about[:-10]
        except TimeoutException:
            pass

        #currentEmployee.website = None
        currentEmployee.experience = self.ExtractEmployeeExperiences(main)  # List
        currentEmployee.education = self.ExtractEmployeeEducation(main)  # List
        currentEmployee.skills = self.ExtractEmployeeSkills(main)  # List
        # Deprecated, accomplishments have been reworked
        #currentEmployee.accomplishments = self.ExtractEmployeeAccomplishments(main)  # List

        return currentEmployee

# Driver Code
if USERNAME and PASSWORD != "":
    database = InsertToLinkedInDB("10.33.113.250", 3308, DATABASE_USERNAME, DATABASE_PASSWORD)
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH, database)
    #driver.LinkedInPeopleSearch("Microsoft")
    URL = "https://www.linkedin.com/in/josh-braida-358a5476/"
    emp = driver.ExtractProfileAttributes(URL)
    print(emp)
