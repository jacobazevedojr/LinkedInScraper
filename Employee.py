from Education import Education
from Experience import Experience


class Employee:
    def __init__(self):
        self.experience = None # List
        self.education = None # List
        self.skills = None # Dict
        self.accomplishments = None # Dict

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
            for key in self.accomplishments:
                acom += ("     " + key + '\n')
                for ac in self.accomplishments[key]:
                    acom += (str(ac) + '\n')

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