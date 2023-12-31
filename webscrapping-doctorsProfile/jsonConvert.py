# Python program to convert text
# file to JSON
 
##NOTE: Data for Psychologist not entered via this code.
import json
 
 
# the file to be converted to
# json format
filename = 'webscrapping-doctorsProfile/doctor.txt'
 
# dictionary where the lines from
# text will be stored
dict1 = {}
subdict = {}

s = "Certifications & Licensure:American Board of Dermatology,Certified in Dermatology;TX State Medical License,Active through 2025"
command, description = s.strip().split(":",1)
# creating dictionary
category_list = [
            "General Practitioner",
            "Cardiologist",
            "Dermatologist",
            "Pediatrics",
            "Neurologist",
            "Orthopedic Surgeon",
            "Radiologist",
            "Gastroenterologist",
            "Oncologist",
            'Pulmonologist',
            "psychologist", 
            'psychiatrist',
            'rheumatologist',
            'endocrinologist',
            'ophthalmologist'
        ]


with open(filename) as fh:
 
    for line in fh:
        
        # reads each line and trims of extra the spaces
        # and gives only the valid words
        if line.strip().isdigit():
            if subdict is not None:
                subdict = {}
            #print(category_list[int(line)-1])
            if category_list[int(line)-1] not in dict1.keys():
                dict1[category_list[int(line)-1]] = []
            #dict1[category_list[int(line)-1]] = []
            dict1[category_list[int(line)-1]].append(subdict)
 
        else: 
            print(line)
            command, description = line.strip().split(":",1)
 
            subdict[command] = description.strip().split(";")
 
# creating json file
# the JSON file is named as test1
out_file = open("doctor_info.json", "w")
json.dump(dict1, out_file, indent = 4, sort_keys = False)
out_file.close()