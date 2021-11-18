const fs = require('fs');

const opencc_fsm_conv = require('./opencc_fsm_conv.js');

try {
  const [fsmFile, inputFile, outputFile] = process.argv.slice(2);
  if (!fsmFile || !inputFile || !outputFile) throw TypeError();
  const fsm = JSON.parse(fs.readFileSync(fsmFile));
  const text = String(fs.readFileSync(inputFile));
  const output = opencc_fsm_conv.convert(fsm, text);
  fs.writeFileSync(outputFile, output);
} catch (e) {
  process.stderr.write(`Usage: ${process.argv.slice(0, 2).join(' ')} fsm_file input_file ouput_file\n`);
}

