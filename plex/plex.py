"""
Written By Robin G
"""

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
import requests
import xml.etree.ElementTree as ET
import jantepastedb

class PlexPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(PlexPlugin, self).__init__(bot,
                                         command="plex", description="Search things on Robins Plex-server.")

        self._config = bot.getConfig()
        self.parser = JanteParser(description='Getting movies from plex', prog='plex', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument("search_terms", nargs="*", metavar="search terms",
                                 help="Words that will be searched.")
        self.parser.add_argument('-p', '--plot', action='store_true', required=False,
                                 help="Shows movie plot.")
        self.parser.add_argument('-t', '--tagline', action='store_true', required=False,
                                 help="Shows movie tagline.")
        self.parser.add_argument('-d', '--duration', action='store_true', required=False,
                                 help="Shows movie duration in minutes.")


    def paste(self, text, message):
        return self._bot.getService("paste").paste(text, message)

    def search(self, word, plot = False, tagline = False, duration = False):
        server_url = self._config["plex"]["serverUrl"]

        api_key = self._config["plex"]["apiKey"]

        xml = requests.get(f"{server_url}{api_key}").text
        root = ET.fromstring(xml)
        movies = {}
        entry = {}
        message = ""
        self.log(word)
        for video_tag in root.findall('Video'):
            if word.lower() in video_tag.get('title').lower():
                entry = {(video_tag.get('title')): {'name': str((video_tag.get('title'))),
                                                    'year': (" (" + str(video_tag.get('year')) + ")"),
                                                    'plot': str((video_tag.get('summary'))),
                                                    'tagline': str((video_tag.get('tagline'))), 'duration': str(
                        round(int(video_tag.get('duration')) / 1000 / 60)) + " minutes"}}
                movies.update(entry)
        for movie in movies:
            message += movies.get(movie).get('name') + movies.get(movie).get('year')
            if plot == True:
                message += " Plot: " + movies.get(movie).get('plot')
            if tagline == True:
                message += " Tagline: " + movies.get(movie).get('tagline')
            if duration == True:
                message += " Duration: " + movies.get(movie).get('duration')
            message += "\n"
        return message if message.strip() != "" else "Did not find anything with that name."

    def parse(self, message):
        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))

        search_terms = " ".join(args.search_terms)
        if args.help:
            return self.parser.format_help()
        if args.plot:
            return self.paste(self.search(search_terms, True), message)
        if args.tagline:
            return self.paste(self.search(search_terms, False, True), message)
        if args.duration:
            return self.paste(self.search(search_terms, False, False, True), message)


        return self.paste(self.search(search_terms), message)
