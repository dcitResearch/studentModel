# imports
import json         # for JSON :)
import os           # for file listing in directory
import pprint       # pretty print
import re           # regex for students
import string       # for isdigit()
import datetime     # datetime


# files and directories relative addresses
courses_file = "../my_elearning_module/courses/courses.json"
students_directory = "../my_elearning_module/students/"
attendance_record_directory = "../attendance_tracking_module/"


class StudentModel:

    # attributes
    global courses_file, students_directory
    __courses = {}
    __students = {}


    # constructor
    def __init__(self):
        self.read_courses()
        self.read_students()
        self.read_attendance_records()


    # methods
    def read_courses(self):
        print("Reading courses from {}".format(courses_file))
        with open(courses_file, 'r') as read_file:
            self.__courses = json.load(read_file)
            print("Courses read successfully\n\n")


    def read_students(self):
        print("Reading students from {}".format(students_directory))
        student_ids = [re.sub("\D", "", file) for file in os.listdir(students_directory)]
        for id in student_ids:
            if id.isdigit():
                file = students_directory + id + ".json"
                with open(file, "r") as read_file:
                    self.__students[id] = json.load(read_file)

                # for attendance records
                self.__students[id]["attendance_record"] = []

        print("Students read successfully\n\n")


    def read_attendance_records(self):
        print("Reading attendance records from {}".format(attendance_record_directory))

        file_list = os.listdir(attendance_record_directory)
        file_list.remove('desktop.ini')

        for file in file_list:
            file_name = attendance_record_directory + file
            course_code, time = file.strip(".json").split("_")
            time = datetime.datetime.strptime(time, "%Y-%m-%d-%H-%M")
            with open(file_name, 'r') as read_file:
                attendance = json.load(read_file)
            for id in attendance.keys():
                self.__students[id]["attendance_record"].append({
                    "course_code": course_code,
                    "time": time,
                    "present": attendance[id]
                }.copy())

        print("Attendance records read successfully\n\n")


    # menu function
    def menu(self):
        return "1. Update Courses\n2. View Courses\n3. Update Students\n4. View Students\n5. Update Attendance Records\n6. View Attendance Records\n7. Quit\n\nEnter choice: "


    # getters and setters
    def get_courses(self):
        return self.__courses


    def get_students(self):
        return self.__students
