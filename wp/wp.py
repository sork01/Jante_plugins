"""
Written By Robin G
"""

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
import jantepastedb
import wikipedia as wk

class WpPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(WpPlugin, self).__init__(bot,
                                         command="wp", description="Get things from wikipedia")

        self._config = bot.getConfig()
        self.parser = JanteParser(description='Get things from wikipedia', prog='wp', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument("search_terms", nargs="*", metavar="search terms",
                                 help="Words that will be searched.")
        self.parser.add_argument('-e', '--english', action='store_true', required=False,
                                 help="English wikipedia.")

    def paste(self, text, message):
        return self._bot.getService("paste").paste(text, message)

    def search(self, word, lang):
        wk.set_lang(lang)
        message = ""
        try:
            page = wk.page(word)
        except wk.exceptions.DisambiguationError as e:
            return "Did not find anything with that name."
        except wk.exceptions.PageError as e:
            e
            return "Did not find anything with that name."
        message += wk.summary(word)
        return message if message.strip() != "" else "Did not find anything with that name."

    def parse(self, message):
        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))

        search_terms = " ".join(args.search_terms)
        if args.help:
            return self.parser.format_help()
        if args.english:
            return self.paste(self.search(search_terms, "en"), message)


        return self.paste(self.search(search_terms, "sv"), message)
