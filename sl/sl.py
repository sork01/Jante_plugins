import requests
import urllib.parse
import json
from datetime import datetime

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error

#res = ""


class SlPlugin(parsingplugintemplate):
    """
    Plugin for echoing things.
    Works similar to echo in bash.
    """
    def __init__(self, bot):
        super(SlPlugin, self).__init__(bot,
                                         command="sl", description="Shows sl traveling directions, there are no useful arguments yet.")

        self.parser = JanteParser(description='Shows sl traveling directions\n No useful arguments yet.', prog='sl', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument('-a', '--arrival', type=str, default="", required=False,
                                 help="Set arrival time in format HH:MM")
        self.parser.add_argument('-s', '--start', type=str, default="", required=False,
                                 help="Set starting time in format HH:MM")
        self.parser.add_argument('-d', '--date', type=str, default="", required=False,
                                 help="Set date for arrival or departure in format YY-MM-DD")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")

    def getdirections(self, json):
        startnames = []
        destnames = []
        starttimes = []
        desttimes = []
        messageslist = []
        transportlist = []
        linelist = []
        if 'Trip' not in json:
            return "No trip found"
        trip = json['Trip']
        leglist = trip[0]['LegList']
        leg = leglist['Leg']
        for i in range(len(leg)):
            if leg[i]['type'] == 'WALK':
                continue
            origin = leg[i]['Origin']
            startnames.append(origin['name'])
            starttimes.append(origin['time'][:-3])
            destination = leg[i]['Destination']
            destnames.append(destination['name'])
            desttimes.append(destination['time'][:-3])
            if 'Messages' in leg[i]:
                messages = leg[i]['Messages']
                message = messages['Message']
                messageslist.append(message[0]['text'])
            if 'Product' in leg[i]:
                status = leg[i]['Product']
                transport = status['catOutL'].lower()
                transportlist.append(transport)
                linelist.append(status['line'])

        res = "Ta "
        for i in range(len(startnames)):
            res += (str(transportlist[i]) + "linje " + str(linelist[i]) + " från " + str(
                startnames[i]) + " som går kl " + str(starttimes[i]) + " som ankommer till " + destnames[i] + " kl " +
                    desttimes[i] + "\n")
            if i < len(startnames) - 1:
                res += "därefter "
        FMT = "%H:%M"
        tdelta = datetime.strptime(desttimes[len(desttimes) - 1], FMT) - datetime.strptime(starttimes[0], FMT)
        res += ("\nDen totala restiden är " + str(tdelta)[:-6] + " timmar och " + str(tdelta)[2:-3] + " minuter")
        return res

    def getids(self, startinput, destinationinput, time = "", arrival = 0, date = ""):

        if startinput == destinationinput:
            return "Can't have the same start and destination"
        urlstart = "https://api.sl.se/api2/typeahead.json?key=4bae1902a34444108f283cc47fe5ccd3&searchstring=" + startinput
        urldest = "https://api.sl.se/api2/typeahead.json?key=4bae1902a34444108f283cc47fe5ccd3&searchstring=" + destinationinput

        f = requests.get(urlstart)
        f2 = requests.get(urldest)

        startlist = json.loads(f.text)
        if len(startlist['ResponseData']) == 0:
            return "No startlocation found"
        start = (startlist['ResponseData'][0])
        startid = (start['SiteId'])
        destlist = json.loads(f2.text)
        if len(destlist['ResponseData']) == 0:
            return "No destination found"
        dest = (destlist['ResponseData'][0])
        destid = (dest['SiteId'])
        trip = "https://api.sl.se/api2/TravelplannerV3_1/trip.json?key=d6dcb0574b8b4487a47e38a7079f3866&originExtId=" + startid + "&destExtId=" + destid + "&time=" + str(time) + "&searchForArrival=" + str(arrival) + "&date=" + date
        print(trip)
        f3 = requests.get(trip)

        tripjson = json.loads(f3.text)
        #res += "Valda stationer är " + start['Name'] + " och " + dest['Name']
        return self.getdirections(tripjson)

    def parse(self, message):
        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        print(args.arrival)
        print(args.start)
        print(args.words)
        if args.help:
            return self.parser.format_help()
        if args.arrival:
            if args.date:
                return self.getids(args.words[0], args.words[1], args.arrival, 1, args.date)
            return self.getids(args.words[0], args.words[1], args.arrival, 1)
        if args.start:
            if args.date:
                return self.getids(args.words[0], args.words[1], args.start, 0, args.date)
            return self.getids(args.words[0], args.words[1], args.start, 0)
        if args.date:
            return self.getids(args.words[0], args.words[1], args.start, 0, args.date)
        else:
            return self.getids(args.words[0], args.words[1])



