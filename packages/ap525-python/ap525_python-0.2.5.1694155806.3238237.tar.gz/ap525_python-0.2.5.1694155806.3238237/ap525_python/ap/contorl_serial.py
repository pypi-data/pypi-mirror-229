import serial
import time


class Serial:
    def __init__(self):
        self.ser = None

    def open_serial(self, com='COM7', baudrate=115200):
        # 判断串口是否打开
        if self.ser is not None:
            return
        self.ser = serial.Serial(com, baudrate)

    def a2b_start(self, start=True):
        if start:
            bytes_to = bytes.fromhex('E5 41 1B 0B 37 08 01 10 00 18 00 20 00 C8 1B FF')
        else:
            bytes_to = bytes.fromhex('E5 41 1B 0B 37 08 00 10 00 18 00 20 00 C7 1B FF')
        # 写入串口
        self.ser.write(bytes_to)
        return self.read_data()

    def read_data(self):
        # 等待一些时间让硬件设备回应
        time.sleep(2)  # 这个时间可能需要调整

        # 读取返回值
        bytes_receive = self.ser.read(self.ser.in_waiting)
        res = bytes_receive.hex()
        # E5 41 1B 0B 37 08
        if 'e5411b0b3708' not in res:
            print('a2b start fail')
            return False
        else:
            print(f"Received: {bytes_receive}")
            return True
        # 关闭串口
    def close(self):
        self.ser.close()


if __name__ == '__main__':
    ser = Serial()
    ser.open_serial('COM7')
    # ser.a2b_start(start=True)
    time.sleep(1)
    ser.a2b_start(start=True)

