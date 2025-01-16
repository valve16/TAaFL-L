import sys
import re

class Token:
    def __init__(self, type_, lexeme, line, column):
        self.type = type_
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __str__(self):
        return f"{self.type} ({self.line}, {self.column}) \"{self.lexeme}\""

class PascalLexer:
    KEYWORDS = {
        "array": "ARRAY",
        "begin": "BEGIN",
        "else": "ELSE",
        "end": "END",
        "if": "IF",
        "of": "OF",
        "or": "OR",
        "program": "PROGRAM",
        "procedure": "PROCEDURE",
        "then": "THEN",
        "type": "TYPE",
        "var": "VAR"
    }

    OPERATORS = {
        "*": "MULTIPLICATION",
        "+": "PLUS",
        "-": "MINUS",
        "/": "DIVIDE",
        ";": "SEMICOLON",
        ",": "COMMA",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        "[": "LEFT_BRACKET",
        "]": "RIGHT_BRACKET",
        "=": "EQ",
        ">": "GREATER",
        "<": "LESS",
        "<=": "LESS_EQ",
        ">=": "GREATER_EQ",
        "<>": "NOT_EQ",
        ":": "COLON",
        ":=": "ASSIGN",
        ".": "DOT"
    }

    def __init__(self, input_file):
        self.input_file = open(input_file, 'r', encoding='utf-8')
        self.current_line = 0
        self.current_column = 0
        self.buffer = ""
        self.eof = False

    def close(self):
        self.input_file.close()

    def read_next_line(self):
        self.buffer = self.input_file.readline()
        # self.buffer = self.buffer.replace("\u00A0", " ")

        if not self.buffer:  # EOF
            self.eof = True
            self.buffer = ""
        else:
            self.current_line += 1
        self.current_column = 1

    def next_token(self):
        while not self.eof or self.buffer:
            if not self.buffer:
                self.read_next_line()
                if self.eof:
                    return None

            # Пропуск пробелов
            while self.buffer and self.buffer[0].isspace():
                self.buffer = self.buffer[1:]
            #print(self.buffer)
            if not self.buffer:  # Если строка пуста после обрезки
                continue

            self.current_column += len(self.buffer) - len(self.buffer.lstrip())

            # Линейный комментарий
            if self.buffer.startswith("//"):
                match = re.match(r"//.*", self.buffer)
                lexeme = match.group(0) if match else ""
                token = Token("LINE_COMMENT", lexeme, self.current_line, self.current_column)
                self.buffer = self.buffer[len(lexeme):]
                self.current_column += len(lexeme)
                return token

            # Блочный комментарий
            if self.buffer.startswith("{"):
                comment_lines = []
                start_line = self.current_line
                start_column = self.current_column

                while True:
                    end_index = self.buffer.find("}")
                    if end_index != -1:  # Закрытие найдено в текущей строке
                        comment_lines.append(self.buffer[:end_index + 1])
                        self.buffer = self.buffer[end_index + 1:]
                        self.current_column += end_index + 1
                        break
                    else:  # Закрытие не найдено в текущей строке
                        comment_lines.append(self.buffer)
                        self.read_next_line()
                        if self.eof:
                            raise SyntaxError(f"Unclosed block comment starting at line {start_line}.")

                lexeme = "".join(comment_lines)
                token = Token("BLOCK_COMMENT", lexeme, start_line, start_column)
                return token

            # Строковый литерал
            if self.buffer.startswith("'"):
                match = re.match(r"'(.*?)'", self.buffer)
                if match:
                    lexeme = match.group(0)
                    token = Token("STRING", lexeme, self.current_line, self.current_column)
                    self.buffer = self.buffer[len(lexeme):]
                    self.current_column += len(lexeme)
                    return token
                else:
                    raise SyntaxError(f"Unclosed string literal at line {self.current_line}.")

            # Идентификатор или ключевое слово
            match = re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", self.buffer)
            if match:
                lexeme = match.group(0)
                token_type = self.KEYWORDS.get(lexeme.lower(), "IDENTIFIER")
                token = Token(token_type, lexeme, self.current_line, self.current_column)
                self.buffer = self.buffer[len(lexeme):]
                self.current_column += len(lexeme)
                return token

            # Целое число или вещественное число
            match = re.match(r"\d+(\.\d+)?", self.buffer)
            if match:
                lexeme = match.group(0)
                token_type = "FLOAT" if "." in lexeme else "INTEGER"
                token = Token(token_type, lexeme, self.current_line, self.current_column)
                self.buffer = self.buffer[len(lexeme):]
                self.current_column += len(lexeme)
                return token

            # Операторы и разделители
            for op, token_type in sorted(self.OPERATORS.items(), key=lambda x: -len(x[0])):
                if self.buffer.startswith(op):
                    token = Token(token_type, op, self.current_line, self.current_column)
                    self.buffer = self.buffer[len(op):]
                    self.current_column += len(op)
                    return token

            # Некорректный символ
            bad_char = self.buffer[0]
            token = Token("BAD", bad_char, self.current_line, self.current_column)
            self.buffer = self.buffer[1:]
            self.current_column += 1
            return token

        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python PascalLexer.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # input_file = "in.txt"
    # output_file = "out.txt"
    lexer = PascalLexer(input_file)

    with open(output_file, 'w') as output:
        while True:
            token = lexer.next_token()
            if token is None:
                break
            print(token)
            output.write(str(token) + '\n')

    lexer.close()

if __name__ == "__main__":
    main()
