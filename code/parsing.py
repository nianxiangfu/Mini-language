from MiniLexer import pre_processing, MiniLexer, type2val
from MiniParser import MiniParser, MiniParseError, CFG, printTree
import sys
import os


if len(sys.argv) == 2:
    src_file = sys.argv[1]
else:
    src_file = "../test/lex_test_pos.mini"
tmp_src_file, line_dict = pre_processing(src_file)

fp = open(tmp_src_file, "r", encoding="utf-8")
src_code_str = fp.read()
fp.close()

mini_lexer = MiniLexer(src_code_str, line_dict)
cfg = CFG("../mini_cfg.txt", "PROGRAM", "#", "ϵ", list(type2val.keys()))
mini_parser = MiniParser(mini_lexer, cfg)
parseTree = mini_parser.LL_1_parse()

with open("parse_output.txt", "w", encoding="utf8") as fp:
    printTree(parseTree, [], True, True, fp)

