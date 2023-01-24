"""
math2html - convert simple latex math expressions to html code
"""

_math2html_map = {
    '+':    '&nbsp;+&nbsp;',
    '-':    '&nbsp;-&nbsp;',
    '=':    '&nbsp;=&nbsp;',
    ',':    ',&thinsp;',
    '\'':   '&prime;',
    '<':    '&nbsp;&lt;&nbsp;'
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


def math2html_inner(expr: str, i: int, paren_depth: int = 0, single: bool = False) -> (str, int, str):
    result = ''
    in_italic = False
    brace_depth = 0
    style = ''

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
            else:
                paren_depth -= 1
        elif x == '{':
            term = ''
            brace_depth += 1
        elif x == '}':
            term = ''
            brace_depth -= 1
            assert brace_depth >= 0
        elif x == '_' or x == '^':
            italic = False
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
        elif '0' <= x <= '9':
            term = x
            italic = False
        elif x == '\\':
            if expr[i:].startswith('style{'):
                i += 5
                temp, i = parse_arg(expr, i)
                if style != '' and temp != ';':
                    style += ';'
                style += temp
            elif expr[i:].startswith('pos{'):
                i += 3
                temp, i = parse_arg(expr, i)
                if temp != '':
                    temp = 'position:relative;left:{}em'.format(temp)
                    if style != '':
                        style += ';'
                    style += temp
            elif expr[i:].startswith('le'):
                i += 2
                term = '&nbsp;&leq;&nbsp;'
                italic = False
            else:
                raise Exception('Unknown command {}'.format(expr[i-1:]))
        else:
            if x not in _math2html_map:
                raise Exception('{} not in map'.format(x))
            term = _math2html_map[x]
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
    print(math2html("F(a)+1"))
    print(math2html("s_i(a+1)"))
    print(math2html("s_{i-1},s_i,s_{i+1}"))
    print(math2html("s'_{\pos{-0.4}i}"))
    print(math2html("2^8=256"))
    print(math2html("0\le i < 200"))