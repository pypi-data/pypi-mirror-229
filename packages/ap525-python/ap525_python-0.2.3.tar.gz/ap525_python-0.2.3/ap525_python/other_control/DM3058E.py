import pyvisa


class DM3058E:
    # 数字万用表
    def __init__(self):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource('USB0::0x1AB1::0x09C4::DM3R251701566::INSTR')  # 例如：'GPIB0::22::INSTR'

    def red_current(self):
        data = self.inst.query(':MEASure:CURRent:DC?')
        return data


if __name__ == '__main__':
    dm = DM3058E()
    data = dm.red_current()
    print(data)
