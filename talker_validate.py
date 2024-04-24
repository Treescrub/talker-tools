import sys
import codecs


class Parser:
    tokens = None
    token_index = 0
    
    issues = None
    
    included_files = None
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.included_files = set()
        self.issues = []

    def parse(self):
        while self.has_tokens():
            lower_token = self.current_token()["value"].lower()
            
            if lower_token == "#include":
                self.parse_include()
            elif lower_token == "response":
                self.parse_response()
            elif lower_token == "criterion" or lower_token == "criteria":
                self.parse_criterion()
            elif lower_token == "rule":
                self.parse_rule()
            elif lower_token == "enumeration":
                self.parse_enumeration()
            else:
                print(f"unknown token: '{lower_token}'")
            
            self.next_token()
        
        print("finished parsing!")
    
    def parse_include(self):
        if not self.peek_next_token():
            self.add_issue_at_current("expected script name to include, but reached end of file")
            return
        
        self.included_files.add(self.next_token()["value"])
    
    def parse_response(self):
        pass
    
    def parse_single_response(self):
        pass
    
    def parse_criterion(self):
        pass
    
    def parse_single_criterion(self):
        pass
    
    def parse_enumeration(self):
        pass
    
    def parse_rule(self):
        pass
    
    def has_tokens(self):
        return self.token_index < len(self.tokens)
    
    def next_token(self):
        self.token_index += 1
        
        return self.current_token()
    
    def peek_next_token(self):
        if self.token_index >= len(self.tokens) - 1:
            return None
        
        return self.tokens[self.token_index + 1]
    
    def current_token(self):
        if not self.has_tokens():
            return None
        
        return self.tokens[self.token_index]

    def add_issue_at_current(self, description):
        self.issues.append((self.current_token()["range"], description))


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
    
    print()
    if len(parser.included_files):
        print(f"Included scripts: {', '.join(parser.included_files)}")
    else:
        print("No included scripts")
    
    print()
    if len(parser.issues):
        print("Issues:")
        for (range, description) in parser.issues:
            (start_pos, end_pos) = range
            (start_line, start_column) = start_pos
            
            print(f"line {start_line + 1}, column {start_column + 1}: {description}")
    else:
        print("No issues")
    
    
if __name__ == "__main__":
    main()