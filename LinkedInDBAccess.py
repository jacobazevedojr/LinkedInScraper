# Could perform insertions over connection
# Or could send the employee data in bulk and make insertions locally
# Is this possible to bulk insert?

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

from Employee import Employee
from Education import Education
from Experience import Experience

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, Table, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class EmployeeEducation(Base):
    __tablename__ = 'employee_education'
    emp_id = Column('emp_id', Integer, ForeignKey('employees.id'), primary_key=True)
    edu_id = Column('edu_id', Integer, ForeignKey('educations.id'), primary_key=True)
    start_date = Column('start_date', Date)
    end_date = Column('end_date', Date)
    GPA = Column('GPA', String(100))
    activities = Column('activities', Text)
    description = Column('description', Text)

    education = relationship("Education")

class EmployeeExperience(Base):
    __tablename__ = 'employee_experience'
    emp_id = Column('emp_id', Integer, ForeignKey('employees.id'), primary_key=True)
    exp_id = Column('exp_id', Integer, ForeignKey('experiences.id'), primary_key=True)
    start_date = Column('start_date', Date, primary_key=True)
    end_date = Column('end_date', Date)
    location = Column('location', String(100))
    description = Column('description', Text)
    employment_type = Column('employment_type', String(100))

    experience = relationship("Experience")

employee_skill = Table('employee_skill', Base.metadata,
                       Column('emp_id', Integer, ForeignKey('employees.id'), primary_key=True),
                       Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
                       )


class Employee(Base):
    # Has an implicit __init__() which accepts keywords according to those listed below
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    user_url = Column(String(100), unique=True)
    name = Column(String(100))
    location = Column(String(100))
    header = Column(String(250))
    about = Column(Text)

    educations = relationship("EmployeeEducation")
    experiences = relationship("EmployeeExperience")
    skills = relationship("Skill", secondary=employee_skill)

    def __repr__(self):
        return "<Employee(user_url='%s'\nname='%s'\nlocation='%s'\nheader='%s')>" % \
               (self.user_url, self.name, self.location, self.header)


class Education(Base):
    __tablename__ = 'educations'

    id = Column(Integer, primary_key=True)
    institution = Column(String(100))
    degree = Column(String(100))
    degree_type = Column(String(100))
    UniqueConstraint(institution, degree, degree_type)

class Experience(Base):
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key=True)
    position = Column(String(100))
    company_name = Column(String(100))
    UniqueConstraint(position, company_name)

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    skill = Column(String(100))
    category = Column(String(100))
    UniqueConstraint(skill, category)

