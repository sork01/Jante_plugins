#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate

class imdb(parsingplugintemplate):
    def __init__(self, bot):
        self._config = bot.getConfig()
        super(imdb, self).__init__(bot, command=self._config['imdb']['command'], description="Get movie information from imdb and rotten tomatoes")

    def getRating(self, name, poster, plot):
        fullname = name.replace(" ", "_")
        url = "http://www.omdbapi.com/?t="+fullname+"&tomatoes=true"+"&apikey=f254e8c5"
        try:
            response = urllib.request.urlopen(url, timeout = 5.0).read().decode("utf-8")
        except Exception as e:
            self.log(str(e))
            fail = ("None or too many movies contains " + name)
            return fail
        jsonvalues = json.loads(response)
        if (plot == 1):
            try:
                title = jsonvalues["Title"]
                plot = jsonvalues["Plot"]
                s = ("The plot of " + title + " : " + plot)
                return s
            except Exception as e:
                self.log(str(e))
                return "Are you sure that movie exists?"
        if (poster == 1):
            try:
                title = jsonvalues["Title"]
                poster = jsonvalues["Poster"]
                s = ("Poster of " + title + " : " + poster)
                return s
            except Exception as e:
                self.log(str(e))
                return "Are you sure that movie exists?"
        else:
            rottendefined = False

            try:
                title  = jsonvalues["Title"]
                rating = jsonvalues["imdbRating"]
                genre = jsonvalues["Genre"]
                year = jsonvalues["Year"]
                actors = jsonvalues["Actors"]
                runtime = jsonvalues["Runtime"]
                for entry in jsonvalues['Ratings']:
                    if (entry['Source'] == 'Rotten Tomatoes'):
                        rotten = entry['Value']
                        rottendefined = True
                link = "https://www.imdb.com/title/" + jsonvalues["imdbID"]
                plot = jsonvalues["Plot"]
            except:
                return "Are you sure that movie exists?"

            # http://zetcode.com/python/fstring/
            import textwrap
            s = textwrap.dedent(f"""
                {title}
                IMDb rating: {rating}
                Genre: {genre}
                Year: {year}
                Actors: {actors}
                Runtime: {runtime}
                IMDb link: {link}

                {plot}
                """)

            if rottendefined:
                s += ("\nRotten Tomatoes user rating = " + rotten)

            return s

    def parse(self, message):
        text = message.getText()
        if len(text) > 0:
            if text.startswith("--poster"):
                return self.getRating(text[9:],1,0)
            if text.startswith("--plot"):
                return self.getRating(text[7:],0,1)
            else:
                return self.getRating(text,0,0)
        else:
            return "Need to input movie title"

if __name__ == '__main__':
    from mockbot import mockbot
    from jantemessage import jantemessage
    
    bot = mockbot()
    bot.setConfig('imdb', 'command', 'imdb')
    
    p = imdb(bot)
    print(p.parse(jantemessage('Star Wars')))
