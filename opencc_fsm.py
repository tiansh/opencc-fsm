import sys
import typing
import fileinput
import json
import argparse

parser = argparse.ArgumentParser(description='输入繁简转换表，使用最大最早匹配，输出状态机')
parser.add_argument('input', nargs='+', help='输入文件')
parser.add_argument('--max-size', '-s', help='忽略超过该长度的规则', type=int, default=-1)
parser.add_argument('--output', '-o', help='输出文件', required=True)
args = vars(parser.parse_args())

Char = str
Text = str
TextPair = typing.Tuple[Text, Text]
RawRule = TextPair
RawTable = typing.List[RawRule]
FirstCharRawTable = typing.Dict[Char, RawTable]
FsmRule = typing.Tuple[Text, 'FsmNode']
FsmNode = typing.Dict[Char, FsmRule]

def clean_up_length(raw_table: RawTable) -> RawTable:
    """
    Clean up rules with a minimal length of args['max_size']
    """
    size = args['max_size']
    result_table = []
    for source, result in raw_table:
        if len(source) > size > 0:
           sys.stderr.write(f'Rule ignored: {source} -> {result}\n')
        else:
            result_table.append((source, result))
    return result_table

def find_matched_rules(raw_table: RawTable, text: str) -> typing.List[RawRule]:
    return [rule for rule in raw_table if text.startswith(rule[0])]

def translate_word(raw_table: RawTable, text: str) -> TextPair:
    """
    Translate first word in text with raw table
    Returns the translated first word and remaining unchanged text
    """
    matched = list(find_matched_rules(raw_table, text))
    if not matched:
        src = dst = text[0]
    else:
        src, dst = max(matched, key=lambda rule: len(rule[0]))
    return dst, text[len(src):]

def translate(raw_table: RawTable, text: str) -> str:
    """
    Translate word using raw table
    """
    output = ''
    while text:
        adding, text = translate_word(raw_table, text)
        output += adding
    return output

def translate_without_direct(raw_table: RawTable, text: str) -> str:
    """
    Apply conversion based on raw table
    """
    matched = [rule for rule in find_matched_rules(raw_table, text) if rule[0] != text]
    if not matched:
        return text[0] + translate(raw_table, text[1:])
    else:
        src, dst = max(matched, key=lambda rule: len(rule[0]))
        return dst + translate(raw_table, text[len(src):])

def build_strict_prefix_set(raw_table: RawTable) -> typing.Set[str]:
    return {s[:i] for s, _ in raw_table for i in range(1, len(s))}

def clean_up_redundant(raw_table: RawTable) -> RawTable:
    """
    Clean up rules which is not necessary as already been included by other rules
    """
    raw_table.sort(key=lambda rule: len(rule[0]))
    all_strict_prefix = build_strict_prefix_set(raw_table)
    result_table: RawTable = []
    for rule in raw_table:
        src, dst = rule
        keep = len(src) == 1 and src != dst
        keep = keep or {src[i:] for i in range(1, len(src))} & all_strict_prefix != set()
        keep = keep or len(src) > 1 and translate_without_direct(raw_table, src) != dst
        if keep:
            result_table.append(rule)
        else:
            sys.stderr.write(f'Rule ignored: {src} -> {dst}\n')
    if len(result_table) == len(raw_table):
        return result_table
    return clean_up_redundant(result_table)

def clean_up(raw_table: RawTable) -> RawTable:
    """
    Clean up raw table
    """
    return clean_up_redundant(clean_up_length(raw_table))

# Read input
def load_raw_table(filenames) -> RawTable:
    raw_table = []
    for filename in filenames:
        with fileinput.input(filename, openhook=fileinput.hook_encoded("utf-8")) as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) >= 2:
                    raw_table.append(tuple(parts[0:2]))
    return raw_table

sys.stderr.write('Phase 0...\n')
ori_table = load_raw_table(args['input'])
ori_table_size = len(ori_table)
# Raw convertion table
raw_table: typing.List[typing.Tuple[str, str]] = clean_up(ori_table)
raw_table_size = len(raw_table)
# Prefix of all words
all_strict_prefix: typing.Set[str] = build_strict_prefix_set(raw_table)

sys.stderr.write('Phase 1...\n')
root: FsmNode = {}
all_nodes: typing.List[FsmNode] = [root]
# Phase 1
# Build FSM Tree with given rules
for src, dst in raw_table:
    current = root
    for c in src:
        if c not in current:
            node: FsmNode = {}
            all_nodes.append(node)
            current[c] = ('', node)
            current = node
        else:
            current = current[c][1]
    current[''] = (dst, root)

def get_node(root: FsmNode, text: str) -> FsmNode:
    current = root
    for c in text:
        if c not in current:
            return None
        current = current[c][1]
    return current

# Phase 2
# Add edges for unmatched rules
sys.stderr.write('Phase 2...\n')
first_char_table: FirstCharRawTable = {}
for rule in raw_table:
    ch = rule[0][0]
    if ch not in first_char_table: first_char_table[ch] = []
    first_char_table[ch].append(rule)

def translate_with_tail(first_char_table: FirstCharRawTable, all_strict_prefix: typing.Set[str], text: str) -> TextPair:
    output = ''
    while text and (not output or text not in all_strict_prefix):
        adding, text = translate_word(first_char_table.get(text[0], []), text)
        output += adding
    return output, text
for src, dst in raw_table:
    for i in range(1, len(src)):
        prefix = src[:i]
        current = get_node(root, prefix)
        if '' in current: continue
        result, tail = translate_with_tail(first_char_table, all_strict_prefix, prefix)
        current[''] = (result, get_node(root, tail))

sys.stderr.write('Phase 3...\n')
# Phase 3
# Remove node with only unmatch
for node in all_nodes:
    for key in sorted(node):
        text, sub = node[key]
        while len(sub) == 1:
            text, sub = text + sub[''][0], sub[''][1]
        node[key] = text, sub

sys.stderr.write('Phase 4...\n')
# Phase 4
# Use number to replace circular reference
nodes: typing.List[FsmNode] = [root]
numbering: typing.Dict[int, int] = { id(root): 0 }

for node in nodes:
    for key in node:
        sub = node[key][1]
        if id(sub) in numbering: continue
        numbering[id(sub)] = len(nodes)
        nodes.append(sub)

table: typing.Dict[str, typing.Tuple[str, int]] = [
    {key: (node[key][0], numbering[id(node[key][1])]) for key in node} for node in nodes
]

table_size = len(table)

# Phase 5
# Write fsm out as a json file
sys.stderr.write('Phase 5...\n')
json_result = json.dumps(table, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
with open(args['output'], 'w', encoding='utf-8') as output:
    output.write(json_result)

sys.stderr.write('Generate FSM with %d nodes based on %d rules (%d rules ignored)' % (table_size, raw_table_size, ori_table_size - raw_table_size))