class LinkedInDB:
    def __init__(self, database, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}")


    def __connect__(self):
        ''' Connect to MySQL database '''

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        return session

    def __createTables__(self):
        Base.metadata.create_all(self.engine)

    def __loadEmployeeURLs__(self):
        session = self.__connect__()
        employeeURLs = set()

        for instance in session.query(Employee).order_by(Employee.id):
            employeeURLs.add(instance.user_url)

        session.close()
        return employeeURLs

    def __checkIfDuplicateProfile__(self, url):
        session = self.__connect__()

        emp = session.query(Employee).filter(Employee.user_url==url).first()

        session.close()

        if emp is None:
            return False

        return True

    def insertEmployees(self, employeeList):
        session = self.__connect__()
        for employee in employeeList:
            emp, experiences, educations, skills = self.__extractTableTuples__(employee)
            employeeDupe = session.query(Employee). \
                            filter(Employee.user_url==emp.user_url).first()

            if employeeDupe is not None:
                print(emp.user_url, "is a duplicate")
                continue

            expList = {}
            for exp in experiences:
                experience = None
                expTuple = (exp[0].position, exp[0].company_name)

                # Sometimes, there are duplicate experiences before those experiences are entered into the DB
                # For instance, someone works for Tesla as an Intern twice while no one else has worked
                # the same position, company pair before. The query below will return nothing despite already adding
                # the new position, company pair earlier in the for loop.
                if expTuple in expList:
                    experience = expList[expTuple]
                else:
                    # Check if the tuple exists in the database
                    experience = session.query(Experience). \
                        filter(Experience.position == exp[0].position,
                               Experience.company_name == exp[0].company_name).first()

                    if experience is None:
                        experience = exp[0]
                        session.add(exp[0])

                    # Since the tuple didn't exist before, we add it to the dictionary
                    expList[expTuple] = experience

                exp[1].experience = experience
                # Append association object only
                emp.experiences.append(exp[1])
                session.add(exp[1])

            eduList = {}
            for edu in educations:
                education = None
                eduTuple = (edu[0].institution, edu[0].degree, edu[0].degree_type)

                if eduTuple in eduList:
                    education = eduList[eduTuple]
                else:
                    education = session.query(Education). \
                        filter(Education.institution == edu[0].institution, Education.degree == edu[0].degree,
                               Education.degree_type == edu[0].degree_type).first()

                    if education is None:
                        education = edu[0]
                        session.add(edu[0])

                    eduList[eduTuple] = education

                edu[1].education = education
                # Append association object only
                emp.educations.append(edu[1])
                session.add(edu[1])

            skillList = {}
            for skill in skills:
                ski = None
                skillTuple = (skill.skill, skill.category)

                if skillTuple in skillList:
                    ski = skillList[skillTuple]
                else:
                    ski = session.query(Skill). \
                        filter(Skill.skill == skill.skill,
                               Skill.category == skill.category).first()

                    if ski is None:
                        ski = skill
                        session.add(skill)

                    skillList[skillTuple] = ski

                emp.skills.append(ski)

            session.add(emp)
            session.commit()
        session.close()

    def __extractTableTuples__(self, employee):
        emp = self.__extractEmployeeTuple__(employee)
        exp = self.__extractExperienceTuples__(employee)
        edu = self.__extractEducationTuples__(employee)
        skill = self.__extractSkillTuples__(employee)

        return emp, exp, edu, skill

    def __extractEmployeeTuple__(self, employee):
        return Employee(user_url=employee.user_url_id, name=employee.name,
                        location=employee.location, header=employee.header, about=employee.about)

    def __extractExperienceTuples__(self, employee):
        exps = employee.experience

        tuples = []
        for exp in exps:
            # Appends a tuple of two tuples: First tuple for exp table, Second tuple for empexp table
            experience = Experience(position=exp.position, company_name=exp.company_name)
            employeeExperience = EmployeeExperience(start_date=self.__castToDate__(exp.start_date),
                                                    end_date=self.__castToDate__(exp.end_date),
                                                    location=exp.location,
                                                    description=exp.description,
                                                    employment_type=exp.employment_type
                                                    )
            tuples.append((experience, employeeExperience))

        return tuples

    def __extractEducationTuples__(self, employee):
        edus = employee.education

        tuples = []
        for edu in edus:
            # Appends a tuple of two tuples: First tuple for edu table, Second tuple for empedu table
            education = Education(institution=edu.institution, degree=edu.degree, degree_type=edu.degree_type)
            employeeEducation = EmployeeEducation(start_date=self.__castToDate__(edu.start_date),
                                                  end_date=self.__castToDate__(edu.end_date),
                                                  GPA=edu.GPA,
                                                  activities=edu.activities,
                                                  description=edu.description
                                                  )
            tuples.append((education, employeeEducation))

        return tuples

    def __extractSkillTuples__(self, employee):
        if employee.skills is None:
            return []

        skills = set()
        tuples = []
        for category in employee.skills:
            for skill in employee.skills[category]:
                if skill.lower() not in skills:
                    skl = Skill(skill=skill, category=category)
                    tuples.append(skl)
                    skills.add(skill.lower())

        return tuples

    def __castToDate__(self, dateStr: str) -> date:
        if dateStr is None:
            return None

        if dateStr.__contains__('Present') or len(dateStr) == 0:
            return None

        dateCheck = dateStr.split()
        if len(dateCheck) == 1:
            # The formatting of the experiences in nested sublists sometimes makes it difficult to extract dates
            # For now, we handle it by returning None, but there needs to be a work around somewhere within the scraper
            d = datetime.strptime(dateStr, '%Y')
        elif len(dateCheck) == 2:
            d = datetime.strptime(dateStr, '%b %Y')

        return d.date()