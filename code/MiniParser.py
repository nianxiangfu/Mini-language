from MiniLexer import MiniLexer
import itertools
import os

class MiniParseError(Exception):
    error_priority_dict = {
        "PROGRAM":1, "FUNCDEF":2, "SIMVARSM":5, "ARRVARSM":5, "CONSTSM":5, "ASSM":5, "IFSM":4, "ELSE":4, "LOOPSM":4,
        "CALLSM":5, "EXP":7
    }
    error_info_dict = {
        "PROGRAM": "program definition error",
        "FUNCDEF": "function definition error",
        "SIMVARSM": "variable description error",
        "ARRVARSM": "array variable description error",
        "CONSTSM": "constant description error",
        "ASSM": "assignment statement error",
        "IFSM": "conditional statement error",
        "ELSE": "conditional statement error",
        "LOOPSM": "loop statement error",
        "CALLSM": "function call statement error",
        "EXP": "expression error",
    }
    def __init__(self, word, lineno, nt):
        self.word = word
        self.lineno = lineno
        self.nt = nt
        
    def __str__(self):
        return f"Parsing failed, {self.error_info_dict[self.nt]}. Illegal word '{self.word}' at row:{self.lineno}."

class CFG():
    def __init__(self, G_path, start, eof, epsilon, Vt):
        self.getProds(G_path)
        self.eof = eof
        self.epsilon = epsilon
        self.Vt = Vt
        self.Vt.append(self.eof)
        self.Vn = set([t[0] for t in self.prods])
        self.start = start
        self.eflag = None   # error flag
        self.getFirsts()
        self.getFollows()
        self.getParseTable()
        # if not os.path.exists("tmp"):
        #     os.makedirs("tmp")
        # with open("tmp/new_g.txt", "w", encoding="utf8") as fp:
        #     for l, r in self.prods:
        #         s = l + " -> " + " ".join(r) + "\n"
        #         fp.write(s)
        
    def getParseTable(self):
        self.LL_1_table = {k:self.eflag for k in itertools.product(self.Vn, self.Vt)}
        for l, r in self.prods:
            first = self.getFirst(r)
            for a in first:
                if a in self.Vt:
                    self.LL_1_table[(l, a)] = (l, r)
            if self.epsilon in first:
                for b in self.follows[l]:
                    self.LL_1_table[(l, b)] = (l, r)
        
    # calc the first_set of the right part of a production
    def getFirst(self, r):
        rhs = self.firsts[r[0]] - {self.epsilon}
        i = 0
        while i < len(r) - 1 and self.epsilon in self.firsts[r[i]]:
            rhs |= self.firsts[r[i+1]] - {self.epsilon}
            i += 1
        if i == len(r) - 1 and self.epsilon in self.firsts[r[-1]]:
            rhs.add(self.epsilon)
        return rhs
        
    def getFirsts(self):
        self.firsts = dict()
        for t in self.Vt:
            self.firsts[t] = {t}
        for nt in self.Vn:
            self.firsts[nt] = set()
        self.firsts[self.epsilon] = {self.epsilon}
        flag = True
        while flag:
            flag = False
            for l, r in self.prods:
                rhs = self.getFirst(r)
                if not rhs.issubset(self.firsts[l]):
                    flag = True
                    self.firsts[l] |= rhs                
        
    def getFollows(self):
        self.follows = dict()
        for nt in self.Vn:
            self.follows[nt] = set()
        self.follows[self.start] = {self.eof}
        flag = True
        while flag:
            flag = False
            for l, r in self.prods:
                if r[0] == self.epsilon:
                    continue
                trailer = self.follows[l].copy()
                for beta in r[::-1]:
                    if beta in self.Vn:
                        if not trailer.issubset(self.follows[beta]):
                            flag = True
                            self.follows[beta] |= trailer
                        if self.epsilon in self.firsts[beta]:
                            trailer |= self.firsts[beta] - {self.epsilon}
                        else:
                            trailer = self.firsts[beta].copy()                            
                    else:
                        trailer = self.firsts[beta].copy()
        
    def getProds(self, G_path):
        def getProd(line):
            left, right = line.split("->")
            left = left.strip()
            right = right.split(" | ")
            r_list = []
            for r in right:
                r_list.append(r.split())
            return left, r_list
        
        self.prods = []
        with open(G_path, "r", encoding="utf8") as fp:
            for line in fp:
                if line.strip() == "":
                    continue
                left, r_list = getProd(line)
                for r in r_list:
                    self.prods.append((left, r))

