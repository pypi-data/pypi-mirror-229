import os
import clr
import subprocess

import pandas as pd
import psutil
import time
from System.IO import Directory, Path
from .contorl_serial import Serial
from .DM3058E import DM3058E
from AudioPrecision.API import *
from .ap_eum import *


class AP500:
    """
    基类
    """

    def __init__(self):
        # dao
        print('init AP500')
        self.APx = None
        self.base_action = BaseFile(self)


class BaseFile:
    """
    基本文件操作
    """

    def __init__(self, apx):
        self.APx = apx

    def __is_process_running(self, process_name):
        # 迭代所有的进程
        for proc in psutil.process_iter():
            try:
                # 检查进程列表中是否有匹配的进程名
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def open_ap(self, app_path: str):
        """
        打开ap软件
        :param app_path: ap的exe路径
        :return: 如果打开成功，返回True，否则返回False
        """
        process_name = "AudioPrecision.APx500.exe"

        try:
            subprocess.Popen(f'"{app_path}"', shell=True)
        except Exception as e:
            print(e)
            success = False
        else:
            max_wait_time = 10  # 等待时间设为10秒
            start_time = time.time()

            while True:
                if time.time() - start_time > max_wait_time:  # 超时退出
                    print("Timeout when starting the application.")
                    success = False
                    return success

                if self.__is_process_running(process_name):  # 成功找到进程
                    success = True
                    return success

                time.sleep(0.5)  # 每隔半秒检查一次

    def close_ap(self):
        """
        关闭ap
        :return:
        """
        process_name = "AudioPrecision.APx500.exe"
        try:
            for proc in psutil.process_iter():
                if process_name.lower() in proc.name().lower():
                    proc.kill()
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def open_project(self, project_file_path: str):
        """
        打开工程
        :param project_file_path: 工程路径
        :return: 如果打开成功，返回True，否则返回False
        """
        try:
            filename = project_file_path
            print(filename)
            directory = Directory.GetCurrentDirectory()
            fullpath = Path.Combine(directory, filename)
            self.APx.APx = APx500_Application()
            self.APx.APx.OpenProject(fullpath)
            self.APx.output_configuration = OutputConfiguration(self.APx.APx)
            self.APx.input_configuration = InputConfiguration(self.APx.APx)
            self.APx.generator = Generator(self.APx.APx)
            self.APx.meter = Meters(self.APx.APx)
            self.APx.switchers = Switchers(self.APx.APx)
            self.APx.recorder = Recorder(self.APx.APx)
            self.APx.stepped_sweep = SteppedSweep(self.APx.APx)
            self.APx.sequence_mode = SequenceMode(self.APx.APx)
            self.APx.advanced = Advanced(self.APx)

            return True
        except Exception as e:
            print(e)
            return False

    def close_project(self):
        """
        关闭工程
        :return:如果关闭成功，返回True，否则返回False
        """
        try:
            self.APx.APx.CloseProject()
            return True
        except Exception as e:
            return False

    def change_mode(self, mode='BenchMode'):
        """
        切换到模式
        :param mode: BenchMode/SequenceMode
        :return:如果切换成功，返回True，否则返回False
        """

        try:
            mode = eval('APxOperatingMode.' + mode)
        except AttributeError as e:
            print(e)
            print(' 请输入正确的模式')
            return False
        self.APx.APx.OperatingMode = mode


