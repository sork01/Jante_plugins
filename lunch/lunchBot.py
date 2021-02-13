#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import code
import time
# install BeutifulSoup by: pip3 install beautifulsoup4
from bs4 import BeautifulSoup
# install requests: pip3 install requests
import requests
import datetime

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

import jantepastedb
from plugins.parsingplugintemplate import parsingplugintemplate

class lunchBotContainer(parsingplugintemplate):
    """docstring for lunchBotContainer."""
    def __init__(self, bot):
        super(lunchBotContainer, self).__init__(bot, "Returns todays lunches. Right now the supported restaurants are systerochbror, iko, Asian Wokhouse.", "lunch")


    def help(self):
        return ("This plugin helps search for lunch options near KTH\nUsage     !lunch resturang (Iko)")

    def getLunchIko(self):
        return ("Iko Food Palace: Stor Lunchbuffe med sushi, thai, kinesiska rätter från kl 10.30 till 14.30 varje dag, Pris: 90 kr")


    def random(self):
        return("not implemented yet")

    def getLunchList(self):


        ans = ("Lunch idag: \n\n")
        ans += ("Iko: \n")
        ans += self.getLunchIko()
        ans += ("\n\nSysterobror: \n")
        ans += self.getLunchSysterOchBror()
        ans += ("\n\nBrazilia: \n")
        ans += self.getLunchBrazilia()
        ans += ("\n\nWok: \n")
        ans += self.kvartersmenyn("http://www.kvartersmenyn.se/rest/12095")
        ans += ("\n\nNymble: \n")
        ans += self.kvartersmenyn("http://www.kvartersmenyn.se/rest/12247")
        ans += ("\n\nJärnväg: \n")
        ans += self.kvartersmenyn("http://www.kvartersmenyn.se/rest/8641")
        ans += ("\n\nIndiska: \n")
        ans += self.kvartersmenyn("http://www.kvartersmenyn.se/rest/14898")
        #Try posting to jantepaste if the list is too long
        hbstatus, hbresult = jantepastedb.post(ans)

        if hbstatus == True:
            return hbresult
        else:
            return ans

    def getLunchSysterOchBror(self):
        weekDay = self.getWeekDayNumber()
        #place dosnt serve lunch on weekends
        if weekDay > 4:
            weekDay = 4

        #place start counting week on 1
        weekDay = weekDay +1

        try:
            #Get the webpage with requests
            r = requests.get("http://www.systerobror.se/lunch/")
        except requests.exceptions.RequestException as e:
            return e
        #make it into a BeautifulSoup
        soup = BeautifulSoup(r.content, "html.parser")

        # create the class we are searching for in the HTML doc
        pageReq = 'single-lunch day-%d'%(weekDay)

        #find the days manu
        lista = soup.find('div',attrs={'class':pageReq})

        #go down the children
        single = list(lista.children)[1]
        #choose the span where the dishes are presented
        span= list(single.children)[3]

        #returns the dishes and removes leading spaces from output
        return (span.get_text().lstrip())

    def getLunchBrazilia(self):
        r = requests.get('http://restaurangbrazilia.se/')
        soup = BeautifulSoup(r.content, "html.parser")
        lista = soup.findAll("h4", class_="menu-dish-name")
        if (len(lista) != 0):
            return (lista[0].get_text() + "\n" + lista[1].get_text() + "\n" + lista[2].get_text())
        else:
            return ("No menu for Brazilia available today")


    def kvartersmenyn(self, restaurang):
        try:
            r = requests.get(restaurang)
        except requests.exceptions.RequestException as e:
            return e
        soup = BeautifulSoup(r.content, "html.parser")
        lista = soup.find('div',attrs={'class':"meny"})

        if lista == None:
            return ''

        #s = re.sub('<br\s*?>', '\n', lista)
        # ersätt <br> taggar med mellanslag
        for br in lista.find_all("br"):
            br.replace_with("\n")

        #print(lista.get_text())
        lista = lista.get_text()
        today = self.getWeekDay()
        #print("detta är vad vi får när vi tar bort fram till dagen\n")
        #print(lista[lista.find(today):])

        tomorrow = self.getWeekDayNumber() +1
        #print("This is the day tomorrow:%d"%(tomorrow))
        weekdays = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

        tomorrow = weekdays[tomorrow]


        ans = lista.split(today)[-1].split(tomorrow)[0]
        return ans


    def wok(self):
        try:
            r = requests.get("http://www.kvartersmenyn.se/rest/12095")
        except requests.exceptions.RequestException as e:
            return e
        soup = BeautifulSoup(r.content, "html.parser")
        lista = soup.find('div',attrs={'class':"meny"})
        lista = lista.get_text()
        # kvartersmenyn har valt att lagt all i samma så vi behöver klippa i
        # lista så vi tar dagen till imorgon
        today = self.getWeekDay()
        tomorrow = self.getWeekDayNumber() +1
        weekdays = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
        tomorrow = weekdays[tomorrow]

        ans = lista.split(today)[-1].split(tomorrow)[0]
        return ans

    def getWeekDay(self):

        weekdays = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
        #day is an integer going from 0 (monday) to 6 (sunday)
        day = datetime.datetime.today().weekday()
        return weekdays[day]


    def getWeekDayNumber(self):
        #day is an integer going from 0 (monday) to 6 (sunday)
        return datetime.datetime.today().weekday()


    def parse(self, message):
        text = message.getText()
        if text == "":
            return self.getLunchList()
        elif text.startswith("iko"):
            return self.getLunchIko()
        elif text.startswith("systerochbror"):
            return self.getLunchSysterOchBror()
        elif text.startswith("brazilia"):
            return self.getLunchBrazilia()
        elif text.startswith("wok"):
            wok = "http://www.kvartersmenyn.se/rest/12095"
            return self.kvartersmenyn(wok)
        elif text.startswith("nymble"):
            nymble = "http://www.kvartersmenyn.se/rest/12247"
            return self.kvartersmenyn(nymble)
        elif text.startswith("järnväg"):
            jarnvag = "http://www.kvartersmenyn.se/rest/8641"
            return self.kvartersmenyn(jarnvag)
        elif text.startswith("felix"):
                india = "http://www.kvartersmenyn.se/rest/14898"
                return self.kvartersmenyn(india)
        elif text.startswith("help"):
            return self.help()

        return "That is not a valid lunch command, use help to get directions"


    def get_tests(self):
        # non-chat-command tests
        assert self.getWeekDayNumber() in [0,1,2,3,4,5,6]
        assert self.getWeekDay() in ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

        # chat command tests
        tests = list()

        # for convenience, since it is used by many tests
        default_response = 'That is not a valid lunch command, use help to get directions'

        # test that the default reponse works
        tests.append(['Default response',
                      '!lunch asdf', botplugin.test_equal, default_response])

        # test that iko gives a non-empty string not equal to default response
        tests.append(['Iko 1',
                      '!lunch iko', botplugin.test_nonempty_string])
        tests.append(['Iko 2',
                      '!lunch iko', botplugin.test_not_equal, default_response])

        # test that systerochbror gives a non-empty string not equal to default response
        tests.append(['SoB 1',
                      '!lunch systerochbror', botplugin.test_nonempty_string])
        tests.append(['SoB 2',
                      '!lunch systerochbror', botplugin.test_not_equal, default_response])

        return tests


if __name__ == '__main__':
    from mockbot import mockbot
    from jantemessage import jantemessage
    
    bot = mockbot()
    
    p = lunchBotContainer(bot)
    print(p.parse(jantemessage('')))
