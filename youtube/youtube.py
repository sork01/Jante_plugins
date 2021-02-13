
import random

from bs4 import BeautifulSoup
import urllib.request
import re


if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
from libs.jantemessage import jantemessage

class YoutubePlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(YoutubePlugin, self).__init__(bot,
                                         command="youtube", description="Searches youtube")

        self.parser = JanteParser(description='Searches youtube', prog='youtube', add_help=False)
        self.parser.add_argument('-n', '--results', type=int, default=1, required=False,
                                 help="Amount of results from 1 to 20")
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument('-r', '--random', action='store_true', required=False,
                                 help="Gives a random youtube link.")
        self.parser.add_argument('-s', '--streaming', action='store_true', required=False,
                                 help="Check if anyone is streaming.")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")


        
    def ytstreaming(self):
        url = ["https://www.youtube.com/channel/UCRU8PSSNf8n_68UZ1iXyr3A", "https://www.youtube.com/user/lurlurlur", "https://www.youtube.com/user/FxH1337", "https://www.youtube.com/channel/UCM9th0j-83uvnP8yfVkqEYw"] 
        message = ""
        for channel in url:
            req = urllib.request.Request(channel)
            req.add_header("Accept-Language", "en-US,en;q=0.5")
            response = urllib.request.urlopen(req)
            html = response.read()
            live = re.findall("(text\":\"LIVE)", str(html))
            if len(live) == 0:
                message += ""
                #print(channel + " is empty")
            else:
                if "68UZ1iXyr3A" in channel or "83uvnP8yfVkqEYw" in channel:
                    name = "Sork: "
                elif "FxH1337" in channel:
                    name = "Felix: "
                else:
                    name = "Lur: "
                link = re.findall("watch\?v=([A-Za-z0-9-_]*)", str(html))
                title = self.yt("https://www.youtube.com/watch?v=" + link[0])
                message += name + title + " https://www.youtube.com/watch?v=" + link[0] + "\n"
        if message == "":
            return "No one is streaming atm"
        else:
            return message

    def yt(self, yturl):
        url = yturl
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find("meta",  {"name":"title"})
        title = title["content"]
        message = ""
        if len(title) == 0:
            message += ("There is no such video")
        else:
            message += str(title)

        return message

    def ytlink(self, searchword, N, random = False):
        query = urllib.parse.quote(searchword)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        ytlist = []
        i = 1
        video = re.findall(r'videoIds":\["([^"]+)', soup.text)
        #title = re.findall(r'title":{"runs":\[{"text":"([^"]+)', soup.text)
            #ytlist.append(str(youtuber) + ": " + vid['title'] + ' https://www.youtube.com' + vid['href'])
        ytlist.append(self.yt('https://www.youtube.com/watch?v=' + video[0]) + ' https://www.youtube.com/watch?v=' + video[0])
            #i = i + 1
        ytlist = ytlist[0:N]
        if random:
            message = "Searchword: " + searchword + "\n"
        else:
            message = ""
        for link in ytlist:
            message += link + '\n'
        message = message[:-1]
        if message == "":
            return "No match for searchword " + searchword
        else:
            return message

    def parse(self, message):

        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        if args.help:
            return self.parser.format_help()
        if args.streaming:
            return self.ytstreaming()
        if args.results < 1 or args.results > 20:
            return (str(args.results) + " is not a valid result")
        if args.random:
            words = self._bot.getService("ngramkeeper").getDictionary()
            longwords = list(filter(lambda word: len(word) > 5, words))
            ans = random.choice(longwords)
            return self.ytlink(ans, args.results, True)
        else:
            return self.ytlink(ans, args.results)


