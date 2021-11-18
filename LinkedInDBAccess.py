# Could perform insertions over connection
# Or could send the employee data in bulk and make insertions locally
# Is this possible to bulk insert?

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

from Employee import Employee
from Education import Education
from Experience import Experience

class InsertToLinkedInDB:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def __connect__(self):
        """ Connect to MySQL database """
        conn = None
        try:
            conn = mysql.connector.connect(host=self.host,
                                           port=self.port,
                                           user=self.user,
                                           password=self.password)

            return conn
        except Error as e:
            print(e)

    def __LoadEmployeeURLs__(self):
        query = 'SELECT user_url FROM EMPLOYEE'
        employeeURLs = []

        try:
            conn = self.__connect__()

            cursor = conn.cursor()
            cursor.execute(query)

            for (user_url, ) in cursor:
                employeeURLs.append(user_url)

        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

        return employeeURLs

    def InsertEmployees(self, employeeList: Employee):
        for employee in employeeList:
            # Store employee attr in Employee table
            empInsert, expInsert, eduInsert, skillInsert, accompInsert = self.__ExtractTableTuples__(
                employee)

            emp_id = self.__InsertEmployeeTuple__(empInsert)
            self.__InsertExperienceTuples__(expInsert, emp_id)
            self.__InsertEducationTuples__(eduInsert, emp_id)
            self.__InsertSkillTuples__(skillInsert, emp_id)
            self.__InsertAccomplishmentTuples__(accompInsert, emp_id)

    def __ExtractTableTuples__(self, employee):
        empInsert = self.__ExtractEmployeeTuple__(employee)
        expInsert = self.__ExtractExperienceTuples__(employee)
        eduInsert = self.__ExtractEducationTuples__(employee)
        skillInsert = self.__ExtractSkillTuples__(employee)
        accompInsert = self.__ExtractAccomplishmentTuples__(employee)

        return empInsert, expInsert, eduInsert, skillInsert, accompInsert

    def __ExtractEmployeeTuple__(self, employee):
        return ( employee.user_url_id, employee.name, employee.location, employee.header, employee.about )

    def __ExtractExperienceTuples__(self, employee):
        exps = employee.experience

        tuples = []
        for exp in exps:
            # Appends a tuple of two tuples: First tuple for exp table, Second tuple for empexp table
            tuples.append(((exp.position, exp.company_name),
                           (self.__CastToDate__(exp.start_date), exp.location, exp.description, self.__CastToDate__(exp.end_date), exp.employment_type)))

        return tuples

    # NEED TO CAST DATES
    # SHOULD DECLARE A FUNCTION
    def __ExtractEducationTuples__(self, employee):
        edus = employee.education

        tuples = []
        for edu in edus:
            # Appends a tuple of two tuples: First tuple for edu table, Second tuple for empedu table
            tuples.append(((edu.degree, edu.degree_type),
                           (self.__CastToDate__(edu.start_date), edu.institution, edu.GPA, edu.activities, edu.description, self.__CastToDate__(edu.end_date))))

        return tuples

    def __ExtractSkillTuples__(self, employee):
        tuples = []
        for category in employee.skills:
            for skill in employee.skills[category]:
                tuples.append((skill, category))

        return tuples

    def __ExtractAccomplishmentTuples__(self, employee):
        tuples = []
        for category in employee.accomplishments:
            for accomp in employee.accomplishments[category]:
                tuples.append((accomp, category))

        return tuples

    def __CastToDate__(self, dateStr: str) -> date:
        if dateStr.__contains__('Present'):
            return None

        d = datetime.strptime(dateStr, '%b %Y')
        return d.date()

    """
    InsertToLinkedInDB::__InsertEmployeeTuple__

    Description:
        Inserts only the Employee components needed to initialize a tuple in the Employee table

    Parameters:
        empInsert -- Employee components needed for Employee tuple
    """

    def __InsertEmployeeTuple__(self, empInsert: (str)) -> int:
        query = "INSERT INTO employee(user_url,name,location,header,about) " \
                "VALUES(%s,%s,%s,%s,%s)"
        args = empInsert

        try:
            conn = self.__connect__()

            cursor = conn.cursor()
            cursor.execute(query, args)

            if cursor.lastrowid:
                return cursor.lastrowid
            else:
                print('last insert id not found')
                return None

            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def __InsertExperienceTuples__(self, expInsert: [(), ()], emp_id: int):
        expQuery = "INSERT INTO EXPERIENCE(position, company_name) " \
                   "VALUES(%s,%s)"
        try:
            conn = self.__connect__()
            cursor = conn.cursor()
            for exp in expInsert:
                expArgs = exp[0]

                cursor.execute(expQuery, expArgs)

                exp_id = cursor.lastrowid

                empExpQuery = "INSERT INTO EMPLOYEEEXPERIENCE(emp_id,exp_id,start_date,location,description,end_date,employment_type) " \
                              f"VALUES({emp_id},{exp_id},%s,%s,%s,%s,%s)"
                empExpArgs = exp[1]

                cursor.execute(empExpQuery, empExpArgs)
            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def __InsertEducationTuples__(self, eduInsert: [(), ()], emp_id: int):
        eduQuery = "INSERT INTO EDUCATION(degree,degree_type) " \
                   "VALUES(%s,%s)"
        try:
            conn = self.__connect__()
            cursor = conn.cursor()

            for edu in eduInsert:
                eduArgs = edu[0]

                cursor.execute(eduQuery, eduArgs)

                edu_id = cursor.lastrowid

                empEduQuery = "INSERT INTO EMPLOYEEEDUCATION(emp_id,edu_id,start_date,institution,GPA,activities,description,end_date) " \
                              f"VALUES({emp_id},{edu_id},%s,%s,%s,%s,%s)"
                empEduArgs = edu[1]

                cursor.execute(empEduQuery, empEduArgs)
            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def __InsertSkillTuples__(self, skillInsert: [(str)], emp_id: int):
        skillQuery = "INSERT INTO SKILL(skill, category) " \
                   "VALUES(%s,%s)"
        try:
            conn = self.__connect__()
            cursor = conn.cursor()

            for skill in skillInsert:
                skillArgs = skill

                cursor.execute(skillQuery, skillArgs)

                skill_id = cursor.lastrowid

                empSkillQuery = "INSERT INTO EMPLOYEESKILL(emp_id,skill_id) " \
                              f"VALUES({emp_id},{skill_id})"

                cursor.execute(empSkillQuery)
            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()

    def __InsertAccomplishmentTuples__(self, accompInsert: [(str)], emp_id: int):
        accompQuery = "INSERT INTO ACCOMPLISHMENT(accomp, category) " \
                   "VALUES(%s,%s)"
        try:
            conn = self.__connect__()
            cursor = conn.cursor()

            for accomp in accompInsert:
                accompArgs = accomp

                cursor.execute(accompQuery, accompArgs)

                accomp_id = cursor.lastrowid

                empAccompQuery = "INSERT INTO EMPLOYEEACCOMPLISHMENT(emp_id,skill_id) " \
                              f"VALUES({emp_id},{accomp_id})"

                cursor.execute(empAccompQuery)
            conn.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            conn.close()
