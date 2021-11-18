import opencc_fsm_conv

import sys
import argparse

parser = argparse.ArgumentParser(description='输入繁简转换的状态机，转换文件')
parser.add_argument('fsm_file', help='状态机文件')
parser.add_argument('input_file', nargs='?', default=None, help='输入文件')
parser.add_argument('output_file', nargs='?', default=None, help='输出文件')
args = vars(parser.parse_args())

with open(args['fsm_file'], 'r', encoding='utf-8') as fsm_file:
    fsm = opencc_fsm_conv.OpenCCFsm(fsm_file)

with (
    open(args['input_file'], 'r', encoding='utf-8', newline='') 
    if args['input_file'] else sys.stdin
    as input_file,
    open(args['output_file'], 'w', encoding='utf-8', newline='')
    if args['output_file'] else sys.stdout
    as output_file
):
    fsm.convertFile(input_file, output_file)


