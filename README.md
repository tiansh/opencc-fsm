基于 OpenCC 项目的繁简转换词典，利用最早最大匹配的分词方式，将词典转换为状态机。单字转换使用词汇表里的第一个结果。

最早最大匹配指，当存在多条规则同时匹配时，优先匹配起始位置最早的，如果起始位置一样，匹配最长的。

生成的状态机：

* 状态机是一个数组，0索引
* 第0个元素是状态机的起始状态
* 每次输入一个字
    * 如果当前状态的字典有这个字对应的键：
        * 输出对应的文本后跳转到指定的状态
    * 如果这个字不在字典中，且当前不是0状态：
        * 按照空字符串对应的状态输出和跳转，之后重新处理输入的这个字
    * 如果这个字不在字典中，且当前是0状态：
        * 原封不动输出这个字
* 当转换结束时，如果不在0状态，反复匹配空串对应的状态，直至到达0状态

示例输出的状态机 fsm/t2s.json, fsm/s2t.json 由 dict 目录下对应的 txt 生成。dict 目录下的 txt 文件基于 OpenCC 的词典生成，有部分改动。详情见 dict 目录。

## Credits

dist 目录下的 json 文件描述的繁简转换规则，基于 OpenCC 项目提供的转换字典生成而来。OpenCC 项目由 BYVoid 等人创作。本项目基于 Apache License 2.0 协议使用该项目的资源。

## About

本项目使用 MIT 协议释出。但请注意附带的转换结果另有其他项目的版权，与本项目无关。
