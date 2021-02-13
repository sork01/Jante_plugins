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

class KanaPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(KanaPlugin, self).__init__(bot,
                                         command="kana", description="Translates English to japanese kana")

        self.parser = JanteParser(description='Translates English to japanese kana', prog='kana', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")
                                 
    def kana(self, searchword):
        query = urllib.parse.quote(searchword)
        HEADER = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
        url = "https://www.sljfaq.org/cgi/e2k.cgi?word=" + query
        req = urllib.request.Request(url, headers=HEADER)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        kana = soup.find("td", class_="katakana-string").text
        return kana.strip()
        
    def parse(self, message):

        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        if args.help:
            return self.parser.format_help()
        else:
            return self.kana(ans)


