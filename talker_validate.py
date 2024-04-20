import sys
import codecs


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
    line = 0
    column = 0
    
    def __init__(self):
        self.tokens = []
    
    def lex(self, data):
        self.data = data
        self.data_index = 0
        
        while self.data_index < len(self.data):
            self.skip_nonprintable()
            
            if self.current_char() is None:
                break
            
            if self.current_char() == '"':
                self.read_quoted()
                continue
            
            if self.current_char() in "{}()'":
                self.add_token(self.current_char(), (self.current_pos(), (self.line, self.column + 1)))
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
        start_pos = self.current_pos()
    
        self.next_char()
        
        start_index = self.data_index
        end_index = start_index
        
        while self.data_index < len(self.data):
            if self.current_char() == '"' or self.current_char() == '\0':
                end_index = self.data_index
                self.next_char()
                break
            
            self.next_char()
        
        self.add_token(self.data[start_index:end_index], (start_pos, self.current_pos()))
    
    def read_token(self):
        start_pos = self.current_pos()
    
        start_index = self.data_index
        end_index = len(self.data)
        
        while self.data_index < len(self.data):
            if ord(self.current_char()) <= 32:
                end_index = self.data_index
                break
            
            self.next_char()
        
        self.add_token(self.data[start_index:end_index], (start_pos, self.current_pos()))
    
    def add_token(self, value, range):
        self.tokens.append({"value": value, "range": range})
    
    def current_pos(self):
        return (self.line, self.column)
    
    def current_char(self):
        if self.data_index >= len(self.data):
            return None
    
        return self.data[self.data_index]
    
    def next_char(self):
        self.data_index += 1
        
        self.column += 1
        
        if self.current_char() == '\n':
            self.line += 1
            self.column = -1
    
        return self.current_char()
    
    def peek_next(self):
        if self.data_index >= len(self.data) - 2:
            return None
        
        return self.data[self.data_index + 1]


def main():
    if len(sys.argv) < 2:
        print("no file path")
        return
    
    if len(sys.argv) > 2:
        print("ignoring arguments")
    
    file_path = sys.argv[1]
    file_contents = ""
    
    try:
        with codecs.open(file_path, encoding="ascii") as file:
            file_contents = file.read()
    except UnicodeDecodeError as error:
        print(f"non-ascii character in file at indices {error.start}-{error.end}, stopping")
        return

    lexer = Lexer()
    lexer.lex(file_contents)

    parser = Parser(lexer.tokens)
    
    parser.parse()
    
    
if __name__ == "__main__":
    main()