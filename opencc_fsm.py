import sys
import typing
import fileinput
import json
import argparse

parser = argparse.ArgumentParser(description='输入繁简转换表，使用最大最早匹配，输出状态机')
parser.add_argument(
    'input',
    nargs='?',
    help='输入文件'
)
parser.add_argument(
    '--output', '-o',
    help='输出文件',
    required=True
)
args = vars(parser.parse_args())

raw_table: typing.List[typing.Tuple[str, str]] = []
all_prefix: typing.List[str] = []

for line in fileinput.input(args['input'], openhook=fileinput.hook_encoded("utf-8")):
    parts = line.strip().split()
    if len(parts) >= 2:
        raw_table.append(tuple(parts[0:2]))

def is_redundant(table: typing.List[typing.Tuple[str, str]], source: str, result: str):
    if source == result == '':
        return True
    for s, t in table:
        if source == s:
            return result == t
        elif source.startswith(s):
            if result.startswith(t):
                return is_redundant(table, source[len(s):], result[len(t):])
            else:
                return False
        elif s.startswith(source):
            return False
    if source[0] != result[0]:
        return False
    return is_redundant(table, source[1:], result[1:])

def clean_up_redundant(raw_table: typing.List[typing.Tuple[str, str]]):
    raw_table.sort(key=lambda p: len(p[0]))
    all_prefix = {s[:i] for s, _ in raw_table for i in range(1, len(s))}
    result_table = []
    for source, result in raw_table:
        keep = len(source) == 1
        keep = keep or {source[i:] for i in range(1, len(source))} & all_prefix != set()
        keep = keep or not is_redundant(result_table, source, result)
        if keep:
            result_table.insert(0, (source, result))
        else:
            sys.stderr.write(f'Rule ignored: {source} -> {result}\n')
    return result_table

def clean_up_redundant_wrap(raw_table: typing.List[typing.Tuple[str, str]]):
    while True:
        lines = len(raw_table)
        raw_table = clean_up_redundant(raw_table)
        if lines == len(raw_table):
            return raw_table

raw_table = clean_up_redundant_wrap(raw_table)

all_prefix = [s[:i] for s, _ in raw_table for i in range(1, len(s))]

def translate_word(text: str) -> typing.Tuple[str, str]:
    for src, dst in raw_table:
        if text.startswith(src):
            return dst, text[len(src):]
    return text[0], text[1:]

def translate(text: str) -> str:
    output = ''
    while text:
        adding, text = translate_word(text)
        output += adding
    return output

def translate_with_tail(text: str) -> typing.Tuple[str, str]:
    output = ''
    while text and (not output or text not in all_prefix):
        adding, text = translate_word(text)
        output += adding
    return output, text

table: typing.List[typing.Dict[str, typing.Tuple[str, int]]] = []

# Parse 1
table.append({})
for src, dst in reversed(raw_table):
    state = 0
    for i in range(len(src)):
        c = src[i]
        current = table[state]
        if c not in current:
            state = len(table)
            current[c] = ('', state)
            table.append({})
        else:
            state = current[c][1]
    table[state][''] = (dst, 0)

def get_node(text):
    state = 0
    while text:
        current = table[state]
        if text[0] not in current:
            return None
        text, state = text[1:], current[text[0]][1]
    return state

# Parse 2
for src, dst in raw_table:
    for i in range(1, len(src)):
        prefix = src[:i]
        state = get_node(prefix)
        current = table[state]
        if '' in current: continue
        result, tail = translate_with_tail(prefix)
        current[''] = (result, get_node(tail))

# Parse 3
mapping = {}
removed = {}
simplify = []

for state in range(len(table)):
    current = table[state]
    if list(current.keys()) == ['']:
        removed[state] = table[state]
    else:
        mapping[state] = len(simplify)
        simplify.append(table[state])
for state in range(len(simplify)):
    current = simplify[state]
    for c in sorted(current.keys()):
        while current[c][1] in removed:
            prev_text, prev_state = current[c]
            current[c] = (prev_text + removed[prev_state][''][0], removed[prev_state][''][1])
        current[c] = (current[c][0], mapping[current[c][1]])

json_result = json.dumps(simplify, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
with open(args['output'], 'w', encoding='utf-8') as output:
    output.write(json_result)


