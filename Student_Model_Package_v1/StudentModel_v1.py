# v1 uses local disk storage

# imports
import json         # for JSON :)
import os           # for file listing in directory
import pprint       # pretty print for dictionaries
import re           # regex for students
import string       # for isdigit()
import datetime     # datetime


# files and directories relative addresses
REST_response_students_file = '../my_elearning_module/REST_response/students.json'
courses_file = "../my_elearning_module/courses/courses.json"
students_directory = "../my_elearning_module/students/"
attendance_tracking_module_directory = "../attendance_tracking_module/"



class StudentModel:

    # attributes
    global courses_file, students_directory
    __courses = {}      # holds detailed information for all courses as decribed by the .json file [either from moodle myelearning or custom]
    __students = {}     # holds detailed information from REST response from my_elearning_module


    # constructor
    def __init__(self):
        self.read_courses()
        self.read_students_v1()
        self.read_tracking_module_attendance_records()


    # methods
    # reads all course info from the 'courses_file' .json into the __courses dictionary
    def read_courses(self):
        print("Reading courses from {}".format(courses_file))
        with open(courses_file, 'r') as read_file:
            self.__courses = json.load(read_file)
            print("Courses read successfully\n\n")


    # parses the .json REST_response file from my_elearning_module and creates the
    def parse_REST_response(self):



    # initial version design where each student has his own directory in the 'students_directory'
    # traverses the subdirectories in 'students_directory' and reads individual student .json files to populate the __students dictionary
    # each student directory is named by the student's id number
    # each student .json file is also named by the student's id number
    def read_students_v1(self):
        print("Reading students from {}".format(students_directory))
        student_ids = [re.sub("\D", "", file) for file in os.listdir(students_directory)]   # regex to return a list of all student sub-directories (example /816000772/ ) in the main 'students_directory'
        for id in student_ids:
            if id.isdigit():                                                                # only considers the directories that are digits
                file = students_directory + id + '/' + id + ".json"                                    # building the student.json file name from which data is read
                with open(file, "r") as read_file:                                          # opens and reads the student.json file
                    self.__students[id] = json.load(read_file)

                # for attendance records
                self.__students[id]["attendance_record"] = []                               # creates an empty attendance_record list for the new student

        print("Students read successfully\n\n")


    # reads the attendance records for students from the tracking_module
    def read_tracking_module_attendance_records(self):
        print("Reading attendance records from {}".format(attendance_tracking_module_directory))

        file_list = os.listdir(attendance_tracking_module_directory)                        # gets list of .json attendance files in the attendance_tracking_module_directory
        file_list.remove('desktop.ini')                                                     # removes the .ini created by the Google drive

        # reads each attendance.json file and updates the corresponding students' attendance_record in the students dictionary
        for file in file_list:
            file_name = attendance_tracking_module_directory + file
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


    # menu function (not currently implemented)
    def menu(self):
        return "1. Update Courses\n2. View Courses\n3. Update Students\n4. View Students\n5. Update Attendance Records\n6. View Attendance Records\n7. Quit\n\nEnter choice: "


    # getters and setters
    def get_courses(self):
        return self.__courses


    def get_students(self):
        return self.__students
