# example 02 别把米洒了

啥叫别把米洒了？我们来想想，ex01 里我们是怎么填凭证的：

> 看到 `ex01.py` 的第 3~4 行：
> ```python
> # init Bot
> bot = Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')
> ```
> 把我们在 ex00 拿到的「Token」填进去就 ok 了

我们直接把凭证放代码里了，这其实非常危险也非常不好：

1. 如果你使用 github/gitee/coding 等代码托管服务的话，这些凭证就会随着代码一起上传到网上，别人很轻松就能拿到你的凭证，拿到凭证 = 机器人归他所有，被拿去做坏事儿你也抓不到
2. 每次换机器人/换配置都要搬出代码来改，蛮麻烦的，特别是以后项目大了更是烦人

那咋办呢？

## 用配置文件存凭证

大家可以看到在 `example` 文件夹下已经有了一个 `config` 文件夹，里面是 `config.json.example`，这是我们为大家准备的样板文件，大家把这个文件改名为 `config.json` 就可以开始用了

> `config.json` 已经被放入了 `.gitignore`，不用担心会被上传到代码托管平台，khl.py 的内部测试也是用的 `config.json` 来做凭证、配置的保存，蛮好用的

### `config.json` 咋填？

我们只需要填「Token」即可，记得打引号哦。还有，json 中字符串只能用双引号括起来，注意一下

Q: 还有两项「verify_token」「encrypt_key」是啥？

A: 「verify_token」「encrypt_key」这两项是为 webhook 准备的，我们现在留空即可

### 怎么在代码中读取 `config.json`？

看 `ex02.py` 第 5 ~ 11 行：

```python
# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
```

是不是很简单？而且以后要换 bot 也不用打开代码来改了，修改一下 json 就行，安全性也得到了保障

## 用配置文件的话，运行代码的方式要变吗

要的，但也很简单：保证你的工作目录在示例代码文件夹内即可，然后：

```shell
python ex02.py
```

怎么看工作目录？ 在命令行中输入 pwd，看看结尾是 `example` 还是 `example/ex02_config_file`，后者是正确的

*（这里使用 ex02 作为例子，如果大家读后续的其他 ex，记得换到对应的目录内）*

为什么要这么做？ 因为我们在代码里是用相对路径定位 `config.json`，文件夹层级乱了就找不到了

*除了改工作目录，当然也可以改代码里的文件路径寻址方式，这里就不展开细说*

*另：在代码中写死路径是一种很不好的习惯，经常会让程序表现和使用者预期不符 /
让使用方法难以理解（比如我们这里就让使用方法难以理解了：如果你换个调用姿势还跑不起来）
但这是为了示例尽量简单，否则处理路径的代码就已经不短了*

*推荐使用 os.path 来解决这种 hardcoded path 问题*
