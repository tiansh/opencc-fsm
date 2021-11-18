import typing
import json

class OpenCCFsm():
    def __init__(self, fsm_file: typing.IO):
        raw_table = json.load(fsm_file)
        for mapping in raw_table:
            for key in mapping:
                text, state_index = mapping[key]
                mapping[key] = (text, raw_table[state_index])
        self.state0 = raw_table[0]

    def convertFile(self, input_file: typing.IO, output_file: typing.IO):
        current = self.state0
        while True:
            ch = input_file.read(1)
            while True:
                try:
                    output, current = current[ch]
                    output_file.write(output)
                except:
                    if current is self.state0:
                        output_file.write(ch)
                    else:
                        output, current = current['']
                        output_file.write(output)
                        continue
                break
            if not ch and current is self.state0: break

    def convert(self, input_text: str):
        current = self.state0
        output_arr = []
        for ch in input_text:
            while True:
                try:
                    output, current = current[ch]
                    output_arr.append(output)
                except:
                    if current is self.state0:
                        output_arr.append(ch)
                    else:
                        output, current = current['']
                        output_arr.append(output)
                        continue
                break
        while current is not self.state0:
            output, current = current['']
            output_arr.append(output)
        return ''.join(output_arr)