class Generator:
    def __init__(self, apx):
        self.APx = apx

    def get_on_false(self):
        return self.APx.BenchMode.Generator.On

    def set_on_false(self, status: bool):
        """
        开启generator
        :param status: True/False
        :return:
        """
        self.APx.BenchMode.Generator.On = status

    def get_auto_on(self):
        return self.APx.BenchMode.Generator.AutoOn

    def set_auto_on(self, status: bool):
        """

        :param status: True/False
        :return:
        """
        self.APx.BenchMode.Generator.AutoOn = status
        if self.get_auto_on() != status:
            return False
        return True

    def get_waveform(self) -> str:
        return self.APx.BenchMode.Generator.Waveform

    def set_waveform(self, waveform):
        """

        :param waveform: sine/Noise/...
        :return:
        """
        self.APx.BenchMode.Generator.Waveform = waveform
        if self.get_waveform() != waveform:
            return False
        return True

    def get_levels_track_ch1(self):
        return self.APx.BenchMode.Generator.Levels.TrackFirstChannel

    def set_levels_track_ch1(self, status: str):
        """
        设置track ch1
        :param status: True/False
        :return:
        """
        self.APx.BenchMode.Generator.Levels.TrackFirstChannel = status
        if self.get_levels_track_ch1() != status:
            return False
        return True

    def get_levels(self, channel: str, unit: str = 'dbfs') -> str:
        """
        :param channel: Ch1/Ch2
        :param unit: v/vp/uv
        :return: str
        """
        return self.APx.BenchMode.Generator.Levels.GetValue(eval('OutputChannelIndex.' + channel), unit)

    def set_levels(self, channel: str, level: str):
        """
        :param channel:  Ch1/Ch2
        :param level: "133mvrms"
        :return:
        """
        self.APx.BenchMode.Generator.Levels.SetValue(eval('OutputChannelIndex.' + channel), level)
        if self.get_levels(channel) != level:
            return False
        return True

    def get_offset(self, channel: str, unit: str = 'v') -> str:
        """
        :param channel: ch1/ch2
        :return:
        """
        return self.APx.BenchMode.Generator.Levels.GetOffsetValue(eval('OutputChannelIndex.' + channel), unit)

    def set_offset(self, channel: str, offset: str):
        """
        :param channel: ch1/ch2
        :param offset: "100mv"
        :return:
        """
        return self.APx.BenchMode.Generator.Levels.SetOffsetValue(eval('OutputChannelIndex.' + channel), offset)

    def get_frequency(self, unit: str = 'hz') -> str:
        """
        :param unit: hz/'F/R'
        :return:
        """
        return self.APx.BenchMode.Generator.Frequency.GetValue(unit)

    def set_frequency(self, frequency: int, unit: str = 'hz'):
        """
        :param frequency: 100
        :param unit: hz/'F/R'
        :return:
        """
        self.APx.BenchMode.Generator.Frequency.Unit = unit
        self.APx.BenchMode.Generator.Frequency.Value = frequency

    def set_channel_enable(self, channel: str, status: bool):
        """
        :param channel: Ch1/Ch2
        :param status: True/False
        :return:
        """
        self.APx.BenchMode.Generator.SetChannelEnabled(eval('OutputChannelIndex.' + channel), status)


class InputConfiguration:
    def __init__(self, apx):
        self.APx = apx

    def connector(self, connector_type: str, channel: str):
        """
        切换connector
        :param connector_type:AnalogUnbalanced"/"DigitalUnbalanced
        :param channel: input1/input2
        :return: 如果切换成功，返回True，否则返回False
        """
        # 此处会自动判定是digital还是analog，然后返回相对应的函数
        channel = APxInputSelection.Input1 if channel == 'input1' else APxInputSelection.Input2
        _connector = eval('InputConnectorType.' + connector_type)
        self.APx.BenchMode.Setup.InputSettings(channel).InputConnector.Type = _connector

    def channels(self, channel: int):
        """
        切换channels
        :param channel: 1,2
        """
        if channel not in (1, 2):
            print('请输入正确的通道数')
            return
        self.APx.BenchMode.Setup.AnalogInput.ChannelCount = channel

    def select_input_channel(self, channel: str):
        """
        如果设置channles为1，那么channel可以选择 ch1或者Ch2
        :param channel: Ch1,Ch2
        :return: 如果切换成功，返回True，否则返回False
        """
        _channel = eval('SingleInputChannelIndex.' + channel)
        self.APx.BenchMode.Setup.AnalogInput.SingleInputChannel = _channel

    def analog_termination(self, channel: str, termination: str):
        """
        切换termination
        :param termination: 300ohm,600ohm,100kohm
        :return: 如果切换成功，返回True，否则返回False
        """
        value = eval('AnalogInputTermination.' + termination)
        channel = eval('InputChannelIndex.' + channel)
        self.APx.BenchMode.Setup.AnalogInput.SetTermination(channel,
                                                            value)

    def digital_bit_depth(self, bit_depth: int):
        """
        :param bit_depth: 8-24
        :return: 如果切换成功，返回True，否则返回False
        """
        pass

    def measure(self, measure: str):
        """
        切换measure
        :param measure: auto,voltage,digital
        :return: 如果切换成功，返回True，否则返回False
        """
        self.APx.BenchMode.Setup.Measure = eval('MeasurandType.' + measure)

    def auto_channel(self, auto: bool = True):
        """
        :param auto: True/False
        :return:
        """
        ap.APx.BenchMode.Setup.AutoChannels = auto

    def filter_high_pass(self, filter_type: str):
        """

        :param filter_type: DC/AC/butterworth/elliptic
        :return:
        """
        self.APx.BenchMode.Setup.HighpassFilter = eval('HighpassFilterMode.' + filter_type)

    def filter_low_pass(self, filter_type: str, connector_type: str):
        """

        :param filter_type: ADC/20Khz/40Khz/butterworth/elliptic
        :param connector_type: Analog/Digital
        :return:
        """
        if connector_type == 'Analog':
            self.APx.BenchMode.Setup.LowpassFilterAnalog = eval('LowpassFilterModeAnalog.' + filter_type)
        elif connector_type == 'Digital':
            self.APx.BenchMode.Setup.LowpassFilterDigital = eval('LowpassFilterModeDigital.' + filter_type)

    def filter_weighting(self, filter_type: str):
        """

        :param filter_type: A/B/C...
        :return:
        """
        self.APx.BenchMode.Setup.WeightingFilter = eval('SignalPathWeightingFilterType.' + filter_type)

    def analog_filter_bandwidth(self, filter_type: str):
        """

        :param filter_type:1.75/2.75/3.5...
        :return:
        """
        self.APx.BenchMode.Setup.LowpassFilterAnalogBandwidth = eval('AdcBandwidthEnum.' + filter_type)


