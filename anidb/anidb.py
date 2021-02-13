
import random

from bs4 import BeautifulSoup
import urllib.request
import re
import numpy


if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
from libs.jantemessage import jantemessage

class AnidbPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(AnidbPlugin, self).__init__(bot,
                                         command="anidb", description="Searches anidb")
        self.parser = JanteParser(description='Searches anidb', prog='anidb', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")

    def anidb(self, searchword):
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        query = urllib.parse.quote(searchword)
        url = "https://anidb.net/search/fulltext/?adb.search=" + query + "&do.search=1&entity.animetb=1&field.titles=1"
        req = urllib.request.Request(url, headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        score = soup.find_all('td', {'class':'score'})
        name = soup.find_all('td', {'class':'relid'})
        link = re.findall(r'href="([^"]+)', str(soup.find_all('td', {'class':'relid'})))
        distance = 100
        count = 0
        index = 0
        for series in name:
            tmpdistance = self.levenshteinDistanceDP(series.text.lower(), searchword.lower()) 
            if tmpdistance < distance:
                distance = tmpdistance
                index = count
            count += 1
        if len(link) == 0:
            message = ("No anime found (" + searchword + ")")
        else:
            descNImg = self.aniDescImg(link[index])
            if descNImg[0] == "Adult":
                message = "Adult content you fucking hentai!"
            else:
                message = (name[index].text + ": Score: " + score[index].text + "\n\n" + descNImg[0] + "\n\n" + descNImg[1] )
        return message
        
    def aniDescImg(self, url):
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        url = ("https://anidb.net" + url)
        req = urllib.request.Request(url, headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        adult = soup.find('h1', {'class':'anime'}).text
        if adult == "Adult Content Warning":
            desc = "Adult"
            img = None
        else:
            desc = soup.find_all('div', {'class':'g_bubble g_section desc resized'})
            if len(desc) == 0:
                desc = ""
                image = soup.find('img', alt=True)
                img = image["src"]
            else:
                desc = desc[0].text
                image = soup.find('img', alt=True)
                img = image["src"]

        return [desc, img]
        
    def levenshteinDistanceDP(self, token1, token2):
        distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

        for t1 in range(len(token1) + 1):
            distances[t1][0] = t1

        for t2 in range(len(token2) + 1):
            distances[0][t2] = t2
            
        a = 0
        b = 0
        c = 0
        
        for t1 in range(1, len(token1) + 1):
            for t2 in range(1, len(token2) + 1):
                if (token1[t1-1] == token2[t2-1]):
                    distances[t1][t2] = distances[t1 - 1][t2 - 1]
                else:
                    a = distances[t1][t2 - 1]
                    b = distances[t1 - 1][t2]
                    c = distances[t1 - 1][t2 - 1]
                    
                    if (a <= b and a <= c):
                        distances[t1][t2] = a + 1
                    elif (b <= a and b <= c):
                        distances[t1][t2] = b + 1
                    else:
                        distances[t1][t2] = c + 1
        return distances[len(token1)][len(token2)]

    def parse(self, message):

        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        if args.help:
            return self.parser.format_help()
        else:
            return self.anidb(ans)
