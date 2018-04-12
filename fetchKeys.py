'''
搜索两个文件重叠的关键字
用有序字典（key，value）方式记录关键字
key为value的hash
把结果存入文件

未来改进方向
不再提供具体的指定文件入口，而是提供两个同一类产品的snapshots
文件格式和关键字分析方法放在类似‘D6K_III Snapshots 文件分析.xlsx’中
程序根据文件结构，自动对所有有用文件进行关键字分析，结果存入数据库中
'''

import collections
import re
import time


def optimize(func):
    def wrapper(*arg,**kwarg):
        start = time.time()
        func(*arg,**kwarg)
        runtime = time.time() - start
        print(runtime)
    return wrapper


@optimize
def fetchKeywords(f1, f2, filetype, text_col, pattern = [(r'\d+\.\d+|\s\d+',r'x'),], f3='keywords.txt', f4 = 'err.key'):
    '''
    Usage::
    搜索两个文件中的关键字，把重叠关键字存放入文件f3，把不重叠的关键字放入文件f4

    Input::
    :param class:str f1，f2为两个源文件的文件路径及名字；
    :param class:str filetype，文件类型，主要为'CSV'，'SSV'等等；
    :param class:int text_col是指关键字所在的列
    :param class:list pattern，提取关键字的正则表达式，缺省为空
    :param class:str f3为存放f1，f2中相同关键字的文件；
    :param class:str f4为存放f1，f2中不同关键字的文件

    Output::
    :return class:bool True成功，False失败
    '''
    # 创建有序字典，用于存储关键字及其hash值
    kw1_dt = collections.OrderedDict()
    kw2_dt = collections.OrderedDict()
    print(pattern)

    try:
        # 从f1中建造关键字字典，需要消除空格的影响
        start = time.time()
        with open(f1, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col, pattern)
                if hash(kw.replace(' ', '')) in kw1_dt.keys():
                    continue
                else:
                    kw1_dt[hash(kw.replace(' ', ''))] = kw
        runtime = time.time() - start
        print('f1=',runtime)

        # 从f2中建造关键字的hash列表，需要消除空格的影响
        start = time.time()
        with open(f2, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col, pattern)
                if hash(kw.replace(' ', '')) in kw2_dt.keys():
                    continue
                else:
                    kw2_dt[hash(kw.replace(' ', ''))] = kw
        runtime = time.time() - start
        print('f2=', runtime)

        # 把既包含在f1中又包含在f2中的关键字存入f3中，把其余写入f4
        start = time.time()
        with open(f3, 'w', encoding='utf-8') as key, open(f4, 'w', encoding='utf-8') as err:
            for keyIDs in kw1_dt:
                if keyIDs in kw2_dt.keys():
                    key.write(kw1_dt[keyIDs])
                    kw2_dt.pop(keyIDs)
                else:
                    #包含在f1中的异常关键字
                    err.write(kw1_dt[keyIDs])
            #把kw2_dt中剩余内容写入err，包含在f2中的异常关键字
            for keyIDs in kw2_dt:
                err.write(kw2_dt[keyIDs])
        runtime = time.time() - start
        print('f3=', runtime)

    except Exception as e:
        print(str(e))
        return False

    # 测试结果是否成功
    if test(f1, f2, filetype, text_col, pattern, f3, f4):
        print('关键字提取成功')
        return True
    else:
        print('关键字提取失败')
        return False


def process(line, filetype, text_col, pattern = [(r'\d+\.\d+|\s\d+',r'x'),]):
    '''
    Usage::
    根据文件结构和过滤规则提取关键字
    经过测试，速度的瓶颈在这个函数的正则表达式，去掉正则运算，时间从10s变为1.7s

    Input::
    :param class:str line为文件的一行
    :param class:str filetype为文件类型：CSV，SSV,etc.
    :param class:int text_col为关键字位置
    :param class:str pattern，提取关键字的正则表达式，缺省为空

    Output::
    :return class:str 关键字字符串，末尾带'\n', 如果是None，说明文件分析失败

    '''
    if filetype == 'CSV':
        key_ls = line.split(',')
        # 排除文件中不符合规则的行
        if len(key_ls) < text_col:
            return '\n'
        # 检验关键字是否含有文件结尾符'\n'
        str1 = key_ls[text_col - 1]
        for pat in pattern:
            str1  = re.sub(pat[0],pat[1],str1)
        if str1[-1] == '\n':
            return str1
        else:
            return '{0}{1}'.format(str1, '\n')
    else:
        return None


def test(f1, f2, filetype, text_col, pattern = [(r'\d+\.\d+|\s\d+',r'x'),], f3 = 'keywords.txt', f4 = 'err.key'):
    '''
    测试代码，用于验证程序结果的正确性

    Input::
    :param class:str f1，f2为两个源文件；
    :param class:str filetype，文件类型，主要为'CSV'，'SSV'等等；
    :param class:int text_col是指关键字所在的列
    :param class:str pattern，提取关键字的正则表达式，缺省为空
    :param class:str f3为存放f1，f2中相同关键字的文件；
    :param class:str f4为存放f1，f2中不同关键字的文件

    Output::
    :return class: bool True  验证成功，False 验证失败

    '''
    f1_set = set()
    f2_set = set()
    f3_set = set()
    f4_set = set()

    try:
        # 测试f3中是否有重复关键字，并把关键字的hash存入集合
        with open(f3, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, 1, pattern)
                if hash(kw.replace(' ', '')) in f3_set:
                    print('关键字文件有重复')
                    return False
                else:
                    f3_set.add(hash(kw.replace(' ', '')))
        # 提取f1的关键字，用集合保存，集合自动过滤重复
        with open(f1, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col, pattern)
                f1_set.add(hash(kw.replace(' ', '')))
        # 提取f2的关键字
        with open(f2, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col, pattern)
                f2_set.add(hash(kw.replace(' ', '')))

    except Exception as e:
        print(str(e))
        return False
    f4_set = f1_set ^ f2_set
    print('f1_set len is {0}'.format(len(f1_set)))
    print('f2_set len is {0}'.format(len(f2_set)))
    print('f1_set & f2_set len is {0}'.format(len(f1_set & f2_set)))
    print('f3_set len is {0}'.format(len(f3_set)))
    print('f4_set len is {0}'.format(len(f4_set)))
    # 集合操作

    if f1_set & f2_set == f3_set:
        return True
    else:
        return False


def main():
    ##    search_keywords(r'E:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\zhongshan NO6 hp\sysMSG.log',
    ##                    r'E:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\sysMSG.log',
    ##                    'CSV',
    ##                    7,
    ##                    f3 =r'C:\Users\305012621\AppData\Local\Programs\Python\Python36\workspace\keywords.txt')
    fetchKeywords(r'D:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\zhongshan NO6 hp\XRImDet.0.log',
                   r'D:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\XRImDet.0.log',
                   'CSV',
                   9,
                   pattern = [(r'\d+\.\d+(e(\+|\-)\d+)?', r'x'),
                              (r'([A-Fa-f0-9]{2}\:){3}[A-Fa-f0-9]\:([A-Fa-f0-9]{2}\:)([A-Fa-f0-9]{2})',
                               r'[MAC_XX]'), (r'\]\d+', r']x'), (r'\:\d+', r':x'), (r'\s\d+', r' x'),
                              (r'PA\d+\-\d', r'PAxxxx'), (r'\d+', r'[n]')],
                   f3 = r'XRImDet.key',
                   f4 = r'XRImDet.err')

main()
