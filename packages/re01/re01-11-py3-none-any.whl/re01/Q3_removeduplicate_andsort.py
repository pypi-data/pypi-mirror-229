print("""
Q3 ) Write a python program to accept a sequence of whitespace separated words as input and prints the words after removing all duplicate words and sorting them alphanumerically.

def remove_dulpicate_sort(sentence):
  words = sentence.split(" ")
  unique_words = set(words)
  sorted_words = sorted(unique_words)
  return " ".join(sorted_words)

sentence = input("enter a sentence :")
result = remove_dulpicate_sort(sentence)
print(result)""")