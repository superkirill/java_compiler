import sys
from definitions import lexemes, key_words

class TScanner(object):
    """Scanner class"""
    def __init__(self, path, position=0):
        try:
            with open(path) as file:
                self.initial_text = file.read()
            print(self.initial_text)
        except Exception as FileNotFoundError:
            print("Specified file has not been found")
            return
        self.pointer = position
        self.line = 1
        self.indent = 1
        self.translations = dict()
        self.MAXLEN_IDENT = 100
        self.MAXLEN_INTCONST = 20

    def set_pointer(self, position):
        self.pointer = position

    def get_pointer(self):
        return self.pointer

    def get_location(self):
        position = self.pointer
        self.pointer = 0
        self.line = 1
        while self.pointer != position:
            lexeme = self.next_lexeme()
            if lexeme[1] == "TEnd":
                break
        self.pointer = position
        return self.line

    def print_error(self, message):
        print("\n\n\nError! %s" % message)
        print("Line: %d, position: %d\n\n\nTermination.\n\n\n" % (self.get_location(), self.indent))

        sys.exit(0)

    def next_lexeme(self):
        lex_type = None
        lex_end = self.pointer + 1
        sym = str(self.initial_text[self.pointer : lex_end])
        start = self.pointer
        while lex_type is None:
            # if self.pointer > 500:
            #     print("\'%s\'" % sym)
            #     sys.exit(1)
            if '0' <= sym <= '9':
                while '0' <= str(self.initial_text[lex_end:lex_end+1]) <= '9':
                    lex_end += 1
                if lex_end - self.pointer > self.MAXLEN_INTCONST:
                    lex_type = "Terr"
                else:
                    lex_type = "TIntegerConstant"
                sym = self.initial_text[self.pointer : lex_end]
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif 'a' <= sym <= 'z' or 'A' <= sym <= 'Z' or sym == '_':   
                while 'A' <= str(self.initial_text[lex_end:lex_end+1]) <= 'z' or\
                        '0' <= str(self.initial_text[lex_end:lex_end+1]) <= '9' or\
                        str(self.initial_text[lex_end:lex_end+1]) == '_':

                    lex_end += 1
                if lex_end - self.pointer > self.MAXLEN_IDENT:
                    # msg = "Identifier is too long"
                    # self.print_error(msg)
                    lex_type = "Terr"
                else:
                    lex_type = "TIdentifier"
                    sym = self.initial_text[self.pointer : lex_end]
                    if sym in key_words.keys():
                        lex_type = key_words[sym]
                    else:
                        lex_type = "TIdentifier"
                if lex_type is None:
                    lex_type = "TIdentifier"
                sym = self.initial_text[self.pointer : lex_end]
                start = self.pointer
                self.pointer = lex_end

            elif sym == "+":
                lex_type = "TAddition"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "-":
                lex_type = "TSubstraction"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "*":
                lex_type = "TMultiplication"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "%":
                lex_type = "TModulus"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "^":
                lex_type = "TBitwiseXor"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "(":
                lex_type = "TLeftParenthesis"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == ")":
                lex_type = "TRightParenthesis"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "{":
                lex_type = "TLeftBrace"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "}":
                lex_type = "TRightBrace"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == ";":
                lex_type = "TSemicolon"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == ".":
                lex_type = "TPeriod"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == ",":
                lex_type = "TComma"
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
            elif sym == "&":
                sym = str(self.initial_text[lex_end:lex_end+1])
                if sym != "&":
                    lex_type = "Terr"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
                else:
                    lex_end += 1
                    lex_type = "TLogicalAnd"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
            elif sym == "|":
                sym = str(self.initial_text[lex_end:lex_end+1])
                if sym != "|":
                    lex_type = "Terr"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
                else:
                    lex_end += 1
                    lex_type = "TLogicalOr"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
            elif sym == "!":
                sym = str(self.initial_text[lex_end:lex_end+1])
                if sym == "=":
                    lex_end += 1
                    lex_type = "TNotEqualTo"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
                else:
                    lex_type = "TLogicalNot"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
            elif sym == "=":
                sym = str(self.initial_text[lex_end:lex_end+1])
                if sym == "=":
                    lex_end += 1
                    lex_type = "TEqualTo"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
                else:
                    lex_type = "TAssign"
                    start = self.pointer
                    sym = str(self.initial_text[self.pointer : lex_end])
                    self.pointer = lex_end
                    lex_end += 1
            elif sym == " ":
                start = self.pointer
                self.pointer = lex_end
                lex_end += 1
                sym = str(self.initial_text[self.pointer : lex_end])           
            elif sym == '':
                lex_type = "TEnd"
                sym = "\\0"
            elif sym == "\n":
                self.line += 1
                self.pointer = lex_end
                start = self.pointer
                lex_end += 1
                self.indent = 1
                sym = str(self.initial_text[self.pointer : lex_end])
            elif sym == "\t":
                self.pointer = lex_end
                start = self.pointer
                lex_end += 1
                sym = str(self.initial_text[self.pointer : lex_end])
            elif sym == "/":
                sym = str(self.initial_text[lex_end:lex_end+1])
                if sym == "/":
                    while sym != "\n" and sym != '':
                        lex_end += 1
                        sym = str(self.initial_text[lex_end:lex_end+1])
                    self.pointer = lex_end
                    lex_end += 1
                elif sym == "*":
                    while True:
                        if sym == "":
                            lex_type = "TEnd"
                            sym = "\\0"
                            break
                        if sym == "*" and str(self.initial_text[lex_end:lex_end+1]) == "/":
                            self.pointer = lex_end + 1
                            lex_end += 2
                            sym = str(self.initial_text[self.pointer : lex_end])
                            break
                        else:    
                            if sym == "\n":
                                self.line += 1
                            self.pointer = lex_end
                            lex_end += 1
                            sym = str(self.initial_text[self.pointer : lex_end])
                else:
                    lex_type = "TDivision"
                    sym = str(self.initial_text[lex_end-1:lex_end])
                    start = self.pointer
                    self.pointer = lex_end
                    lex_end += 1
            else:
                self.pointer = lex_end
                lex_end += 1
                lex_type = "Terr"

        self.indent += (lex_end-1) - start
        # print(sym)
        return [sym,
                lex_type,
                lexemes[lex_type],
                self.line,
                start,
                lex_end-1
                ]