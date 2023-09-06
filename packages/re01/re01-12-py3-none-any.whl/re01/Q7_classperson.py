print("""
Q7) Write a program that has a class Person, inherit a class Student from Person which is has a class MarksAttendance   
      
      
class Person:
  def __init__(self, usn, name, dob , gender):
    self.usn = usn
    self.name = name
    self.dob = dob
    self.gender = gender
class Student(Person):
  def __init__(self, usn, name, dob , gender ,marks, attendance):
    super().__init__(usn, name, dob, gender)
    self.marks = marks
    self.attandence = attendance
class MarksAttandence():
  def __init__ (self, marks, attandence):
    self.marks = marks
    self.attandence = attandence
    
s = Student("1nt21ai043", "XYZ", 2002-11-29," M" , 85, 98)
print("usn:", s.usn)
print("name:", s.name)
print("dob :", s.dob)
print("gender ", s.gender)
print("Marks:", s.marks)
print("Attendance:", s.attandence)""")