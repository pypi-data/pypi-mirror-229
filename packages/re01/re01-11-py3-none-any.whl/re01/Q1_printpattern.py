print(  """
  Q1 ) Write a Program to print the following pattern.
  
  alphabet = "A"
for i in range(1,6):
  for j in range(i*2-1):
    print(alphabet, end = "")
    alphabet = chr(ord(alphabet)+1)

    if alphabet > "Z":
      alphabet = "A"
  print()
  
  """)
  