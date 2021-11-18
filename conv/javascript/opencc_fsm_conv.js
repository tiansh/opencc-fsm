/** @typedef {{ [ch: string]: [string, number] }[]} OpenCCFsm */
/** @typedef {(fsm: OpenCCFsm, text: string) => string} OpenCCFsmConvert */
; (function (global, /** @type {() => { convert: OpenCCFsmConvert }} */factory) {
  if (typeof exports === 'object' && typeof module !== 'undefined') {
    module.exports = factory();
  } else if (typeof define === 'function' && define.amd) {
    define('underscore', factory);
  } else {
    const main = typeof globalThis !== 'undefined' ? globalThis : global || self;
    main.OpenCCFsm = factory();
  }
}(this, function () {
  /** @type {OpenCCFsmConvert} */
  const openCCFsmConvert = function (fsm, text) {
    const hasOwnProperty = Object.prototype.hasOwnProperty;
    let output = '';
    let state = 0;
    for (let char of text) {
      while (true) {
        const current = fsm[state];
        const hasMatch = hasOwnProperty.call(current, char);
        if (!hasMatch && state === 0) {
          output += char;
          break;
        }
        if (hasMatch) {
          const [adding, next] = current[char];
          if (adding) output += adding;
          state = next;
          break;
        }
        const [adding, next] = current[''];
        if (adding) output += adding;
        state = next;
      }
    }
    while (state !== 0) {
      const current = fsm[state];
      const [adding, next] = current[''];
      if (adding) output += adding;
      state = next;
    }
    return output;
  };

  return { convert: openCCFsmConvert };
}));