class OutputConfiguration:
    def __init__(self, apx):
        self.APx = apx

    def output_connector(self, connector_type: str):
        """
        切换connector
        :param connector_type:AnalogUnbalanced"/"DigitalUnbalanced
        :return: 如果切换成功，返回True，否则返回False
        """
        try:
            _connector = eval('APxConnectorType.' + connector_type).value
        except AttributeError as e:
            print(' 请输入正确的connector')
            return False
        self.APx.BenchMode.Setup.OutputConnector.Type = _connector
        return True

    def output_channels(self, channel: int):
        """
        切换channels
        :param channel: 1,2
        """
        if channel not in (1, 2):
            print('请输入正确的通道数')
            return False
        self.APx.BenchMode.Setup.AnalogOutput.ChannelCount = channel
        return True

    def digital(self, sample_rate: str):
        """
        output digital->sample rate
        :param sample_rate:
        :return:
        """
        pass


class Switchers:
    def __init__(self, apx):
        self.APx = apx

    def change_switcher(self, switcher_type: str):
        """
        切换switcher
        :param switcher_type: output/input
        :return:
        """
        pass

    def enabled(self, status: bool):
        """
        :param status: True/False
        :return:
        """
        self.APx.BenchMode.Setup.UseInputSwitcher = status

    def set_switcher(self, address: str, channel: str, port: str):
        """

        :param address: switcher 地址
        :param channel: CHA/CHB
        :param port: 1-12
        :return:
        """
        if port == 'None':
            _port = getattr(SwitcherChannelSelection, 'None')
        else:
            _port = eval('SwitcherChannelSelection.' + port)
        _address = eval('SwitcherAddressEnum.' + address).value
        if channel == 'CHA':
            self.APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelA(_address,
                                                                            _port)
        elif channel == 'CHB':
            self.APx.BenchMode.Setup.InputSwitcherConfiguration.SetChannelB(_address,
                                                                            _port)


