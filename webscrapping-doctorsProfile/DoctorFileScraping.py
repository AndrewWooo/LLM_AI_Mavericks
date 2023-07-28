import requests
from bs4 import BeautifulSoup
import re
#grab website from online
#res = requests.get('https://www.mdvip.com/doctors/karledelmannmd?requestType=JoinNow')
#res_plano = requests.get('https://www.mdvip.com/doctor-search?location=Plano%2C%20TX%2C%20USA')
#noStarchSoup = BeautifulSoup(res.content, 'html.parser')
#planoSoup = BeautifulSoup(res_plano.content, 'html.parser')

#with open('plano.html','w',encoding='utf-8') as file:
#    file.write(str(planoSoup.prettify()))
#file.close()
#with open("output.html", "w", encoding = 'utf-8') as f:
#    # prettify the soup object and convert it into a string  
#    f.write(str(noStarchSoup.prettify()))
#f.close()
#html file
with open('plano.html', 'r') as f:
    contents = f.read()
f.close()
noStarchSoup = BeautifulSoup(contents, 'html.parser')

title = noStarchSoup.find_all('title')[0]

doctors = noStarchSoup.findAll('div',{"class":"views-row"})
CLEANR = re.compile('<.*?>') 

with open('output.txt', mode='wt', encoding='utf-8') as file:
#print(doctors)
    for p in doctors:
        name = p.find('a',{"class":"phy-name"})
        #profilelink = name.get('href')
        #print(profilelink)
        cleanname = re.sub(CLEANR, '', str(name))
        address = p.find('div',{"class":"addr-wrapper"})
        cleanaddress = re.sub(CLEANR, '', str(address))
        file.write(cleanname.strip()+'\n')
        file.write(cleanaddress.strip()+'\n')

    base_url = 'https://www.mdvip.com'
# profile
    for link in noStarchSoup.findAll('a',{"class":"phy-name"}):
        profile = link.get('href')
    

    # get profile information
        review = requests.get(base_url+profile)
        reviewSoup = BeautifulSoup(review.content,'html.parser')

        education = reviewSoup.find('div', {"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--content"}).text
        certification = reviewSoup.find('div',{"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--2--content"}).text
        affiliation = reviewSoup.find('div',{"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--3--content"}).text
        file.write(education.strip()+'\n')
        file.write(certification.strip()+'\n')
        file.write(affiliation.strip()+'\n')
file.close()




#education = noStarchSoup.find('div', {"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--content"})
#print_edu = education.find_all('div',{"class":"cat-one"})
#title_edu = "Education"#education.find('a').text

#certification = noStarchSoup.find('div', {"class":"js-form-wrapper form-wrapper form-item js-form-item panel panel-default", "id":"bootstrap-panel--2"})
#affiliation = noStarchSoup.find('div', {"class":"js-form-wrapper form-wrapper form-item js-form-item panel panel-default", "id":"bootstrap-panel--3"})

#title_cert = "Certification"#certification.find('a').text
#title_aff = "Hospital Affilation"#affiliation.find('a').text
#print_cert = noStarchSoup.find('div',{"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--2--content"})
#print_aff = noStarchSoup.find('div',{"class":"panel-body panel-collapse collapse fade", "id":"bootstrap-panel--3--content"})


#review_link = noStarchSoup.find('div', {"id":"testimonials"})
#link_list = []
#for link in review_link.findAll('a'):
#    if link.get('href') != "/doctors/karledelmannmd":
#        link_list.append(link.get('href'))
#link_list = set(link_list)
#print(title)
#print(education)
#print(certification)
#print(affiliation)
#title_name = title.text.split('-')
#with open('output.txt', mode='wt', encoding='utf-8') as file:
    #file.write(title_name[0])
    #file.write(education)
    #file.write(str(certification))
    #file.write(str(affiliation))
    #file.write(str(review))
#    file.write(title_edu+':\n')
#    for i in print_edu:
        #print(i.text)
#        file.write('\t'+i.text+'\n')
#    file.write('\n')
#    file.write(title_cert+':\n')
#    for i in print_cert:
        #print(i.text)
#        file.write('\t'+i.text.strip()+'\n')
#    file.write('\n')
#    file.write(title_aff+':\n')
#    for i in print_aff:
        #print(i.text)
#        file.write('\t'+i.text.strip()+'\n')
    #for link in link_list:
    #    file.write('mdvip.com'+link+'\n')
#    base_url = "https://www.mdvip.com"
#    count = 1
#    for link in link_list:
#        url = base_url+link
        #print(url)
  #      review = requests.get(url)
 #       reviewSoup = BeautifulSoup(review.content,'html.parser')
#        reviewContent = reviewSoup.find('div',{"class":"blog-discription"})
#        file.write(str("Review#"+str(count)+'\n'))
#        file.write(reviewContent.text+'\n')
#        count+=1
#file.close()


# write the reviews in the txt file

#url = "https://www.mdvip.com/patients/member-testimonials/kari-has-worked-extremely-hard"
#review = requests.get(url)
#reviewSoup = BeautifulSoup(review.content,'html.parser')
#reviewContent = reviewSoup.find('div',{"class":"blog-discription"})
#print(reviewContent.text)



#    with open("review.html", "w") as file:
#    # prettify the soup object and convert it into a string  
#        file.write(str(reviewSoup.prettify()))
#    file.close()

