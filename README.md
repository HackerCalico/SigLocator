# SigLocator

### 请给我 Star 🌟，非常感谢！这对我很重要！

### Please give me Star 🌟, thank you very much! It is very important to me!

### 1. 介绍

https://github.com/HackerCalico/SigLocator

高效的 RAT 特征码定位器，支持定位不同杀软标记的静态查杀、内存查杀的特征码。

为了改进我的混淆器以及 C2 框架，我开发了该项目来探究特征码。它通过一定算法将 RAT 机器码不断分片查杀，在尽可能少的次数内定位到准确的特征码。

### 2. 使用方法

<mark>先将当前项目添加至白名单，关闭所有杀软的样本提交功能，确保要测试的样本对当前主机没有危害(测试过程中可能运行)，确保只有一个杀软起作用，就可以开始了。</mark>

(1) 测试 Windows Defender 静态查杀特征码

自行准备一份 CS Stager 的 ShellCode 二进制文件。

```bash
> python SigLocator.py
CodePath: stager.bin
是否测试内存查杀 (任意字符Yes/回车No):
测试杀软是否为 Windows Defender (任意字符Yes/回车No): y
Testing length: 447
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\StjhBDaHNH.exe
Testing length: 223
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\xKVmmJxzHh.exe
....
[+] Signature: b'\xfcH...wininet'
Save to LWhhKCiFTo.bin
```

我的测试结果放在了 Signature Results 文件夹。

该过程全自动，因为被 WD 查杀时可以自动捕获到准确的查杀异常信息。

(2) 测试 Kaspersky 企业版静态查杀特征码

自行准备一份 CS Stager 的 ShellCode 二进制文件。

```bash
> python SigLocator.py
CodePath: stager.bin
是否测试内存查杀 (任意字符Yes/回车No):
测试杀软是否为 Windows Defender (任意字符Yes/回车No):
Testing length: 447
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\IlUEEwWSHt.exe
是否被查杀(任意字符Yes/回车No): y
Testing length: 223
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\HyCVmBCXUL.exe
是否被查杀(任意字符Yes/回车No):
....
[+] Signature: b'wininet\x00AVI\x89\xe6'
[+] Save to lKvXAIPfbu.bin
```

我的测试结果放在了 Signature Results 文件夹。

<mark>在测试 WD 以外的杀软时需要手动判断每次是否被查杀，下面列出了测试 Kaspersky 时会遇到的坑：</mark>

1.是否被查杀在下图界面 (主页 -> 详细信息) 可以第一时间看到，但是如果查杀后样本被立刻清除，则此界面信息会一闪而过，只能在右下角的弹窗通知看到，所以每个弹窗通知看完后要及时关闭，否则后面的弹窗会被阻塞。如果此界面存在 "解决" 按钮，则必须解决完后再继续测试下一个片段，否则可能无法看到查杀信息导致判断错误。

2.在测试每个片段时建议多等几秒钟，且不要输入错误，不要因为着急导致判断错误。

![Kaspersky.png](https://github.com/HackerCalico/SigLocator/blob/main/Image/Kaspersky.png)

(3) 测试 Kaspersky 企业版内存查杀特征码

自行通过 Process Hacker 2 从 CS 后门内存中导出机器码。

![dump.png](https://github.com/HackerCalico/SigLocator/blob/main/Image/dump.png)

```bash
> python SigLocator.py
CodePath: dump.bin
是否测试内存查杀 (任意字符Yes/回车No): y
Testing length: 274432
Testing Bin: C:\Users\Calico\Desktop\YMfXHUncCX\NIdTeSIdUB.bin
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\bSIdBWZJeI.exe
是否被查杀(任意字符Yes/回车No): y
Testing length: 137216
Testing Bin: C:\Users\Calico\Desktop\YMfXHUncCX\TkbLLCOsGK.bin
Testing EXE: C:\Users\Calico\Desktop\YMfXHUncCX\vERLvfLDaz.exe
是否被查杀(任意字符Yes/回车No): y
....
[+] Signature: b'\x03\xd1\xc1\xc8\r\x8b\xceD3\xf8D\x03\xc2A\x0b\xce#\xcfE\x03\xd8A\x8b\xc6A\x8b\xd23\xd3'
[+] Save to UlvAVFvfiT.bin
....
[+] Signature: b'%s as %s\\%s:....%d\t%d\t%s'
[+] Save to jlvJcZLJCu.bin
```

我的测试结果 (特征码 x 6) 及测试过程，放在了 Signature Results 文件夹。

<mark>测试 Kaspersky 时会遇到的坑同 (2)</mark>

### 3. 功能实现

(1) 查杀测试

1.静态查杀：将机器码直接保存为 EXE 运行，不符合 PE 结构也会让杀软立刻对其检测。

2.内存查杀：将一个 sleep 1 分钟的 ShellCode 与机器码拼接保存为 BIN 文件，再用一个 Loader 程序对其加载。

实验证明 Loader 程序本身因为不包含特征码不会被 Kaspersky 查杀。而创建线程调用机器码时 Kaspersky 会检测内存中的机器码，如果存在特征码会清除 Loader 程序。但是不会清除 BIN 文件，证明内存特征码必须加载到内存进行测试。

(2) 分片算法

1.二分定位

将机器码等分为两个片段，分别进行查杀测试。

若被查杀则对片段递归进一步二分定位。

若两片段均存活，说明机器码中仅有一个特征码且被截断，进行逼近定位。

2.逼近定位

分别对机器码中唯一的特征码的 "起始位置" 和 "结束位置" 进行逼近定位，最终得到准确的特征码。

下面简单展示对 "起始位置" 逼近定位时的流程，对 "结束位置" 的逼近定位思想一样。

黄色代表特征码的位置。

start 的初始位置为当前片段的起始位置。

end 的初始位置为当前片段的正中间，因为特征码的 "起始位置" 一定在其左侧。

point 的初始位置为 start 与 end 的正中间。

| 0     | <mark>1</mark> | <mark>2</mark> | <mark>3</mark> | <mark>4</mark> | <mark>5</mark> | <mark>6</mark> | <mark>7</mark> | 8   |
|:----- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- |:--- |
| start |                | point          |                | end            |                |                |                |     |

测试 point 到结尾的片段发现存活，说明特征码被 point 截断， point > 特征码的 "起始位置"，更新 end、point。

| 0     | <mark>1</mark> | <mark>2</mark> | <mark>3</mark> | <mark>4</mark> | <mark>5</mark> | <mark>6</mark> | <mark>7</mark> | 8   |
|:----- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- |:--- |
| start | point          | end            |                |                |                |                |                |     |

测试 point 到结尾的片段发现被查杀，说明 point <= 特征码的 "起始位置"，更新 start、point。

| 0   | <mark>1</mark> | <mark>2</mark> | <mark>3</mark> | <mark>4</mark> | <mark>5</mark> | <mark>6</mark> | <mark>7</mark> | 8   |
|:--- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- |:--- |
|     | start point    | end            |                |                |                |                |                |     |

start = point，说明找到了特征码的 "起始位置"。