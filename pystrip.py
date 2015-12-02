#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pystrip.py
#
"""Strip a Python source file of comments and docstrings.

Source: http://stackoverflow.com/a/2962727/390275

Also part of pyminifier.

"""

import tokenize
import re

def remove_comments_and_docstrings(source):
    """Returns 'source' minus comments and docstrings."""
    out = []
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0

    for tok in tokenize.generate_tokens(source.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]

        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0

        if start_col > last_col:
            out.append(" " * (start_col - last_col))

        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an
                # operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new 
                    # statement and newlines inside of operators such as 
                    # parentheses, brackets, and curly braces. Newlines 
                    # inside of operators are NEWLINE tokens and 
                    # newlines which start new code are NL tokens.
                    
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out.append(token_string)

                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parentheses,
                    # brackets, and curly braces) as actual indentation.
                    #
                    # For example:
                    #
                    # def foo():
                    #     """Whitespace before this docstring is tokenize.INDENT"""
                    #     test = [
                    #         "Whitespace before this string does not get a token"
                    #     ]
        else:
            out.append(token_string)

        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line

    out = "".join(out).splitlines()
    return "\n".join(line for line in out if line.strip())


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')
    else:
        infile = sys.stdin

    print(remove_comments_and_docstrings(infile))

    if infile is not sys.stdin:
        infile.close()
