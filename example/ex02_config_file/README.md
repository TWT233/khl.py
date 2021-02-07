# example 02 别把米洒了

啥叫别把米洒了？我们来想想，ex01 里我们是怎么填凭证的：

> 我们看到 `ex01.py` 的第 3~4 行：
>
> ```python
> # init Cert for Bot OAuth
> cert = Cert(client_id='xxxxxxxx', client_secret='xxxxxxxx', token='xxxxxxxx')
> ```
>
> 把我们在 ex00 拿到的「Client Id」「Token」「Client Secret」对号入座填进去就 ok 了，注意用引号括起来
>
> 填完之后保存一下代码，然后我们再来一把：

我们直接把凭证放代码里了，这其实非常危险也非常不好：

1. 如果你使用 github/gitee/coding 等代码托管服务的话，这些凭证就会随着代码一起上传到网上，别人很轻松就能拿到你的凭证，拿到凭证 = 机器人归他所有，被拿去做坏事儿你也抓不到
2. 每次换机器人/换配置都要搬出代码来改，蛮麻烦的，特别是以后项目大了更是烦人

那咋办呢？

## 用配置文件存凭证

大家可以看到在 `example` 文件夹下已经有了一个 `config` 文件夹，里面是 `config.json.example`，这是我们为大家准备的样板文件，大家把这个文件改名为 `config.json` 就可以开始用了

`config.json` 已经被放入了 `.gitignore`，不用担心上传到代码托管平台的安全问题，所以 khl.py 的内部测试其实也是用的 `config.json` 来做凭证、配置的保存，蛮好用的

### `config.json` 咋填？

和 ex01 一样，「Client Id」「Token」「Client Secret」对号入座，保存文件即可

Q: 还有两项「verify_token」「encrypt_key」是啥？

A: 这两项是为 webhook 准备的，我们现在留空即可

### 怎么在代码中读取 `config.json`？

看 `ex02.py` 第 5 ~ 13 行：

```python
# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 用读取来的 config 初始化 cert，字段对应即可
cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])
```

其他部分都一样，就不再 copy 过来水行数了，水太多也不好

## 用配置文件的话，运行代码的方式要变吗

是需要的，但也很简单：保证你的工作目录在 `example` 文件夹下即可，然后：

```shell
python ex02_config_file/ex02.py
```

怎么看工作目录？
在命令行中输入 pwd，看看结尾是 `khl.py/example` 还是 `khl.py`，前者是正确的

为什么要这么做？
因为我们在代码里是用相对路径定位 `config.json`，文件夹层级乱了就找不到了

除了改工作目录，当然也可以改代码里的文件路径了，这里就不展开细说
