# khl.py

SDK for kaiheila.cn in python

# install

**Only available in test.pypi now**

```shell
python3 -m pip install Flask==1.1.2 requests==2.25.0 pycryptodomex==3.9.9
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps khl.py
```

# short-term roadmap

feat:

- [ ] bot init config
- [ ] msg handling in events loop
- [ ] log system
- [ ] command alias
- [ ] command & arg parse system
- [ ] `MsgCtx` design
- [ ] replace `flask` with `aiohttp`

bug fix:

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message