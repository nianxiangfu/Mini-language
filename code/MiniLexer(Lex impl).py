import sys
import ply.lex as lex
import os

def pre_processing(file_name):
    def check(item):
        # 原则：保留空格的作用是为了区分两个标识符
        idx, char = item
        if not char.isspace():
            return True
        else:
            _last = line[idx-1]
            _next = line[idx+1]
            if (_last.isalnum() or _last.isalpha() or _last == "_") and \
                (_next.isalnum() or _next.isalpha() or _next == "_"):
                return True
        return False
            
    line_map = dict()
    new_file_name = "tmp_" + file_name
    with open(file_name, "r", encoding="utf-8") as fp:
        nfp = open(new_file_name, "w", encoding="utf_8")
        line = fp.readline()
        cur_old_line = cur_new_line = 1
        while line:
            # 消除回车
            if line[-1] == "\n":
                line = line[:-1]
            # 消除注释
            single_com_idx = line.find("#")
            if single_com_idx != -1:
                line = line[0:single_com_idx]
            # 消除前后的空字符
            line.strip()
            if len(line) == 0:
                line = fp.readline()
                cur_old_line += 1
                continue
            # 消除行内的多余空格
            line = ' '.join(line.split()) # 多个空格合并成一个空格
            newline = "".join([x[1] for x in list(filter(check, enumerate(line, 0)))])
            newline += "\n"
            nfp.write(newline)
            line_map[cur_new_line] = cur_old_line
            cur_new_line += 1
            line = fp.readline()
            cur_old_line += 1
        nfp.close()         
    return new_file_name, line_map

type2val = {
    "id":0, "number":1, "{":2, "}":3, "=":4, "+":5, "-":6, "*":7, "/":8, "%":9,
    "eq":10, "neq":11, "<":12, "le":13, ">":14, "ge":15, "and":16, "or":17, "!":18, "[":19,
    "]":20, "(":21, ")":22, ",":23, ";":24, "#":25, "return":26, "false":27, "true":28, "begin":29,
    "end":30, "if":31, "continue":32, "else":33, "while":34, "program":35, "func":36, "const":37,
    "var":38, "break":39
}

def MiniLexer(line_map):
    literals = "+-*/%=<>![](),;#{}"   # 18
    
    reserved = ["false", "true", "begin","end", "if", "continue", "else", "while", "program", "func",
                "const", "var", "return", "break"]   # 14
    
    tokens = ["id", "number", "eq", "neq", "le", "ge", "and", "or"] + reserved  # 8 + 14

    num_table = []
    sym_table = []
    t_ignore = ' \t'
    # Regular expression rules for simple tokens
    t_eq = r"=="
    t_neq = r"!="
    t_le = r"<="
    t_ge = r">="
    t_and = r"&&"
    t_or = r"\|\|"
    
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_error(t):
        print(f"Illegal character '{t.value[0]}' at row:{line_map[t.lexer.lineno]}")
        t.lexer.skip(1)
    
    def number_lookup(value):
        try:
            idx = num_table.index(value)
        except ValueError:
            num_table.append(value)
            idx = len(num_table) - 1
        return idx

    def symble_lookup(value):
        try:
            idx = sym_table.index(value)
        except ValueError:
            sym_table.append(value)
            idx = len(sym_table) - 1
        return idx

    def t_id(t):
        r"[a-zA-Z_][0-9a-zA-Z_]*"
        if t.value in reserved: # check for reserved words
            t.type = t.value
            t.value = (t.value, reserved.index(t.value))
        else:
            t.type = "id"
            t.value = (t.value, symble_lookup(t.value))
        return t
    
    def t_number(t):
        r"[\+-]*\d+(\.\d+)?"
        if t.value.find(".") < 0:
            t.value = int(t.value)
        else:
            t.value = float(t.value)
        t.value = (t.value, number_lookup(t.value))    
        return t
    
    return lex.lex()

class Token:
    def __init__(self, type, type_no, value):
        self.type = type
        self.type_no = type_no
        self.value = value
        
    def __str__(self):
        if isinstance(self.value, tuple):
            return f"<{self.type}({self.type_no}), {self.value[0]}({self.value[1]})>"
        else:
            return f"<{self.type}({self.type_no}), {self.value}>"
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        src_file = os.path.basename(sys.argv[1])
    else:
        src_file = "test_neg.mini"
    tmp_src_file, line_map = pre_processing(src_file)
    mini_lexer = MiniLexer(line_map)
    with open(tmp_src_file, "r", encoding="utf-8") as fp:
        src_code = fp.read()
        mini_lexer.input(src_code)
        token = mini_lexer.token()
        while token:
            print(Token(token.type, type2val[token.type], token.value))
            token = mini_lexer.token()