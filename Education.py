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