class Meters:
    def __init__(self, apx):
        self.APx = apx

    def get_enabled(self):
        return self.APx.BenchMode.Meters.Enabled

    def set_enabled(self, status: bool):
        self.APx.BenchMode.Meters.Enabled = status

    def get_meter_unit(self, meter_type: str, input_channel: str = 'Input1') -> str:
        """
        :param mode: RmsLevelMeter
        :param input_channel: Input1/Input2
        :return: dbrs/%/mHZ
        """
        return self.APx.BenchMode.Meters.GetDisplaySettings(eval('BenchModeMeterType.' + meter_type),
                                                            eval('APxInputSelection.' + input_channel)).Unit

    def set_meter_unit(self, meter_type: str, input_channel: str = 'Input1', unit: str = 'dbra'):
        """
        :param mode: RmsLevelMeter
        :param input_channel: Input1/Input2
        :return: dbrs/%/mHZ
        """
        self.APx.BenchMode.Meters.GetDisplaySettings(eval('BenchModeMeterType.' + meter_type),
                                                     eval('APxInputSelection.' + input_channel)).Unit = unit

    def get_meter_value(self, meter_type: str, input_channel: str = 'Input1') -> list[str]:
        """
        :param mode: RmsLevelMeter
        :param input_channel: CH1/CH2
        :return: -2dbrs/0.01%/70mHZ
        """
        res = self.is_valid(meter_type)
        if not res:
            self.add_meter_type(meter_type)
            time.sleep(1)
        if meter_type == 'GainMeter':
            self.set_meter_unit('GainMeter', 'Input1', 'db(vrms/fs)')

        return [i for i in
                self.APx.BenchMode.Meters.GetReadings(eval('BenchModeMeterType.' + meter_type),
                                                      eval(
                                                          'APxInputSelection.' + input_channel))]

    def add_meter_type(self, meter_type: str, input_channel: str = 'Input1'):
        """
        :param meter_type:RmsLevelMeter
        :param input_channel: Input1/Input2
        :return:
        """
        self.APx.BenchMode.Meters.Add(eval('BenchModeMeterType.' + meter_type),
                                      eval('APxInputSelection.' + input_channel))

    def show(self):
        """
        显示meter
        :return:
        """
        self.APx.BenchMode.Meters.Show()

    def is_valid(self, meter_type: str):
        try:
            return self.APx.BenchMode.Meters.IsValid(eval('BenchModeMeterType.' + meter_type))
        except Exception as e:
            return False


class Recorder:
    def __init__(self, apx):
        self.APx = apx

    def recorder_show(self):
        self.APx.BenchMode.Measurements.Recorder.Show()

    def start(self):
        self.APx.BenchMode.Measurements.Recorder.Start()

    def stop(self):
        self.APx.BenchMode.Measurements.Recorder.Stop()

    def save_file(self, path: str):
        if not path.endswith('.csv'):
            path = path + '.csv'
        self.APx.BenchMode.Measurements.Recorder.ExportData(
            path,
            NumberOfGraphPoints.GraphPointsAllPoints, False)

    def clear_data(self):
        self.APx.BenchMode.Measurements.Recorder.ClearData()


class SteppedSweep:
    def __init__(self, apx):
        self.APx = apx

    def sweep_show(self):
        self.APx.BenchMode.Measurements.SteppedSweep.Show()

    def start(self):
        self.APx.BenchMode.Measurements.SteppedSweep.Start()

    def save_file(self, path):
        print(path)
        self.APx.BenchMode.Measurements.SteppedSweep.ExportData(
            path,
            NumberOfGraphPoints.GraphPointsAllPoints, False)

    def start_fr(self, fr: int):
        self.APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Start.Value = fr

    def stop_fr(self, fr: int):
        self.APx.BenchMode.Measurements.SteppedSweep.SourceParameters.Stop.Value = fr


class SequenceMode:
    def __init__(self, apx):
        self.APx = apx

    def signal_path_setup(self):
        self.APx.ShowMeasurement('Signal Path1', 'Signal Path Setup')
        self.APx.SignalPathSetup.UseInputSwitcher = True
        # self.APx.

    def SignalToNoiseRatio_show(self):
        self.APx.ShowMeasurement('Signal Path1', 'Signal to Noise Ratio')

    def SignalToNoiseRatio(self):
        self.APx.ShowMeasurement('Signal Path1', 'Signal to Noise Ratio')
        time.sleep(1)
        self.APx.SignalToNoiseRatio.Start()
        time.sleep(1)
        res = self.APx.SignalToNoiseRatio.SignalToNoiseRatio.GetValues()
        return res

    def SignalToNoiseRatio_set_levels(self, channel: str, level: str):
        self.APx.SignalToNoiseRatio.Generator.Levels.SetValue(eval('OutputChannelIndex.' + channel), level)

    def SignalToNoiseRatio_set_frequency(self, frequency: int, unit: str = 'hz'):
        """
        :param frequency: 100
        :param unit: hz/'F/R'
        :return:
        """
        self.APx.SignalToNoiseRatio.Generator.Frequency.Unit = unit
        self.APx.SignalToNoiseRatio.Generator.Frequency.Value = frequency

    def CrosstalkOneChannelUndriven_show(self):
        self.APx.ShowMeasurement('Signal Path1', 'Crosstalk, One Channel Undriven')

    def crosstalk_one_channel_undriven(self):
        # 'Crosstalk, One Channel Undriven'
        self.APx.ShowMeasurement('Signal Path1', 'Crosstalk, One Channel Undriven')
        time.sleep(1)
        self.APx.CrosstalkOneChannelUndriven.Start()

        data = self.APx.CrosstalkOneChannelUndriven.Crosstalk.GetValues()
        return data

    def CrosstalkOneChannelUndriven_set_levels(self, channel: str, level: str):
        self.APx.CrosstalkOneChannelUndriven.Generator.Levels.SetValue(
            eval('OutputChannelIndex.' + channel), level)

    def CrosstalkOneChannelUndriven_set_frequency(self, frequency: int, unit: str = 'hz'):
        """
        :param frequency: 100
        :param unit: hz/'F/R'
        :return:
        """
        self.APx.CrosstalkOneChannelUndriven.Generator.Frequency.Unit = unit
        self.APx.CrosstalkOneChannelUndriven.Generator.Frequency.Value = frequency

    def set_switcher(self, address: str, channel: str, port: str):
        """

        :param address: switcher 地址
        :param channel: CHA/CHB
        :param port: 1-12
        :return:
        """
        if port == 'None':
            _port = getattr(SwitcherChannelSelection, 'None')
        else:
            _port = eval('SwitcherChannelSelection.' + port)
        _address = eval('SwitcherAddressEnum.' + address).value
        if channel == 'CHA':
            self.APx.SignalPathSetup.InputSwitcherConfiguration.SetChannelA(_address,
                                                                            _port)
        elif channel == 'CHB':
            self.APx.SignalPathSetup.InputSwitcherConfiguration.SetChannelB(_address,
                                                                            _port)


