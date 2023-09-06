print("""
      

from  datetime import datetime, timedelta

class birthday_calc:
  def __init__(self, birthday):
    self.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()

  def age(self):
    print("self.birthday:",self.birthday )
    today = datetime.today().date()
    age = today.year - self.birthday.year
    if (today.month, today.day) < (self.birthday.month, self.birthday.day):
      age -= 1
    return age

  def timetobirthday(self):
    today  = datetime.today().date()
    next_birthday = datetime(today.year, self.birthday.month, self.birthday.day ).date()

    if next_birthday<today:
      next_birthday = datetime(today.year + 1, self.birthday.month, self.birthday.day).date()

    time_till_nextbirthday = next_birthday- today
    days = time_till_nextbirthday.days
    hours , remainder = divmod(time_till_nextbirthday.seconds, 3600)
    minutes , seconds = divmod(remainder, 60)

    return days, hours , minutes, seconds

dob = input("enter birthdate (yyyy-mm-dd):")
calc = birthday_calc(dob)
age = calc.age()
print("age = ", age)

days, hours, minutes , seconds = calc.timetobirthday()
print(f"days {days } hours {hours}, minutes {minutes}, sec {seconds}")""")