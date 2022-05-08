import os

type2val = {
    "id":0, "number":1, "{":2, "}":3, "=":4, "+":5, "-":6, "*":7, "/":8, "%":9,
    "==":10, "!=":11, "<":12, "<=":13, ">":14, ">=":15, "&&":16, "||":17, "!":18, "[":19,
    "]":20, "(":21, ")":22, ",":23, ";":24, "#":25, "return":26, "false":27, "true":28, "begin":29,
    "end":30, "if":31, "continue":32, "else":33, "while":34, "program":35, "func":36, "const":37,
    "var":38, "break":39, "array":40, "call":41
}

def pre_processing(file_name):
    line_dict = dict()
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    new_file_name = "tmp/tmp_" + os.path.basename(file_name)
    with open(file_name, "r", encoding="utf-8") as fp:
        nfp = open(new_file_name, "w", encoding="utf_8")
        line = fp.readline()
        cur_old_line = cur_new_line = 1
        while line:
            # 消除回车
            if line[-1] == "\n":
                line = line[:-1]
            # 消除注释
            single_com_idx = line.find("//")
            if single_com_idx != -1:
                line = line[0:single_com_idx]
            # 消除前后的空字符
            line.strip()
            if len(line) == 0:
                line = fp.readline()
                cur_old_line += 1
                continue
            # 消除行内的多余空格
            newline = ' '.join(line.split())  + "\n"# 多个空格合并成一个空格并在行尾添加换行符
            nfp.write(newline)
            line_dict[cur_new_line] = cur_old_line
            cur_new_line += 1
            line = fp.readline()
            cur_old_line += 1
        nfp.close()         
    return new_file_name, line_dict

class FARule(object):
    def __init__(self, state, char_set, next_state):
        self.state = state
        self.char_set = char_set
        self.next_state = next_state

    # 通过判断当前的状态和输入和此规则是否相容来决定是否使用该规则
    def applies(self, state, char):
        return self.state == state and char in self.char_set
    
class DFA:
    # 初始化有限自动机时包含了初始状态、接受状态集和转移规则的集合
    def __init__(self, init_state, accept_states, rule_set):
        self.init_state = init_state
        self.accept_states = accept_states
        self.rule_set = rule_set
        self.cur_state = init_state

    # 当输入一个字符时，根据当前状态和输入去转移规则中寻找对应的转移规则，
    # 根据规则获取下一个状态，并把下一个状态置为当前状态
    def inputChar(self, char):
        for r in self.rule_set:
            if r.applies(self.cur_state, char):
                self.cur_state = r.next_state
                return True
        return False

    def isAccept(self):
        return self.cur_state in self.accept_states
            
    def reset(self):
        self.cur_state = self.init_state
        
class Token:
    def __init__(self, t_type, value):
        self.t_type = t_type
        self.value = value
        
    def __str__(self):
        return f"<{self.t_type}, {self.value[0]}>"
            
class LexError(Exception):
    def __init__(self, char, lineno):
        self.char = char
        self.lineno = lineno
        
    def __str__(self):
        return f"Scanning error. Illegal character '{self.char}' at row:{self.lineno}."

class MiniLexer:
    
    reserved = ["false", "true", "begin","end", "if", "continue", "else", "while", "program", "func",
                "const", "var", "return", "break", "array", "call"]   # 16
    oper_deli = "+-*/%=<>![](),;{}&| \t\n"
    num_table = []
    sym_table = []
    
    def __init__(self, data, line_dict):
        self.data = data
        alphaBet = ''.join([chr(i) for i in range(97,123)]) + ''.join([chr(i) for i in range(65,91)]) + '_'
        digitStr = ''.join([str(i) for i in range(0,10)])
        self.rule_set = {
            FARule(1, "!<=>", 6),
            FARule(1, "%,/;[]{}()*", 2),
            FARule(1, "&", 7),
            FARule(1, digitStr, 4),
            FARule(1, "+-", 8),
            FARule(1, alphaBet, 5),
            FARule(1, "|", 9),
            FARule(3, digitStr, 3),
            FARule(4, ".", 3),
            FARule(4, digitStr, 4),
            FARule(5, digitStr+alphaBet, 5),
            FARule(6, "=", 2),
            FARule(7, "&", 2),
            FARule(8, digitStr, 4),
            FARule(9, "|", 2)
        }
        self.ac_dict = {2:"oper_deli", 3:"number", 4:"number", 5:"id", 6:"oper_deli", 8:"oper_deli"}
        self.dfa = DFA(1, self.ac_dict.keys(), self.rule_set)
        self.line_dict = line_dict
        self.cur_pos = 0
        self.lineno = 1
        self.last_token = None
    
    # Iterator interface
    def __iter__(self):
        return self

    def __next__(self):
        t = self.getToken()
        if t is None:
            raise StopIteration
        return t
    
    def skip(self, n):
        self.cur_pos += n
    
    def number_lookup(self, value):
        try:
            idx = self.num_table.index(value)
        except ValueError:
            self.num_table.append(value)
            idx = len(self.num_table) - 1
        return idx

    def symble_lookup(self, value):
        try:
            idx = self.sym_table.index(value)
        except ValueError:
            self.sym_table.append(value)
            idx = len(self.sym_table) - 1
        return idx
    
    def getToken(self):
        self.dfa.reset()
        if self.data is None:
            raise RuntimeError('No input string for scanning')
        if self.cur_pos >= len(self.data):
            return None
        if self.data[self.cur_pos] == " " or self.data[self.cur_pos] == "\t" or self.data[self.cur_pos] == "\n":
            if self.data[self.cur_pos] == "\n":
                self.lineno += 1
            self.cur_pos += 1
            # elif self.cur_pos >= len(self.data):
            #     return None
            return self.getToken()
        
        
        word = ""
        while self.cur_pos < len(self.data) and self.dfa.inputChar(self.data[self.cur_pos]):
            word += self.data[self.cur_pos]
            self.cur_pos += 1
        if self.dfa.isAccept():
            ac_state = self.dfa.cur_state
            ac_type = self.ac_dict[ac_state]
            if ac_type == "id":
                # 标识符和保留字后面只能跟限界符与运算符（包括空格）
                if self.cur_pos < len(self.data) and self.data[self.cur_pos] not in self.oper_deli:
                    raise LexError(self.data[self.cur_pos if self.cur_pos < len(self.data) else len(self.data) - 1], self.line_dict[self.lineno])
                if word in self.reserved:
                    t_type = word
                    t_val = word
                else:
                    t_type = "id"
                    self.symble_lookup(word)
                    t_val = word
            elif ac_type == "number":
                # 常量后面只能跟限界符与运算符（包括空格）
                if self.cur_pos < len(self.data) and self.data[self.cur_pos] not in self.oper_deli:
                    raise LexError(self.data[self.cur_pos if self.cur_pos < len(self.data) else len(self.data) - 1], self.line_dict[self.lineno])
                if word[0] in ["+", "-"] and self.last_token and self.last_token.t_type in ["id", "number", "false", "true"]:
                    t_type = word[0]
                    t_val = word[0]
                    self.cur_pos = self.data.rfind(word[0], 0, self.cur_pos) + 1
                else:
                    t_type = "number"
                    self.number_lookup(word)
                    t_val = word
            else:
                t_type = word
                t_val = word
            self.last_token = Token(t_type, t_val)
            return Token(t_type, t_val)

        raise LexError(self.data[self.cur_pos if self.cur_pos < len(self.data) else len(self.data) - 1], self.line_dict[self.lineno])