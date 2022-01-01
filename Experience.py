class Experience:
    def __init__(self):
        self.position = ""
        self.company_name = ""
        self.employment_type = ""
        self.location = ""
        self.description = ""
        self.media = ""
        self.start_date = ""
        self.end_date = ""

    def __str__(self):
        date = ""
        if self.start_date and self.end_date is not None:
            date = self.start_date + " - " + self.end_date
        else:
            date = "ERROR"
        return f"     Position: {self.position}\n     Company Name: {self.company_name}\n     Employment Type: {self.employment_type}\n     Location: {self.location}\n     Dates: {date}\n"
