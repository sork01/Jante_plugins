#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import mechanize
import re
import random

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
from libs.jantemessage import jantemessage

class ArraksPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(ArraksPlugin, self).__init__(bot,
                                         command="arraks", description="gets anagrams from arraks.fi")
        self.parser = JanteParser(description='Gets anagrams from arraks.fi', prog='arraks', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument('-a', '--all', action='store_true', required=False,
                                 help="Gives all found anagrams.")
        self.parser.add_argument('-l', '--language', type=str, default="sw", required=False,
                                 help="Choose language to get the anagram in, languages being en,fi,no,da,fr,ge,du,la and sw")
        self.parser.add_argument('-n', '--mwords', type=int, default=0, required=False,
                                 help="Max number of words in anagram, from 1 to 8")
        self.parser.add_argument("words", nargs="*",
                                 help="The search words")

    def arraks(self, word, N, lang, all=False):
        if N == 0:
            if len(word.split(" ")) < 2:
                N = 2
            else:
                N = len(word.split(" ")) 
        br = mechanize.Browser()
        br.set_handle_robots(False)
        response = br.open("https://www.arrak.fi/sv/ag")
        response.encoding = "utf-8"
        br.form = list(br.forms())[0]
        #word = word.encode('utf-8')
        br["sourcetext"] = word.encode('windows-1252')
        br["maxword"] = [str(N)]
        languages = ["Swedish", "English", "Finnish", "Norwegian", "Danish", "French", "German", "Dutch", "Latin"]
        for language in languages:
            if lang.lower() == language[:2].lower():
                chlang = language
                break
            else:
                chlang = "Swedish"
        br["lang"] = [chlang]
        resp = br.submit().read().decode('windows-1252')
        resp1 = str(resp)[2:-1]
        resp1 = resp1.replace("\n","    ")
        print(resp1)
        res = re.findall(r'"no">([^<]+)', resp1)
        res =(res[0].replace("\\n","     "))
        res =(res[:-4])
        res = re.split("     |    |   ", res)
        res = [x.strip() for x in res if x.strip()]
        res = list(filter(None, res))
        result = []
        
        for anagram in res:
            if sorted(re.split(r'\s+', word.lower())) != sorted(re.split(r'\s+', anagram.lower())):
                result.append(anagram)
                
        message = ""
        if len(result) == 0:
            message = "No anagram found"
        else:
            if all:
                for answer in result:
                    message += (answer + ", ")
                message = message[:-2]
            else:
                message = result[random.randint(0, len(result)-1)]
        return message
        
    def parse(self, message):

        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))
        ans = " ".join(args.words)
        if args.help:
            return self.parser.format_help()
        if args.all:
            return self.arraks(ans, args.mwords, args.language, True)
        else:
            return self.arraks(ans, args.mwords, args.language)
    
