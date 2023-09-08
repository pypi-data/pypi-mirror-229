from PySide6.QtCore import QThread, Signal
import string
import os
import concurrent.futures


class FindSoftwareThread(QThread):
    signal = Signal(str)

    def __init__(self, start_directories=None, software_name=None):
        QThread.__init__(self)
        self.start_directories = start_directories if start_directories else ['%s:\\' % d for d in
                                                                              string.ascii_uppercase if
                                                                              os.path.exists('%s:\\' % d)]
        self.software_name = software_name if software_name else "AudioPrecision.APx500.exe"

    def find_software_in_directory(self, directory, software_name):
        for root, dirs, files in os.walk(directory):
            if software_name in files:
                return os.path.join(root, software_name)
        return None

    def multi_thread_search(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_dir = {executor.submit(self.find_software_in_directory, directory, self.software_name): directory
                             for directory in self.start_directories}
            for future in concurrent.futures.as_completed(future_to_dir):
                res = future.result()
                if res is not None:
                    return res
        return "Software not found."

    def run(self):
        result = self.multi_thread_search()
        self.signal.emit(result)  # 发送信号
