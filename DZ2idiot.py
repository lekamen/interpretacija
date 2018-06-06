from pj import *
import re

# GRAMATIKA (puna)
# decimalni     -> 0 | [1-9][0-9]*
# separator     -> ( | ) | [ | ] | { | } | , | ;
# unarni_op     -> ! | ~ | - | *
# binarni_op    -> . | -> | * | / | % | + | - | << | >> |
#                  < | <= | >= | > | == | != | & | ^ | | |
#                  && | || | ? | :
# op_priruz     -> = | += | -= | *= | /= | %= | <<= | >>=
#               -> &= | ^= | |=
# postfix_op    -> -- | ++
# escape        -> \n | \t | \v | \b | \r | \f | \a |
#                  \\ | \' | \"
# identifier    -> [A-Za-z_][A-Za-z0-9_]*    
# broj          -> decimalni | heksadekadski
# heksadekadski -> 0[xX][0-9a-fA-F]+
# nchar         -> (normalni znak osim ")
# lchar         -> (normalni znak osim >)

#sve iznad je u Tokenima, ispod je za lexer
# library       -> <lchar*>
# schar         -> nchar | escape
# cchar         -> nchar | escape | " | \0
# string        -> "schar*"
# char          -> 'cchar'

class Tokeni(enum.Enum):
    #separatori
    OOTV, OZATV, UOTV, UZATV, VOTV, VZATV, ZAREZ, SEP = '()[]{},;'
    #unarni operatori
    USKL, TILDA, MINUS, ZVJ = '!~-*'
    #binarni operatori bez zvjezdice!!!
    TOCKA, STRELICA, SLASH, MOD, PLUS, LSHIFT, RSHIFT = '.', '->', '/', '%', '+', '<<', '>>'
    LESS, LESSEQ, GRTEQ, GRT, EQ, DISEQ, BITAND, BITEXCLOR, BITOR = '<', '<=', '>=', '>', '==', '!=', '&', '^', '|'
    LAND, LOR, CONDQ, CONDDOT = '&&', '||', '?', ':'
    #operatori pridruzivanja bez jednakosti!!!
    PLUSEQ, MINUSEQ, ZVJEQ, SLASHEQ, MODEQ, LSHIFTEQ, RSHIFTEQ, ASSIGN= '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '='
    ANDEQ, POTEQ, CRTAEQ = '&=', '^=', '|='
    #postfiksni operatori
    DECR, INCR = '--', '++'
    #escape sekvence
    NRED, NTAB, NVERTTAB, BACKSP, RET, FFEED, ALERT = '\n', '\t', '\v', '\b', '\r', '\f', '\a'
    QUOTE, DBLQUOTE, ESCSLASH = '\'', '\"', '\\'
    #komentari
    COMMENT, COM_BEGIN, COM_END = '//', '/*', '*/'
    class IDENTIFIER(Token):
        def vrijednost(self): 
            p = re.compile('^[A-Za-z_]\w*$')
            if (p.match(self.sadržaj) is None):
                raise RuntimeError("Neispravni identifikator")
            return str(self.sadržaj) #isprobati još?

    class DECIMALNI(Token):
        def vrijednost(self): return int(self.sadržaj)
    class HEKSADEKADSKI(Token):
        def vrijednost(self):
            p = re.compile('^0[xX][0-9a-fA-F]+$')
            if (p.match(self.sadržaj) is None):
                raise RuntimeError("Neispravan heksadekadski broj")
            return hex(self.sadržaj) #isprobati!!
    class CHRLIT(Token):
        def vrijednost(self):
            return self.sadržaj #testiraj jel 'znak'
    class STRLIT(Token):
        def vrijednost(self):
            return self.sadržaj#testiraj jel "string"
    class LIBLIT(Token):
        def vrijednost(self):
            return self.sadržaj#testiraj jel <string>


