import os
import shutil


# 删除文件夹
def del_dir(dir_name: str, mode=1):
    """
    :param dir_name: 文件夹名字
    :param mode: 1为删除文件夹里面内容 2为连着文件夹一起删除
    :return:
    """
    if mode == 1:
        for file in os.listdir(dir_name):
            file_path = os.path.join(dir_name, file)
            os.remove(file_path)
    elif mode == 2:
        shutil.rmtree(dir_name)


# 格式化为可以创建的文件名
def format_str(data: str):
    # 去除字符串中的 ' / , \ , " , ? , * , < , > , | , : ,空格'
    return data.replace('/', '').replace('\\', '').replace('"', '').replace('?', '').replace('*', '') \
        .replace('<', '').replace('>', '').replace('|', '').replace(':', '').replace(' ', '')


# 创建文件夹
def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if isExists := os.path.exists(path):
        # print(' 创建过了')
        return False
    os.makedirs(path)
    print(f'{path} 创建成功')
    return True


# 获取文件夹大小
def getdirsize(dir):
    return sum(sum(os.path.getsize(os.path.join(root, name)) for name in files) for root, dirs, files in os.walk(dir))


# 获取硬盘信息
def get_ssd_info(path, show_mode='gb'):
    import shutil
    total, used, free = shutil.disk_usage(path)
    # bite/1024 kb/1024 mb/1024 gb
    if show_mode == 'gb' or show_mode == 'GB':
        sizi = 1024 ** 3
    elif show_mode == 'mb' or show_mode == 'MB':
        sizi = 1024 ** 2
    else:
        raise '输入正确字节单位'
    all_size = round(total / sizi, 2)
    used_size = round(used / sizi, 2)
    free_size = round(free / sizi, 2)
    return all_size, used_size, free_size


# 获取系统路径
def get_path(desktop=False, temp=False):
    if desktop:
        return os.path.join(os.path.expanduser("~"), 'Desktop')
    if temp:
        return os.getenv('TEMP')