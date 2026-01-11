# Error

This agent shows an error with base `minimal` and base `fedora`.  
The error is displayed when exiting the agent right after start by repeatedly pressing Ctrl-C.

## Details

This error is shown:

```terminaloutput
file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:303297
    module2.exports = (string) => typeof string === "string" ? string.replace(ansiRegex3(), "") : string;
                                                                              ^

TypeError: ansiRegex3 is not a function
    at module2.exports (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:303297:79)
    at stringWidth (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:303358:16)
    at file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:303407:17
    at Array.map (<anonymous>)
    at ansiAlign (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:303405:19)
    at makeContentText (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:374660:40)
    at boxen (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:374828:10)
    at process.<anonymous> (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:374939:25)
    at process.emit (node:events:520:35)
    at process.processEmit [as emit] (file:///usr/local/lib/node_modules/@qwen-code/qwen-code/cli.js:249783:41)

Node.js v24.12.0
```
