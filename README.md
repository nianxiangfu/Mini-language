* 项目简介

  此项目是《编译原理》课程大作业，自制了Mini语言的词法规则与语法规则，并用Python实现了词法分析器与语法分析器。在词法分析器中构造了一个识别Mini语言单词符号的有限自动机，在语法分析器中用LL(1)预测分析法对Mini语言的语法单位进行识别。具体内容可见`Mini语言的词法设计及词法分析.md`与`Mini语言的语法设计及语法分析.md`。

* 目录与文件描述

  * `mini_cfg.txt`：Mini语言的上下文无关文法，语法分析器将以此作为输入。
  * `re.txt`：识别Mini语言所有单词符号的正规式。
  * `test`：其中包含了用Mini语言编写的冒泡排序算法与快速排序算法，作为测试用例。
  * `code`：程序代码
  * `code/MiniLexer(Lex impl).py`：利用[PLY(Python Lex Yacc)](http://www.dabeaz.com/ply/index.html)编写的Mini语言的词法分析器
  * `ply`：PLY(Python Lex Yacc)源代码

