import sys
import codecs


RESPONSE_TYPES = {"scene", "sentence", "speak", "response", "print"}
ROOT_COMMANDS = {"#include", "response", "enumeration", "criteria", "criterion", "rule"}


class Parser:
    tokens = None
    token_index = 0
    
    issues = None
    
    included_files = None
    enumerations = None
    response_groups = None
    criteria = None
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.issues = []
        
        self.included_files = set()
        self.enumerations = {}
        self.response_groups = {}
        self.criteria = {}

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
        
        self.next_token()
        
        self.included_files.add(self.current_token_value())
    
    def parse_response(self):
        if self.at_final_token():
            self.add_issue_at_current("expected response group name, but reached end of file")
            return
        
        self.next_token()
        group_name = self.current_token_value()
        
        while not self.at_final_token():
            self.next_token()
            lower_token = self.current_token_value().lower()
            
            if lower_token in ROOT_COMMANDS:
                self.previous_token()
                break
                
            if lower_token == '{':
                while self.has_tokens():
                    if self.at_final_token():
                        self.add_issue_at_current("expected response or command in response group body, but reached end of file")
                        return
                        
                    self.next_token()
                    lower_token = self.current_token_value().lower()
                    
                    if lower_token == '}':
                        break
                    if lower_token == "permitrepeats":
                        continue
                    if lower_token == "sequential":
                        continue
                    if lower_token == "norepeat":
                        continue
                    
                    self.parse_single_response()
                    
                break
            
            if self.parse_response_options():
                continue
            
            self.parse_single_response()
        
        self.response_groups[group_name] = {}
    
    def parse_single_response(self):
        if self.current_token_value().lower() not in RESPONSE_TYPES:
            self.add_issue_at_current(f"expected valid response type, got '{self.current_token_value()}' instead")
            return
        
        response_type = self.current_token_value().lower()
        
        self.next_token()
        response_value = self.current_token_value()
        
        while self.has_tokens_on_same_line():
            self.next_token()
            
            lower_token = self.current_token_value().lower()
            
            if self.parse_response_options():
                continue
            if lower_token == "weight":
                if self.at_final_token():
                    self.add_issue_at_current("expected weight value, but reached end of file")
                    return
                
                # TODO: parse weight
                self.next_token()
                continue
            if lower_token == "displayfirst":
                continue
            if lower_token == "displaylast":
                continue
            if lower_token == "fire":
                if self.at_final_token():
                    self.add_issue_at_current("expected targetname for 'fire', but reached end of file")
                    return
                
                self.next_token()
                target = self.current_token_value()
                
                if self.at_final_token():
                    self.add_issue_at_current("expected input name for 'fire', but reached end of file")
                    return
                
                self.next_token()
                input = self.current_token_value()
                
                if self.at_final_token():
                    self.add_issue_at_current("expected delay for 'fire', but reached end of file")
                    return
                
                self.next_token()
                delay = self.current_token_value()
                
                continue
            if lower_token == "then":
                if self.at_final_token():
                    self.add_issue_at_current("expected target for 'then', but reached end of file")
                    return
                
                self.next_token()
                target = self.current_token_value()
                
                if self.at_final_token():
                    self.add_issue_at_current("expected concept name for 'then', but reached end of file")
                    return
                
                self.next_token()
                concept = self.current_token_value()
                
                if self.at_final_token():
                    self.add_issue_at_current("expected contexts for 'then', but reached end of file")
                    return
                
                # TODO: concatenate tokens for stupidity
                while self.has_tokens_on_same_line():
                    self.next_token()
                
                if self.at_final_token():
                    self.add_issue_at_current("expected delay for 'then', but reached end of file")
                    return
                
                delay = self.current_token_value()
                
                continue
            
            self.add_issue_at_current(f"unknown response command '{self.current_token_value()}'")
    
    def parse_response_options(self):
        lower_token = self.current_token_value().lower()
    
        if lower_token == "predelay":
            if self.at_final_token():
                self.add_issue_at_current("expected predelay value, but reached end of file")
                return
            
            # TODO: parse interval
            self.next_token()
            return True
        if lower_token == "nodelay":
            # BUG!!!!! In the actual parser it skips a token!
            self.add_issue_at_current("nodelay has a bug that will cause weird behavior, do not use it!")
            return True
        if lower_token == "defaultdelay":
            return True
        if lower_token == "delay":
            if self.at_final_token():
                self.add_issue_at_current("expected delay value, but reached end of file")
                return
        
            # TODO: parse interval
            self.next_token()
            return True
        if lower_token == "speakonce":
            return True
        if lower_token == "noscene":
            return True
        if lower_token == "stop_on_nonidle":
            return True
        if lower_token == "odds":
            if self.at_final_token():
                self.add_issue_at_current("expected odds value, but reached end of file")
                return
        
            # TODO: parse odds
            self.next_token()
            return True
        if lower_token == "respeakdelay":
            if self.at_final_token():
                self.add_issue_at_current("expected respeakdelay value, but reached end of file")
                return
                
            # TODO: parse interval
            self.next_token()
            return True
        if lower_token == "weapondelay":
            if self.at_final_token():
                self.add_issue_at_current("expected weapondelay value, but reached end of file")
                return
                
            # TODO: parse interval
            self.next_token()
            return True
        if lower_token == "soundlevel":
            if self.at_final_token():
                self.add_issue_at_current("expected soundlevel value, but reached end of file")
                return
            
            # TODO: parse sound level
            self.next_token()
            return True
        
        return False
    
    def parse_criterion(self):
        if self.at_final_token():
            self.add_issue_at_current("expected criteria name, but reached end of file")
            return
            
        self.next_token()
        criterion_name = self.current_token_value()
        
        self.parse_single_criterion()
        
        self.criteria[criterion_name] = {}
    
    def parse_single_criterion(self):
        got_body = False
    
        while self.has_tokens_on_same_line() or not got_body:
            self.next_token()
            
            lower_token = self.current_token_value().lower()
            
            if lower_token in ROOT_COMMANDS:
                self.previous_token()
                break
            
            if lower_token == '{':
                got_body = True
                
                self.next_token()
                while self.has_tokens():
                    lower_token = self.current_token_value().lower()
                    
                    if lower_token == '}':
                        break
                    
                    # TODO: parse subcriteria
                    
                    self.next_token()
                    
                continue
            if lower_token == "required":
                continue
            if lower_token == "weight":
                if self.at_final_token():
                    self.add_issue_at_current("expected weight value, but reached end of file")
                    return
                
                # TODO: parse weight
                self.next_token()
                continue
            
            match_key = self.current_token_value()
            
            self.next_token()
            if self.at_final_token():
                self.add_issue_at_current("expected match value, but reached end of file")
                return
            
            match_value = self.current_token_value()
            
            got_body = True
    
    def parse_enumeration(self):
        if self.at_final_token():
            self.add_issue_at_current("expected enumeration name, but reached end of file")
            return
        
        self.next_token()
        name = self.current_token_value()
        
        if self.at_final_token():
            self.add_issue_at_current("expected enumeration body, but reached end of file")
            return
        
        self.next_token()
        if self.current_token_value() != '{':
            self.add_issue_at_current(f"expected opening bracket '{{' for enumeration body, got '{self.current_token_value()}' instead")
            return
        
        keys = {}
        
        self.next_token()
        while self.has_tokens():
            if self.current_token_value() == '}':
                break
            
            key = self.current_token_value()
            
            if self.at_final_token():
                self.add_issue_at_current("expected value for key, but reached end of file")
                return
            
            self.next_token()
            value = self.current_token_value()
            
            keys[key] = value
            
            if self.at_final_token():
                self.add_issue_at_current("expected more enumerations, but reached end of file")
                return
            
            self.next_token()
        
        if not self.has_tokens():
            self.add_issue_at_current(f"expected ending bracket '}}' for enumeration body, but reached end of file")
            return
        
        self.enumerations[name] = keys
    
    def parse_rule(self):
        if self.at_final_token():
            self.add_issue_at_current("expected rule name, but reached end of file")
            return
        
        self.next_token()
        
        rule_name = self.current_token_value()
        
        if self.at_final_token():
            self.add_issue_at_current("expected opening bracket '{' for rule body, but reached end of file")
            return
            
        self.next_token()
        
        if self.current_token_value() != '{':
            self.add_issue_at_current(f"expected opening bracket '{{' for rule body, got '{self.current_token_value()}' instead")
            return
        
        while self.has_tokens():
            if self.at_final_token():
                self.add_issue_at_current("expected rule content, but reached end of file")
                return
        
            self.next_token()
        
            lower_token = self.current_token_value().lower()
            
            if lower_token == '}':
                break
            
            if lower_token == "matchonce":
                continue
            if lower_token == "applycontexttoworld":
                continue
            if lower_token == "applycontext":
                if self.at_final_token():
                    self.add_issue_at_current("expected context value, but reached end of file")
                    return
                    
                # TODO: handle context storing
                self.next_token()
                continue
            if lower_token == "response":
                while self.has_tokens_on_same_line():
                    self.next_token()
                    
                    # TODO: store response data
                continue
            if lower_token == "criteria" or lower_token == "criterion":
                while self.has_tokens_on_same_line():
                    self.next_token()
                    
                    # TODO: store criteria data
                continue
            
            # inline criteria
            self.previous_token()
            
            self.parse_single_criterion()
    
    def at_final_token(self):
        return self.token_index == len(self.tokens) - 1
    
    def has_tokens_on_same_line(self):
        if not self.has_tokens() or self.at_final_token():
            return False
        
        # tokens cannot span multiple lines, so check current token start and next token start
        ((current_line, _), (_, _)) = self.current_token()["range"]
        ((next_line, _), (_, _)) = self.peek_next_token()["range"]
        
        return current_line == next_line
        
    
    def has_tokens(self):
        return self.token_index < len(self.tokens)
    
    def next_token(self):
        self.token_index += 1
        
        return self.current_token()
    
    def previous_token(self):
        if self.token_index <= 0:
            return None
        
        self.token_index -= 1
        
        return self.current_token()
    
    def peek_next_token(self):
        if self.token_index >= len(self.tokens) - 1:
            return None
        
        return self.tokens[self.token_index + 1]
    
    def current_token_value(self):
        return self.current_token()["value"]
    
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
    
    print_includes(parser)
    print_enums(parser)
    print_response_groups(parser)
    print_criteria(parser)
    
    print_issues(parser)


def print_includes(parser):
    print()
    print(f"{len(parser.included_files)} included scripts")
    if len(parser.included_files):
        print(f"Included scripts: {', '.join(parser.included_files)}")


def print_enums(parser):
    print()
    print(f"{len(parser.enumerations)} enumerations")
    if len(parser.enumerations):
        print(f"Enumeration names: {', '.join(parser.enumerations.keys())}")


def print_response_groups(parser):
    print()
    print(f"{len(parser.response_groups)} response groups")
    if len(parser.response_groups):
        print(f"Response group names: {', '.join(parser.response_groups.keys())}")


def print_criteria(parser):
    print()
    print(f"{len(parser.criteria)} criteria")

def print_issues(parser):
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