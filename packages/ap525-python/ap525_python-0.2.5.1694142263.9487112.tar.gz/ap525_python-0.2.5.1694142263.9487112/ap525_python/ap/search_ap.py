import os
import string
import concurrent.futures


def find_software_in_directory(directory, software_name):
    for root, dirs, files in os.walk(directory):
        if software_name in files:
            return os.path.join(root, software_name)
    return None  # 如果在此目录下未找到软件，则返回None


def multi_thread_search(start_directories, software_name):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_dir = {executor.submit(find_software_in_directory, directory, software_name): directory for directory
                         in start_directories}
        print(future_to_dir)
        for future in concurrent.futures.as_completed(future_to_dir):
            res = future.result()
            if res is not None:
                return res
    return "Software not found."


if __name__ == '__main__':
    # 识别所有的硬盘分区
    available_drives = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)]

    software_name_to_find = "AudioPrecision.APx500.exe"  # 更改为你希望搜索的软件名称，并包括文件扩展名

    print(multi_thread_search(available_drives, software_name_to_find))