class Advanced:

    def __init__(self, ap):
        self.ap = ap
        self.auto_control_hex = (0x01, 0x02, 0x04, 0x08, 0x010, 0x20, 0x40, 0x80)
        self.double_auto_control_hex = (0x03, '', 0x0c, '', 0x30, '', 0xc0)
        self.dm = DM3058E()  #
        self.serial = Serial()

        # self.serial.open_serial('COM8')

    def open_device(self, usb, port):
        self.dm.open_device(usb)
        self.serial.open_serial(port)

    # 基础环境
    def e371_base(self):
        """
        e371 8通道 ap环境初始化
        """
        self.ap.base_action.change_mode()
        self.ap.output_configuration.output_connector('DigitalOptical')
        self.ap.input_configuration.connector('AnalogBalanced', 'input1')
        self.ap.input_configuration.filter_high_pass('AC')
        self.ap.input_configuration.filter_low_pass('LpAes17_20k', 'Analog')
        self.ap.input_configuration.filter_weighting('wt_A')
        self.ap.generator.set_levels('Ch1', '-16.6dbfs')
        self.ap.generator.set_frequency(1000)
        self.ap.switchers.enabled(True)
        self.ap.switchers.set_switcher('Switcher0', 'CHA', 'None')
        self.ap.switchers.set_switcher('Switcher0', 'CHB', 'None')
        self.ap.meter.show()

    def e371_sequence_mode_base(self):
        self.ap.base_action.change_mode('SequenceMode')
        self.ap.sequence_mode.signal_path_setup()
        self.ap.sequence_mode.set_switcher('Switcher0', 'CHA', 'None')
        self.ap.sequence_mode.set_switcher('Switcher0', 'CHB', 'None')
        self.ap.sequence_mode.CrosstalkOneChannelUndriven_show()
        self.ap.sequence_mode.CrosstalkOneChannelUndriven_set_levels('Ch1', '-16.6dbfs')
        self.ap.sequence_mode.CrosstalkOneChannelUndriven_set_frequency(1000)
        self.ap.sequence_mode.SignalToNoiseRatio_show()
        self.ap.sequence_mode.SignalToNoiseRatio_set_levels('Ch1', '-16.6dbfs')
        self.ap.sequence_mode.SignalToNoiseRatio_set_frequency(1000)

    def static_current(self):
        self.serial.a2b_start(False)
        time.sleep(3)
        sum_data = 0
        for _ in range(10):
            sum_data += float(self.dm.red_current())
        self.serial.a2b_start(True)
        time.sleep(1)
        return round((sum_data / 10) * 1000, 3)

    def idle_current(self):
        self.ap.generator.set_on_false(False)
        time.sleep(1)
        data = self.dm.red_current()
        self.ap.generator.set_on_false(True)
        print(data)
        return round(float(data), 3)

    def operating_current(self):
        data = self.dm.red_current()
        print(data)
        return round(float(data), 3)

    def background_noise(self):
        """
        底噪
        """
        self.ap.generator.set_on_false(True)
        time.sleep(1)
        self.ap.generator.set_on_false(False)
        time.sleep(1)
        data = self.ap.meter.get_meter_value('RmsLevelMeter', 'Input1')
        return data

    def dc_offset(self):
        res = self.ap.meter.is_valid('DcLevelMeter')
        if not res:
            self.ap.meter.add_meter_type('DcLevelMeter')
        time.sleep(1)
        self.ap.generator.set_on_false(True)
        time.sleep(1)
        self.ap.generator.set_on_false(False)
        time.sleep(2)
        data = self.ap.meter.get_meter_value('DcLevelMeter', 'Input1')

        return data

    def sweep(self, path, stop):
        self.ap.stepped_sweep.sweep_show()
        self.ap.stepped_sweep.start_fr(1000)
        self.ap.stepped_sweep.stop_fr(stop)
        self.ap.stepped_sweep.start()
        time.sleep(30)
        self.ap.stepped_sweep.save_file(path)
        df = pd.read_csv(path,
                         skiprows=2,
                         skipfooter=5,
                         engine='python')

        # 将列名重命名为合适的名称
        df.columns = ['Ch1_X', 'Ch1_Y', 'Ch2_X', 'Ch2_Y']

        # 计算每列 Y 值的绝对值的最大值
        df['Ch1_Y'] = pd.to_numeric(df['Ch1_Y'], errors='coerce')
        df['Ch2_Y'] = pd.to_numeric(df['Ch2_Y'], errors='coerce')
        # 最下面一个值减去倒数第十二个值
        ch1_y_max = df['Ch1_Y'].abs().iloc[-1] - df['Ch1_Y'].abs().iloc[1]
        print(ch1_y_max)
        return ch1_y_max

    def new_sweep(self):
        self.ap.generator.set_frequency(1000)
        self.ap.generator.set_on_false(True)
        self.ap.meter.set_meter_unit('RmsLevelMeter', 'Input1', 'dbra')
        time.sleep(1)
        frequency_1000 = self.ap.meter.get_meter_value('RmsLevelMeter', 'Input1')
        self.ap.generator.set_frequency(20)
        time.sleep(1)
        frequency_20 = self.ap.meter.get_meter_value('RmsLevelMeter', 'Input1')
        self.ap.generator.set_frequency(20 * 1000)
        time.sleep(1)
        frequency_20k = self.ap.meter.get_meter_value('RmsLevelMeter', 'Input1')
        self.ap.generator.set_on_false(False)
        frequency_20_1000 = [abs(frequency_1000[i] - frequency_20[i]) for i in range(len(frequency_1000))]
        frequency_20k_1000 = [abs(frequency_1000[i] - frequency_20k[i]) for i in range(len(frequency_20k))]
        self.ap.meter.set_meter_unit('RmsLevelMeter', 'Input1', 'vrms')

        return frequency_20_1000, frequency_20k_1000

    def test_on_off_transient_test(self):

        self.serial.a2b_start(False)
        time.sleep(2)
        self.serial.a2b_start(True)
        time.sleep(2)

    def on_off_transient_test(self, com):
        # serial = Serial()
        # serial.open_serial(com)
        self.ap.recorder.recorder_show()
        self.ap.recorder.start()
        # res = self.serial.a2b_start(start=False)
        # if not res:
        #     return False
        # time.sleep(2)
        # res = self.serial.a2b_start()
        # if not res:
        #     return False
        time.sleep(5)
        self.ap.recorder.stop()
        # 获取当前目录
        path = os.getcwd()

        self.ap.recorder.save_file(f'{path}\\recoder.csv')

        df = pd.read_csv(f'{path}\\recoder.csv',
                         skiprows=2,
                         skipfooter=5,
                         engine='python')

        # 将列名重命名为合适的名称
        df.columns = ['Ch1_X', 'Ch1_Y', 'Ch2_X', 'Ch2_Y']

        # 计算每列 Y 值的绝对值的最大值
        df['Ch1_Y'] = pd.to_numeric(df['Ch1_Y'], errors='coerce')
        df['Ch2_Y'] = pd.to_numeric(df['Ch2_Y'], errors='coerce')
        ch1_y_max = df['Ch1_Y'].abs().max()
        ch2_y_max = df['Ch2_Y'].abs().max()
        # 写入csv文件
        # with open("popdata.csv", 'a+', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow([ch1_y_max, ch2_y_max])

        print(f'Ch1 Y的绝对值最大值: {ch1_y_max}')
        print(f'Ch2 Y的绝对值最大值: {ch2_y_max}')

        self.ap.recorder.clear_data()
        # self.serial.a2b_start()

        return ch1_y_max, ch2_y_max

    def aux_control_output(self, data):
        """
        data 16进制数据
        :param data：0x11
        """
        self.ap.APx.AuxControlMonitor.AuxControlOutputValue = data


