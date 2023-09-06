print(""" 
Q10) extract all mobile numbers present in input.txt where numbers are mixed with normal text data.

import re
file1 = open("input.txt", "r")
file2 = open("output.txt", "w")
for line in file1:
  list = re.findall('[7-9]\d{9}', line)
  for n in list:
    file2.write(n+"\an")
print("extracted all mobile no in output.txt")
file1.close()
file2.close()

input.txt:
hello
world
again
9284628473
python snake
0011284569
zebra

""")