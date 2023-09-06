print("""
Q2) Given a list of strings, count and print the number of strings where the string length is 
2 or more & the 1st & last characters are same.

def count_strings(list):
  count = 0
  for s in list:
    if len(s) >=2 and s[0] == s[-1]:
      count+=1
  return count
strings = ["racecar", "apple", "civic", "pyhton", "madam"]
count = count_strings(strings)
print(f" there are {count} strings the meet the criteria")""")