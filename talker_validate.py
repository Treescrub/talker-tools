import sys


class Parser:
    tokens = None
    current_token = 0
    
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        pass
    
    def parse_rule(self):
        pass


class Lexer:
    data = None
    tokens = None
    
    def __init__(self):
        self.tokens = []
    
    def lex(self, data):
        self.data = data


def main():
    file_contents = ""

    lexer = Lexer()
    lexer.lex(file_contents)
    
    parser = Parser(lexer.tokens)
    
    parser.parse()
    
    
if __name__ == "__main__":
    main()