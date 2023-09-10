import shutil


def main():
    print(f'好家伙')
    print(f'不可能')


def get_example():
    # 获取当前文件的路径
    src = __file__
    # 生成目标文件名，可以根据需要修改
    dst = "example.py"
    # 复制文件
    shutil.copy(src, dst)
