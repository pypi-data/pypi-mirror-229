print("""
Q4) Solve the following using Recursion:
• find the length of a string
• find the smallest element in a list      

def length(string):
    if string == "":
        return 0
    else:
        return 1 + length(string[1:] )
str = "Geeksfor. Geeks"

print ("length of string is :", length(str))

def find_min(list):
  if len(list) == 1:
    return list[0]
  return min(list[0], find_min(list[1:]))

listA = [9,6,1,80,9]
find_min(listA)""")