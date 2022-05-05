from MiniLexer import pre_processing, MiniLexer
import sys
import os


if len(sys.argv) == 2:
    src_file = os.path.basename(sys.argv[1])
else:
    src_file = "../test/lex_test_pos.mini"
tmp_src_file, line_dict = pre_processing(src_file)

fp = open(tmp_src_file, "r", encoding="utf-8")
src_code_str = fp.read()
fp.close()
mini_lexer = MiniLexer(src_code_str, line_dict)
token = mini_lexer.getToken()
while token:
    print(token)
    token = mini_lexer.getToken()
    
# for token in mini_lexer:
#     print(token)