if __name__ == '__main__':
    # -16.600dBFS
    ap = AP500()
    # ap.base_action.open_project(r"C:\Users\hatcher\Desktop\AAC_12CH.approjx")

    # "D:\soft\ap\APx500 8.0\AudioPrecision.APx500.exe"
    # "C:\Users\hatcher\Desktop\AAC_12CH.approjx"
    ap.base_action.open_ap("D:\\soft\\ap\\APx500 8.0\\AudioPrecision.APx500.exe")
    # time.sleep(50)
    ap.base_action.open_project(r"C:\Users\hatcher\Desktop\8CHProject.approjx")
    ap.advanced.on_off_transient_test('com8')
    # ap.advanced.e371_base()
    # for key in [1, 3, 5, 7]:
    #     ap.advanced.aux_control_output(ap.advanced.double_auto_control_hex[key - 1])
    #     ap.switchers.set_switcher('Switcher0', 'CHA', 'Ch' + str(key))
    #     ap.switchers.set_switcher('Switcher0', 'CHB', 'Ch' + str(key + 1))
    #     ap.generator.set_on_false(True)
    #     time.sleep(1)
    #     gain_data = ap.meter.get_meter_value('GainMeter', 'Input1')
    #     print('gain', gain_data)
    #     # excel_operation.write_case_data('GAIN @ 1KHz 1W', gain_data, 2)
    #     thd_n_data = ap.meter.get_meter_value('ThdNRatioMeter', 'Input1')
    #     print('thd', thd_n_data)
    #     # excel_operation.write_case_data('THD+N @ 1KHz 1W', thd_n_data, 2)
    #     ap.input_configuration.filter_weighting('wt_None')
    #     sweep_value = ap.advanced.new_sweep()
    #     print('sweep', sweep_value)
    # excel_operation.write_case_data('Frequency Response @ 20Hz 1W', sweep_value[0], 2)
    # excel_operation.write_case_data('Frequency Response @ 20KHz 1W', sweep_value[1], 2)

    # ap.advanced.e371_base()
    # ap.generator.set_levels('Ch1', '-3.58dbfs')
    # for key in range(1,9):
    #     ap.advanced.aux_control_output(ap.advanced.auto_control_hex[key - 1])
    #     ap.switchers.set_switcher('Switcher0', 'CHA', 'Ch' + str(key))
    #     ap.generator.set_on_false(True)
    #     THD_20w_data = ap.meter.get_meter_value('ThdNRatioMeter', 'Input1')
    #
    #     print('thd', THD_20w_data)
    #     # excel_operation.write_case_data('THD+N @ 1KHz 20W', THD_20w_data[:1], 1)
    #     ap.generator.set_on_false(False)
    # excel_operation = ExcelOperation()
    # excel_operation.open_excel(r"C:\Users\hatcher\Downloads\E371.xlsm", "AFT")
    #
    # excel_operation.get_empty_cell_in_row()
    # ap.advanced.e371_base()
    # ap.generator.set_levels('Ch1', '-3.58dbfs')
    # for key in range(1,9):
    #     ap.advanced.aux_control_output(ap.advanced.auto_control_hex[key - 1])
    #     ap.switchers.set_switcher('Switcher0', 'CHA', 'Ch' + str(key))
    #     ap.generator.set_on_false(True)
    #     THD_20w_data =ap.meter.get_meter_value('ThdNRatioMeter', 'Input1')
    #     excel_operation.write_case_data('THD+N @ 1KHz 20W', [THD_20w_data[0]], 1)
    #     print('thd', THD_20w_data)
    # ASSIGNMENT
    # THD_20w_data
    # excel_operation.write_case_data('THD+N @ 1KHz 20W', [THD_20w_data[0]], 1)
    # ap.generator.set_on_false(False)
    # ENDFOR
