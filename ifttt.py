import requests,re

private_url = open('../ifttturl.txt','r').read()
htmlmessage = open('dailymessage.html','r').read()


string1 = "Delware County COVID-19 Monitor<br>\n"
string2 = htmlmessage
string3 = '<img src="https://github.com/ptgressman/COVIDanalysis/blob/master/plotnearby.png?raw=true">'
string3 +='<br><img src="https://github.com/ptgressman/COVIDanalysis/blob/master/hospital.png?raw=true">'
string3 +='<br><img src="https://public.tableau.com/static/images/D1/D1LastWeek/LastWeek/1.png">'
r = requests.post(private_url, params={"value1":string1,"value2":string2,"value3":string3})
