import datetime
import time
import re

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.plugintemplate import plugintemplate

class sclass(plugintemplate):
    def __init__(self, bot):
        myconfig = bot.getConfig('class')
        super().__init__(bot, 'Where is next class?')
        bot.addCommandListener(myconfig.get('command', 'class'), self.parse, strip_preamble=True,
            direct_reply=True)
    def getNextclass(self, date):
        
        
        file = open("assets/class/personal.ics", "r")
        test = file.read()
        test = test.replace('\n',' ').replace('\r','')
        # print test
        now = date
        dst = time.localtime().tm_isdst
        try:
            m = re.findall("BEGIN:VEVENT (.+?(?=END:))",test)
            output = ""
            stime2 = []
            nowtime = int(now.strftime("%H%M"))
            
            for courses in m:
                sdate = re.findall("DTSTART;VALUE=DATE-TIME:(\d+)", courses)
                if (sdate[0] == now.strftime("%Y%m%d")):
                
                # if (sdate[0] == now.strftime("%Y%m%d")):
                    name = re.findall("SUMMARY:(.+?(?=\())", courses)
                    sstrtime = re.findall("DTSTART;VALUE=DATE-TIME:\d+T(\d+)", courses)
                    estrtime = re.findall("DTEND;VALUE=DATE-TIME:\d+T(\d+)", courses)
                    location = re.findall("LOCATION:(.+?(?=S))", courses)
                    stime = int(sstrtime[0])/100 + 200
                    stime2.append(int(sstrtime[0])/100 + 200)
                    
                    # return str(int(stime)) +  " " + str(nowtime)
                    if (nowtime < int(stime) + 50):
                    
                        stime = stime / 100 
                        etime = int(estrtime[0])
                        etime = etime / 10000 + 2
                        time1 = (str(int(stime + 1 - dst)) + ":00" + " - " + str(int(etime + 1 - dst)) + ":00")
                        output += (name[0] + "\n" + time1 + "\n" + location[0] + "\n")

            if (nowtime > int(stime2[len(stime2) - 1]) + 50):
                output = "No more classes today"
        except:
            output = "No classes today"
             
        #return stime2
        return output



    def parse(self, message):
        today_time = datetime.datetime.now()
        tomorrow = today_time + datetime.timedelta(days=1)
        tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
        text = message.getText()
        print(text)
        if len(text) > 0:
            if text.startswith("--tomorrow"):
                return self.getNextclass(tomorrow)
        else:
            return self.getNextclass(datetime.datetime.now())
        
if __name__ == '__main__':
    from mockbot import mockbot
    from jantemessage import jantemessage
    
    bot = mockbot()
    bot.setConfig('class', 'command', 'class')
    
    p = imdb(bot)
    print(p.parse(jantemessage('buktalarkursen')))
