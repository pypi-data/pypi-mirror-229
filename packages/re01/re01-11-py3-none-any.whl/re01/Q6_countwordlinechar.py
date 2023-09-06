print("""
Q6 ) Python program to print the number of lines, words and characters present in the given file.
      
def count_lines_word_characters(file_path):
  line_count = 0
  word_count = 0
  character_count = 0
  with open(file_path, "r") as file:
    for line in file:
      line_count +=1
      words = line.split()
      word_count += len(words)
      character_count += len(line)
  print("Number of lines :", line_count)
  print("Number of words :", word_count)
  print("Number of characters:", character_count)
  
file_path = "input.txt"
count_lines_word_characters(file_path)

input.txt:
hello 
word 
pyhton snake
elephant
cow
""")