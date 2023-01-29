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
    '<':    '&nbsp;&lt;&nbsp;',
    '>':    '&nbsp;&gt;&nbsp;',
    '/':    '/'
}

_math2html_unary = {
    '+':    '+',
    '-':    '-',
    '=':    '=&nbsp;',
    '<':    '&lt;&nbsp;'
}

_math2html_symbols = {
    'le': '&nbsp;&leq;&nbsp;',
    'circ': '&cir;',
    'ldots': '&hellip;',
    'Vert': '&Vert;',
    'log':  'log',
    'prod': '<span style="font-size:150%">&prod;</span>',
    'equiv':    '&nbsp;&equiv;&nbsp;',
    '{':        '&lcub;',
    '}':        '&rcub;&nbsp;'
}

_math2html_letters = {
}

_math2html_env = {'aligned'}

for letter in ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota',
               'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau',
               'upsilon', 'phi', 'chi', 'psi',  'omega'
]:
    _math2html_letters[letter] = '&' + letter + ';'
    letter = letter[0].upper()
    _math2html_letters[letter] = '&' + letter + ';'


def math2html(expr: str):
    """
    The main entry point
    convert LaTeX math expression to html
    """
    result, i, style = math2html_inner(expr, 0)
    assert i == len(expr)
    return result


def parse_arg(expr: str, i: int) -> (str, int):
    """
    get argument to command
    """
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
    if 'a' <= result <= 'z' or 'A' <= result <= 'Z':
        while i < len(expr):
            x = expr[i]
            if 'a' <= x <= 'z' or 'A' <= x <= 'Z':
                i += 1
                result += x
            else:
                break
    return result, i


def math2html_inner(expr: str, i: int, paren_depth: int = 0, single: bool = False) -> (str, int, str):
    """
    The main loop converting LaTeX expression to html
    """
    result = ''
    in_italic = False
    brace_depth = 0
    style = ''
    binary = False
    scopes = [{}]
    environs = []

    while i < len(expr):
        x = expr[i]
        i += 1

        italic = in_italic

        if x == ' ' or x == '\n':
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
            term, i, temp = math2html_inner(expr, i, paren_depth + 1, True)
            tag = 'sub' if x == '_' else 'sup'
            if i < len(expr):
                if (expr[i] == '^' or expr[i] == '_') and expr[i] != x:
                    #temp = 'position:absolute;white-space:nowrap;' + temp
                    temp = 'display:inline-block;width:0px;white-space:nowrap;' + temp
            if temp == '':
                open = '<{}>'.format(tag)
            else:
                open = '<{} style=\"{}\">'.format(tag, temp)
            term = open + term + '</{}>'.format(tag)
        elif x == '\'' and i < len(expr) and expr[i] == '_':
            italic = False
            term = "<span style='display:inline-block;width:0px'>&prime;</span>"
        elif 'A' <= x <= 'Z' or 'a' <= x <= 'z':
            italic = True
            term = x
            binary = True
            if 'rm' in scopes[-1]:
                italic = False
            if 'mathbb' in scopes[-1]:
                italic = False
                term = '&' + x + 'opf;'
            elif 'mathcal' in scopes[-1]:
                italic = False
                term = '&' + x + 'scr;'
        elif '0' <= x <= '9' or x == '.':
            term = x
            italic = False
            binary = True
        elif x == '\\':
            command, i = parse_command(expr, i)
            if command == ' ':
                term = command
                binary = False
            elif command == 'begin':
                arg, i = parse_arg(expr, i)
                assert arg in _math2html_env
                environs.append(arg)
                assert arg == 'aligned'
                term = '<table style="border:none;margin:auto;display:inline;font-size:100%">\n' + \
                       '<tr><td style="white-space:nowrap;border:none;text-align:right;padding:0;">'
                italic = False
            elif command == '\\':
                if environs[-1] == 'aligned':
                    term = '</td></tr>\n<tr><td style="white-space:nowrap;border:none;text-align:right;padding:0;">'
                    italic = False
                else:
                    term = '<br>'
            elif command == 'end':
                arg, i = parse_arg(expr, i)
                assert arg == environs.pop()
                term = '</td></tr></table>'
            elif command == 'style':
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
            elif command in _math2html_symbols:
                term = _math2html_symbols[command]
                italic = False
                binary = False
            elif command in _math2html_letters:
                term = _math2html_letters[command]
                italic = True
                binary = True
            elif command == 'mathbb' or command == 'mathcal' or command == 'rm':
                scopes[-1] = set()
                scopes[-1].add(command)
                term = ''
            else:
                raise Exception('Unknown command {}'.format(command))
        elif x == '&':
            assert environs[-1] == 'aligned'
            term = '</td><td style="white-space:nowrap;border:none;text-align:left;padding:0;">'
            italic = False
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
        # "s^i_{23}(a+1),s_i^{23},s'_{i+1}",
        # "2^8=256",
        # "0\\le i < 200",
        # "Q + {\\mathbb F + H} + R_{-1}",
        # "2^s > \\omega/2",
        # "f_i\\circ\\omega\\Vert{\\mathcal ab}c \\lambda",
        "s'_i=s_{i-1}{\\rm \\ XOR\\ }(s_i{\\rm \\ OR\\ }s_{i+1})",
        "\\begin{aligned}"
        "&g_{1i}\\equiv(f_i^2-f_i)/Z_N,\\\\"
        "&g_{2i}\\equiv(f_i\\circ\\omega+f_{i-1}-2f_{i-1}f_i\\circ\\omega-f_i-f_{i+1}+f_if_{i+1})/Z_N,\\\\"
        "&g_{3i}\\equiv(f_i-a_i)/(X-c\\omega^N)."
        "\\end{aligned}",
        "\\{x_1,x_2,x_3,x_4\\}=\\{2,3,4,5\\}"
    ]:
        htmleq = math2html(code)
        print(htmleq)
        html += "<p>" + htmleq + "</p>"

    html += '<p>a = jgp + c + d + e + f + g + h<br>x&nbsp;=&nbsp;' \
            '<span style="display:inline-block;width:2em;position:relative;">' \
            '<span style="display:inline-block;padding-top:0.8em;position:relative;bottom:-1em;text-align:center;font-size:70%;white-space:nowrap">N - 1</span>' \
            '<span style="display:inline-block;position:relative;left:0em;bottom:-0.6em;font-size:150%">&prod;</span>' \
            '<span style="display:inline-block;padding-bottom:1.5em;position:relative;top:1.5em;width:2em;text-align:center;font-size:70%">i = 0</span>' \
            '</span>' \
            '(X-c&omega;<sup>N</sup>)<br>aa = jgp + c + d + e + f + g + h</p>'
    html += "<p><span style='position:absolute'>overlayed text</span>\n" \
            "This is some dummy text</p>"
    with open("testmath.html", "w") as f:
        f.write(html)
    webbrowser.open("file://" + os.path.abspath(os.getcwd()) + "/testmath.html", new=2)
