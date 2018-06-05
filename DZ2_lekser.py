import string.hexdigits

def isxdigit(self, znak):
    return znak.isdigit() or znak in string.hexdigits

def isidentifier(self, znak):
    return znak.isalpha() or znak.isdigit() or znak == '_'

def Lekser(kôd):
    lex = Tokenizer(kôd)

    for znak in iter(lex.čitaj, ''):
        if znak.isalpha or znak == '_':
            # onda je identifier
            lex.plus(str.isidentifier)
            yield lex.token(Tokeni.IDENTIFIER)
        elif znak.isdigit(): 
            # onda je dec ili hex
            if znak == '0': 
                sljedeći = lex.čitaj()
                if sljedeći == 'x' or sljedeći == 'X':
                    # onda je hex
                    lex.plus(str.isxdigit)
                    yield lex.token(Tokeni.HEKSADEKADSKI)
                else: lex.greška('očekujem x ili X')
            else:
                # onda je dec
                lex.zvijezda = lex.token(str.isdigit)
                yield lex.token(Tokeni.DECIMALNI)
        elif znak == '\' :
            sljedeći = lex.čitaj()
            if sljedeći in "ntvbrfa'\""
            yield lex.token(Tokeni.ESCAPE)

    else: yield lex.token(operator(AN, znak) or lex.greška())
