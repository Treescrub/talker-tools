# Parsing notes

Uses `CVEngineServer::ParseFile` to parse tokens.

### CVEngineServer::ParseFile

Wrapper for `COM_ParseFile`, which is a wrapper for `COM_Parse`.

### COM_Parse

* Seems to be ASCII only

#### Steps

1. Skips all non-printable chars and line comments.
2. If the current char is a double quote (`"`) read all chars into token until null terminator or second double quote is encountered, then return token.
3. If the current char is in the set of `{}()'` chars, store current char in token and return.
4. Read and store chars into token until a non-printable char is encountered.
5. Return token.