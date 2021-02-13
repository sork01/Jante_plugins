#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import random
import requests
import re
import urllib.parse

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error

imageList = []


class google(parsingplugintemplate):

    def __init__(self, bot):
        super(google, self).__init__(bot,
                                         command="google", description="Generates Google search queries.")

        self.parser = JanteParser(description='Searches Google', prog='google', add_help=False)
        self.parser.add_argument('-n', '--results', type=int, default=1, required=False,
                                 help="Amount of results from 1 to 100")
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument('-l', '--lucky', action='store_true', required=False,
                                 help="Displays first result.")
        self.parser.add_argument('-i', '--image', action='store_true', required=False,
                                 help="Google Image Search.")
        self.parser.add_argument('-r', '--random', action='store_true', required=False,
                                 help="Gives a random Google Search.")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")


    def gislink(self, searchword, N, random=False):
        HEADER = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"}

        split_query = searchword.split()
        split_query = '+'.join(split_query)
        url = "https://www.google.co.in/search?q=" + split_query + "&tbm=isch"
        soup = BeautifulSoup(requests.get(url, headers=HEADER).text, 'html.parser')
        imageList = re.findall(r".+(https:.+.jpg)", soup.text[-100000:])
        if random:
            message = "Searchword: " + searchword + "\n"
        else:
            message = ""

        if len(imageList) == 0:
            return "No match for searchword " + searchword
        else:
             message += imageList[0] + '\n'
        message = message[:-1]
        return message

    def parse(self, message):
        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        if args.help:
            return self.parser.format_help()
        if args.results < 1 or args.results > 100:
            return (str(args.results) + " is not a valid result")
        if args.lucky:
            if args.image:
                return self.gislink(ans, args.results)
            elif args.random:
                words = self._bot.getService("ngramkeeper").getDictionary()
                longwords = list(filter(lambda word: len(word) > 5, words))
                ans = random.choice(longwords)
                querystring = urllib.parse.urlencode({'q': ans, 'btnI': '1'})
                return 'https://www.google.com/search?{}'.format(querystring)
            else:
                querystring = urllib.parse.urlencode({'q': ans, 'btnI': '1'})
                return 'https://www.google.com/search?{}'.format(querystring)
        if args.random:
            if args.image:
                words = self._bot.getService("ngramkeeper").getDictionary()
                longwords = list(filter(lambda word: len(word) > 5, words))
                ans = random.choice(longwords)
                return self.gislink(ans, args.results, True)
            else:
                words = self._bot.getService("ngramkeeper").getDictionary()
                longwords = list(filter(lambda word: len(word) > 5, words))
                ans = random.choice(longwords)
                querystring = urllib.parse.urlencode({'q': ans})
                return 'https://www.google.com/search?{}'.format(querystring)
        if args.image:
            return self.gislink(ans, args.results)
        else:
            querystring = urllib.parse.urlencode({'q': ans})
            return 'https://www.google.com/search?{}'.format(querystring)


if __name__ == '__main__':
    from mockbot import mockbot
    from jantemessage import jantemessage

    bot = mockbot()

    p = google(bot)
    print(p.parse(jantemessage('')))
    print(p.parse(jantemessage('--quote')))
    print(p.parse(jantemessage('--quote Albert Einstein')))
