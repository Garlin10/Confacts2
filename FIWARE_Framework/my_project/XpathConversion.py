# Python program to find yesterday,
# today and tomorrow
 
 
# Import datetime and timedelta
# class from datetime module
from datetime import datetime, timedelta
 
 
# Get today's date
presentday = datetime.now() # or presentday = datetime.today()
# Get Tomorrow
tomorrow = presentday + timedelta(1)
# strftime() is to format date according to
# the need by converting them to string
print("Today = ", presentday.strftime('%d-%m-%Y'))
print("Tomorrow = ", tomorrow.strftime('%d-%m-%Y'))
today = presentday.strftime('%d-%m-%Y')
tomorrow = tomorrow.strftime('%d-%m-%Y')
age = 74
xpath = ("Hello, {today} {tomorrow}. You are {age}. ")
print(xpath.format(today=today, tomorrow=tomorrow, age=age))
