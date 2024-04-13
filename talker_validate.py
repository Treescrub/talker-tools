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
    tokens = None
    
    def __init__(self):
        self.tokens = []
    
    def lex(self, data):
        self.data = data
        self.data_index = 0
        
        while self.data_index < len(self.data):
            self.skip_nonprintable()
            
            if self.current_char() == '"':
                self.read_quoted()
                continue
            
            if self.current_char() in "{}()'":
                self.add_token(self.current_char())
                self.next_char()
                continue
            
            self.read_token()
        
    
    def skip_nonprintable(self):
        while self.data_index < len(self.data):
            if ord(self.current_char()) <= 32:
                self.next_char()
                continue
            
            if self.current_char() != '/':
                return
            if self.peek_next() != '/':
                return
            
            self.next_char()
            
            while self.data_index < len(self.data):
                if self.current_char() == '\n' or self.current_char() == '\0':
                    self.next_char()
                    break
                
                self.next_char()
    
    def read_quoted(self):
        self.next_char()
        
        start_index = self.data_index
        end_index = start_index
        
        while self.data_index < len(self.data):
            if self.current_char() == '"' or self.current_char() == '\0':
                end_index = self.data_index
                self.next_char()
                break
            
            self.next_char()
        
        self.add_token(self.data[start_index:end_index])
    
    def read_token(self):
        start_index = self.data_index
        end_index = len(self.data)
        
        while self.data_index < len(self.data):
            if ord(self.current_char()) <= 32:
                end_index = self.data_index
                break
            
            self.next_char()
        
        self.add_token(self.data[start_index:end_index])
    
    def add_token(self, value):
        self.tokens.append(value)
    
    def current_char(self):
        if self.data_index >= len(self.data):
            return None
    
        return self.data[self.data_index]
    
    def next_char(self):
        self.data_index += 1
    
        return self.current_char()
    
    def peek_next(self):
        if self.data_index >= len(self.data) - 2:
            return None
        
        return self.data[self.data_index + 1]


def main():
    file_contents = ""

    lexer = Lexer()
    lexer.lex(file_contents)
    
    parser = Parser(lexer.tokens)
    
    parser.parse()
    
    
if __name__ == "__main__":
    main()