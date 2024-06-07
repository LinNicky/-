import re
pattern = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}$"
password = input("Enter string to test: ")
result = re.findall(pattern, password)
if (result):
    print("Valid password")
else:
    print("Password not valid")