class Node:
    def __init__(self, text):
        self.text = text
        self.child = []

    def __str__(self):
        return self.text
    
def printTree(node, indent, is_last_child, is_root, file=None):
    for i in indent:
        print(i, end = "", file=file)
    if not is_root:
        print('?????????' if is_last_child else '?????????', end="", file=file)
    print(node, file=file)
    indent.append('    ' if is_last_child else '???   ')
    for i, c in enumerate(node.child, 0):
        printTree(c, indent, i == len(node.child) - 1, False, file=file)
    indent.pop()

class MiniParser:
    def __init__(self, lexer, cfg):
        self.lexer = lexer
        self.cfg = cfg
        
    def nextWord(self):
        return self.lexer.getToken()
        
    # def LL_1_parse(self):
    #     word = self.nextWord()
    #     stack = [self.cfg.eof, self.cfg.start]
    #     nt_stack = [(self.cfg.start, 1)]
    #     while True:
    #         if stack[-1] == self.cfg.eof:   # eof
    #             if word is None:
    #                 print("Parsing success.")
    #                 break
    #             else:
    #                 raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
    #         elif stack[-1] in self.cfg.Vt:  # Vt
    #             if stack[-1] == word.t_type:
    #                 stack.pop()
    #                 word = self.nextWord()
    #                 if len(stack) == nt_stack[-1][1]:
    #                     nt_stack.pop()
    #             else:
    #                 # print(stack)
    #                 # print(nt_stack)
    #                 raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
    #         else:   # Vn
    #             p = self.cfg.LL_1_table[(stack[-1], word.t_type)]
    #             if p != self.cfg.eflag:
    #                 nt = stack.pop()
    #                 # ???ELSE???????????????????????????????????????else?????????else?????????????????????if????????????
    #                 if nt == "ELSE" and word.t_type == "else":
    #                     stack += reversed(["else", "SM"])
    #                 elif p[1][0] != self.cfg.epsilon:
    #                     if nt in MiniParseError.error_priority_dict.keys() and \
    #                         MiniParseError.error_priority_dict[nt] > MiniParseError.error_priority_dict[nt_stack[-1][0]]:
    #                         nt_stack.append((nt, len(stack)))
    #                     stack += reversed(p[1])
    #             else:
    #                 raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
    
    def LL_1_parse(self):
        word = self.nextWord()
        tree = Node(self.cfg.start)
        stack = [Node(self.cfg.eof), tree]
        nt_stack = [(self.cfg.start, 1)]
        while True:
            if stack[-1].text == self.cfg.eof:   # eof
                if word is None:
                    print("Parsing success.")
                    break
                else:
                    raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
            elif stack[-1].text in self.cfg.Vt:  # Vt
                if stack[-1].text == word.t_type:
                    stack.pop()
                    word = self.nextWord()
                    if len(stack) == nt_stack[-1][1]:
                        nt_stack.pop()
                else:
                    # print(stack)
                    # print(nt_stack)
                    raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
            else:   # Vn
                p = self.cfg.LL_1_table[(stack[-1].text, word.t_type)]
                if p != self.cfg.eflag:
                    cur_node = stack.pop()
                    # ???ELSE???????????????????????????????????????else?????????else?????????????????????if????????????
                    if cur_node.text == "ELSE" and word.t_type == "else":
                        for i in reversed(["else", "SM"]):
                            stack.append(Node(i))
                            cur_node.child.insert(0, stack[-1])
                    elif p[1][0] != self.cfg.epsilon:
                        if cur_node.text in MiniParseError.error_priority_dict.keys() and \
                            MiniParseError.error_priority_dict[cur_node.text] > MiniParseError.error_priority_dict[nt_stack[-1][0]]:
                            nt_stack.append((cur_node.text, len(stack)))
                        for i in reversed(p[1]):
                            stack.append(Node(i))
                            cur_node.child.insert(0, stack[-1])
                    elif p[1][0] == self.cfg.epsilon:
                        cur_node.child.insert(0, Node(self.cfg.epsilon))
                else:
                    raise MiniParseError(word.value, self.lexer.line_dict[self.lexer.lineno], nt_stack[-1][0])
        return tree