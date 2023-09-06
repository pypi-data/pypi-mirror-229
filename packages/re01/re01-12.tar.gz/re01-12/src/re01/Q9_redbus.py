print("""
Q9 ) 9. Program to get all phone numbers of redbus.in by using web scraping and regular
  
from urllib import request
import re
reader = request.urlopen("https://www.redbus.in/info/redcare")
text = reader.read()
regex = "[0-9-]{9}[0-9-]+"
numbers = re.findall(regex, str(text), re.I)
for no in numbers:
  print(no)
  
--

import re,urllib
import urllib.request
u=urllib.request.urlopen("https://www.redbus.in/info/redcare")
text=u.read()
numbers=re.findall("[0-9-]{7}[0-9-]+",str(text))
for no in numbers:
    print(no)  
  



o/p - 
65-31582888
2023-09-05
24595215509
  """
  )