# khl.py

SDK for kaiheila.cn in python

# install

Python requirement: >= Python 3.6

```shell
pip install khl.py
```

# short-term roadmap

docs:

- [x] docs init

perf:

- [x] check `SN`

feat:

T1:

- [ ] log system
- [ ] command alias
- [ ] command & arg parse system
- [ ] `MsgCtx` design

bug fix:

- [x] error parsing str in `."` pattern (cmd_prefix+unclosing quote)

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message