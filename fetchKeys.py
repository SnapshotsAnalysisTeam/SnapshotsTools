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


def fetch_keywords(f1, f2, filetype, text_col, f3='keywords.txt'):
    '''
    功能：搜索两个文件中重叠的关键字，并把关键字存放在文件中

    输入：f1，f2为两个源文件；
    filetype：CSV；
    text_col是指关键字所在的列
    f3为存放关键字的文件；

    输出：True成功，False失败
    '''
    # 创建有序字典，用于存储关键字及其hash值
    kw_dt = collections.OrderedDict()
    kw_ls = []
    try:
        # 从f1中建造关键字字典，需要消除空格的影响
        with open(f1, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col)
                if hash(kw.replace(' ', '')) in kw_dt.keys():
                    continue
                else:
                    kw_dt[hash(kw.replace(' ', ''))] = kw

        # 从f2中建造关键字的hash列表，需要消除空格的影响
        with open(f2, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col)
                if hash(kw.replace(' ', '')) in kw_ls:
                    continue
                else:
                    kw_ls.append(hash(kw.replace(' ', '')))

        # 把既包含在f1中又包含在f2中的关键字存入f3中
        with open(f3, 'w', encoding='utf-8') as f:
            for keyIDs in kw_dt:
                if keyIDs in kw_ls:
                    kw_ls.remove(keyIDs)
                    f.write(kw_dt[keyIDs])

    except Exception as e:
        print(str(e))
        return False

    # 测试结果是否成功
    if test(f1, f2, f3, filetype, text_col):
        print('关键字提取成功')
        return True
    else:
        print('关键字提取失败')
        return True


def process(line, filetype, text_col):
    '''
    功能：根据文件结构提取关键字

    输入：line为文件的一行
    filetype为文件类型：CSV，SSV,etc.
    text_col为关键字位置

    返回值：关键字字符串，末尾带'\n'
    如果是None，说明文件分析失败

    '''
    if filetype is 'CSV':
        key_ls = line.split(',')
        # 排除文件中不符合规则的行
        if len(key_ls) < text_col:
            return '\n'
        # 检验关键字是否含有文件结尾符'\n'
        if key_ls[text_col - 1][-1] is '\n':
            return key_ls[text_col - 1]
        else:
            return '{0}{1}'.format(key_ls[text_col - 1], '\n')
    else:
        return None


def test(f1, f2, f3, filetype, text_col):
    '''
    测试代码，用于验证程序结果的正确性

    输入：f1，f2是原始提取文件
    f3是关键字文件
    filetype为文件类型：CSV，SSV,etc.
    text_col为关键字位置

    输出：True 验证成功
    False验证失败

    '''
    f1_set = set()
    f2_set = set()
    f3_set = set()
    try:
        # 测试f3中是否有重复关键字，并把关键字的hash存入集合
        with open(f3, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, 1)
                if hash(kw.replace(' ', '')) in f3_set:
                    print('关键字文件有重复')
                    return False
                else:
                    f3_set.add(hash(kw.replace(' ', '')))
        # 提取f1的关键字，用集合保存，集合自动过滤重复
        with open(f1, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col)
                f1_set.add(hash(kw.replace(' ', '')))
        # 提取f2的关键字
        with open(f2, 'r', encoding='utf-8') as f:
            for line in f:
                kw = process(line, filetype, text_col)
                f2_set.add(hash(kw.replace(' ', '')))

    except Exception as e:
        print(str(e))
        return False
    print('f1_set len is {0}'.format(len(f1_set)))
    print('f2_set len is {0}'.format(len(f2_set)))
    print('f1_set & f2_set len is {0}'.format(len(f1_set & f2_set)))
    print('f3_set len is {0}'.format(len(f3_set)))
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
    fetch_keywords(r'E:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\zhongshan NO6 hp\XRImDet.0.log',
                   r'E:\Document\DEV\Python\Logs_analysis\case\D6K\D6K_III\XRImDet.0.log',
                   'CSV',
                   9,
                   f3=r'C:\Users\305012621\AppData\Local\Programs\Python\Python36\workspace\keywords.txt')


main()
