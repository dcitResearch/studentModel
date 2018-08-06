from StudentModel import *


pp = pprint.PrettyPrinter(indent=4)

student_model = StudentModel()

pp.pprint(student_model.get_courses())

print("\n\n")

pp.pprint(student_model.get_students())
