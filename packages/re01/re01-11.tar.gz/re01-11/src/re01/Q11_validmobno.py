print("""
Q11) check whether the given number is a valid mobile number or not.
import re
n = input("enter number ")
m = re.fullmatch("[7-9]\d{9}",n)
if m!= None:
  print("valid mob no")
else :
  print("in valid mob no")""")