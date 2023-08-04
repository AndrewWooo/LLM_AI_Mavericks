# Python program to convert text
# file to JSON
 
 
import json
 
 
# the file to be converted to
# json format
filename = 'doctor.txt'
 
# dictionary where the lines from
# text will be stored
dict1 = {}
subdict = {}

s = "Certifications & Licensure:American Board of Dermatology,Certified in Dermatology;TX State Medical License,Active through 2025"
command, description = s.strip().split(":",1)
# creating dictionary
with open(filename) as fh:
 
    for line in fh:
        
        # reads each line and trims of extra the spaces
        # and gives only the valid words
        if line.strip().isdigit():
            dict1[int(line)] = subdict
        else: 
            print(line)
            command, description = line.strip().split(":",1)
 
            subdict[command] = description.strip().split(";")
 
# creating json file
# the JSON file is named as test1
out_file = open("test1.json", "w")
json.dump(dict1, out_file, indent = 4, sort_keys = False)
out_file.close()