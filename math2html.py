"""
math2html - convert simple latex math expressions to html code
"""

import webbrowser
import os

_math2html_map = {
    '+':    '&nbsp;+&nbsp;',
    '-':    '&nbsp;-&nbsp;',
    '=':    '&nbsp;=&nbsp;',
    ',':    ',&thinsp;',
    '\'':   '&prime;',
    '<':    '&nbsp;&lt;&nbsp;'
}

_math2html_unary = {
    '+':    '+',
    '-':    '-',
    '=':    '=&nbsp;',
    '<':    '&lt;&nbsp;'
}

_math2html_mathbb = {
}

def math2html(expr: str):
    result, i, style = math2html_inner(expr, 0)
    assert i == len(expr)
    return result


def parse_arg(expr: str, i: int) -> (str, int):
    depth = 0
    result = ''
    while True:
        x = expr[i]
        i += 1
        if x == '}':
            depth -= 1
        if depth > 0:
            result += x
        if x == '{':
            depth += 1
        if depth <= 0:
            break
    return result, i


def parse_command(expr: str, i: int) -> (str, int):
    """
    parse command following backslash
    """
    result = expr[i]
    i += 1
    while i < len(expr):
        x = expr[i]
        if 'a' <= x <= 'z' or 'A' <= x <= 'Z':
            i += 1
            result += x
        else:
            break
    return result, i


def math2html_inner(expr: str, i: int, paren_depth: int = 0, single: bool = False) -> (str, int, str):
    result = ''
    in_italic = False
    brace_depth = 0
    style = ''
    binary = False
    scopes = [{}]

    while i < len(expr):
        x = expr[i]
        i += 1

        italic = in_italic

        if x == ' ':
            continue
        elif x == '(' or x == ')':
            italic = False
            term = x
            if x == '(':
                paren_depth += 1
                binary = False
            else:
                paren_depth -= 1
                binary = True
        elif x == '{':
            term = ''
            brace_depth += 1
            scopes.append(scopes[-1])
        elif x == '}':
            term = ''
            brace_depth -= 1
            assert brace_depth >= 0
            scopes.pop()
        elif x == '_' or x == '^':
            italic = False
            binary = True
            tag = 'sub' if x == '_' else 'sup'
            term, i, temp = math2html_inner(expr, i, paren_depth + 1, True)
            if temp == '':
                open = '<{}>'.format(tag)
            else:
                open = '<{} style=\"{}\">'.format(tag, temp)
            term = open + term + '</{}>'.format(tag)
        elif 'A' <= x <= 'Z' or 'a' <= x <= 'z':
            italic = True
            term = x
            binary = True
            if 'mathbb' in scopes[-1]:
                italic = False
                term = '&' + x + 'opf;'
        elif '0' <= x <= '9':
            term = x
            italic = False
            binary = True
        elif x == '\\':
            command, i = parse_command(expr, i)
            if command == 'style':
                temp, i = parse_arg(expr, i)
                if style != '' and temp != ';':
                    style += ';'
                style += temp
                continue
            elif command == 'pos':
                temp, i = parse_arg(expr, i)
                if temp != '':
                    temp = 'position:relative;left:{}em'.format(temp)
                    if style != '':
                        style += ';'
                    style += temp
                continue
            elif command == 'le':
                term = '&nbsp;&leq;&nbsp;'
                italic = False
                binary = False
            elif command == 'mathbb':
                scopes[-1] = set()
                scopes[-1].add('mathbb')
                term = ''
            else:
                raise Exception('Unknown command {}'.format(command))
        else:
            if not binary and x in _math2html_unary:
                term = _math2html_unary[x]
            elif x in _math2html_map:
                term = _math2html_map[x]
                binary = False
            else:
                raise Exception('{} not in map'.format(x))
            italic = False

        if not in_italic and italic:
            result += '<i>'
        elif in_italic and not italic:
            result += '</i>'

        in_italic = italic
        if paren_depth > 0:
            term = term.replace('&nbsp;', '&thinsp;')
        result += term

        if single and brace_depth == 0:
            break

    if in_italic:
        result += '</i>'
    return result, i, style


if __name__ == "__main__":
    html = "<html><body>"
    for code in [
        "s_i(a+1),s_i,s'_{\\pos{-0.4}i+1}",
        "2^8=256",
        "0\\le i < 200",
        "s_{-1}",
        "\mathbb F"
    ]:
        htmleq = math2html(code)
        print(htmleq)
        html += "<p>" + htmleq + "</p>"
    with open("testmath.html", "w") as f:
        f.write(html)
    webbrowser.open("file://" + os.path.abspath(os.getcwd()) + "/testmath.html", new=2)
