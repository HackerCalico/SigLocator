import os
import shutil
import string
import random
import threading
import subprocess

sigList = []
workPath = os.path.join(os.environ['userprofile'], 'Desktop', "".join(random.choices(string.ascii_letters, k=10)))
testWD = True
testMem = False

# 测试机器码是否存在特征码
def TestCode(code):
    print(f'Testing length: {len(code)}')
    killed = False
    if testMem:
        # 保存至桌面 BIN 文件
        '''
        开头添加该函数 ShellCode, 让杀毒软件有充足的扫描时间
        void Wait(PVOID pSleep) {
            ((int(*)(...))pSleep)(60000);
        }
        '''
        codePath = f'{workPath}\\{"".join(random.choices(string.ascii_letters, k=10))}.bin'
        with open(codePath, 'wb') as f:
            f.write(b'\x48\x89\x4C\x24\x08\x48\x83\xEC\x28\xB9\x60\xEA\x00\x00\xFF\x54\x24\x30\x90\x48\x83\xC4\x28\xC3' + code)
        # 创建 Loader 程序
        testMemPath = f'{workPath}\\{"".join(random.choices(string.ascii_letters, k=10))}.exe'
        shutil.copyfile('TestMem.exe', testMemPath)
        # 内存加载查杀
        print(f'Testing Bin: {codePath}')
        print(f'Testing EXE: {testMemPath}')
        try:
            threading.Thread(target=lambda: subprocess.Popen([testMemPath, codePath])).start()
        except:
            pass
        killed = input('是否被查杀(任意字符Yes/回车No): ')
        try:
            os.remove(codePath)
        except:
            pass
        try:
            os.remove(testMemPath)
        except:
            pass
    else:
        # 保存至桌面 EXE 文件
        samplePath = f'{workPath}\\{"".join(random.choices(string.ascii_letters, k=10))}.exe'
        with open(samplePath, 'wb') as f:
            f.write(code)
        # 运行查杀
        try:
            print(f'Testing EXE: {samplePath}')
            os.startfile(samplePath)
        except Exception as e:
            if testWD and 'WinError 225' in str(e):
                killed = True
        if not testWD:
            killed = input('是否被查杀(任意字符Yes/回车No): ')
        try:
            os.remove(samplePath)
        except:
            pass
    return killed

def FindSigHead(start, end, code):
    while True:
        point = (start + end) // 2
        snippet = code[point:]
        # print('FindSigHead', start, point, end)
        if point == start:
            break
        if TestCode(snippet): # point <= 特征码起始位置
            start = point
        else: # point > 特征码起始位置
            end = point
    return start

def FindSigTail(start, end, code):
    while True:
        point = (start + end) // 2
        snippet = code[:point]
        # print('FindSigTail', start, point, end)
        if point == start:
            break
        if TestCode(snippet): # point >= 特征码结束位置
            end = point
        else: # point < 特征码结束位置
            start = point
    return end

def BinarySearch(code):
    segSize = len(code) // 2
    snippet1 = code[:segSize]
    snippet2 = code[segSize:]

    # 定位两片段中的特征码
    killed = False
    if TestCode(snippet1):
        killed = True
        BinarySearch(snippet1)
    if TestCode(snippet2):
        killed = True
        BinarySearch(snippet2)

    # 两片段均存活, 说明机器码中仅有一个特征码且被截断
    if not killed:
        # 查找特征码起始位置 (一定位于 0 ~ segSize 之间)
        head = FindSigHead(0, segSize, code)
        # 查找特征码结束位置 (一定位于 segSize ~ 结尾 之间)
        tail = FindSigTail(segSize, len(code), code)
        # 输出特征码
        signature = code[head:tail]
        if len(signature) > 0:
            global sigList
            sigList += [signature]
            print('\033[92m' + f'[+] Signature: {signature}' + '\033[0m')
            sigName = f'{"".join(random.choices(string.ascii_letters, k=10))}.bin'
            with open(sigName, 'wb') as f:
                f.write(signature)
            print('\033[92m' + f'[+] Save to {sigName}' + '\033[0m')

if __name__ == '__main__':
    print(r'''   ___|  _)         |                          |
 \___ \   |   _` |  |       _ \    __|   _` |  __|   _ \    __|
       |  |  (   |  |      (   |  (     (   |  |    (   |  |
 _____/  _| \__, | _____| \___/  \___| \__,_| \__| \___/  _|
            |___/
https://github.com/HackerCalico/SigLocator''')
    print('\033[31m' + f'[!] 当前项目务必添加至所有杀毒软件的白名单.' + '\033[0m')
    print('\033[31m' + f'[!] 定位前务必关闭所有杀毒软件的样本提交功能.' + '\033[0m')
    print('\033[31m' + f'[!] 请在确保样本在本机运行时不会产生危害的情况下进行测试.' + '\033[0m')
    print('\033[31m' + f'[!] 为了测试准确请确保只有一个杀毒软件起作用, 建议阅读 README.' + '\033[0m')
    codePath = input('\033[94m' + 'CodePath: ' + '\033[0m')
    with open(codePath, 'rb') as f:
        code = f.read()
    testMem = input('\033[94m' + '是否测试内存查杀 (任意字符Yes/回车No): ' + '\033[0m')
    if not testMem:
        testWD = input('\033[94m' + '测试杀软是否为 Windows Defender (任意字符Yes/回车No): ' + '\033[0m')
    os.makedirs(workPath)

    _1st = True
    while _1st or TestCode(code):
        _1st = False
        # 定位特征码
        BinarySearch(code)
        # 清除已知特征码
        if len(sigList) == 0: # 样本不存在特征码
            break
        for sig in sigList:
            code = code.replace(sig, b'')