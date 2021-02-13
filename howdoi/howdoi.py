"""
Written By Robin G
"""

from plugins.parsingplugintemplate import parsingplugintemplate
from libs.janteparse import JanteParser, ArgumentParserError # pylint:disable=import-error
import jantepastedb
from howdoi import howdoi

class hdiPlugin(parsingplugintemplate):
    def __init__(self, bot):
        super(hdiPlugin, self).__init__(bot,
                                         command="howdoi", description="How to do things")

        self._config = bot.getConfig()
        self.parser = JanteParser(description='Get told how to do things', prog='howdoi', add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true', required=False,
                                 help="Shows this helpful message.")
        self.parser.add_argument("search_terms", nargs="*", metavar="search terms",
                                 help="Words that will be searched.")

    def paste(self, text, message):
        return self._bot.getService("paste").paste(text, message)

    def search(self, word):

        parser = howdoi.get_parser()
        args = vars(parser.parse_args(word.split(' ')))

        output = howdoi.howdoi(args)

        return output if output.strip() != "" else "Did not find anything containing that"

    def parse(self, message):
        try:
            args = self.parser.parse_args(message.getText().split(" "))
        except ArgumentParserError as error:
            return ArgumentParserError("\n{}".format(error))

        search_terms = " ".join(args.search_terms)
        if args.help:
            return self.parser.format_help()


        return self.paste(self.search(search_terms), message)
