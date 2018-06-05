# GRAMATIKA (puna)
# identifier    -> [A-Za-z_][A-Za-z0-9_]* LEX
# broj          -> decimalni | heksadekadski LEX
# decimalni     -> 0 | [1-9][0-9]* LEX
# heksadekadski -> 0[xX][0-9a-fA-F]+ LEX
# string        -> "schar*"
# char          -> 'cchar'
# library       -> <lchar*>
# schar         -> nchar | escape
# cchar         -> nchar | escape | " | \0
# nchar         -> (normalni znak osim ")
# lchar         -> (normalni znak osim >)
# escape        -> \n | \t | \v | \b | \r | \f | \a |
#                  \\ | \' | \" LEX
# separator     -> ( | ) | [ | ] | { | } | , | ;
# unarni_op     -> ! | ~ | - | * LEX
# binarni_op    -> . | -> | * | / | % | + | - | << | >> |
#                  < | <= | >= | > | == | != | & | ^ | | |
#                  && | || | ? | :
# op_priruz     -> = | += | -= | *= | /= | %= | <<= | >>=
#               -> &= | ^= | |=
# postfix_op    -> -- | ++
