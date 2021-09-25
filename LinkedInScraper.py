from selenium import webdriver
import time

from selenium.common.exceptions import NoSuchElementException

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
    return None, None

USERNAME, PASSWORD = GetUsernameAndPassword("creds.txt")

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
        time.sleep(40)

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
                time.sleep(20)

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
            button = list[-1].find_elements_by_tag_name("button")
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

# Driver Code
if (USERNAME and PASSWORD != ""):
    driver = LinkedInScraper(USERNAME, PASSWORD, DRIVER_PATH)
    driver.LinkedInPeopleSearch("Microsoft")
