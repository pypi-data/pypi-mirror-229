import enum

# from AudioPrecision.API import APxOperatingMode, OutputConnectorType, InputConnectorType, BenchModeMeterType, \
#     InputFrequencyScalingType, \
#     APxInputSelection, SingleInputChannelIndex, AnalogInputTermination, SwitcherAddress, SwitcherChannelSelection, \
#     LowpassFilterModeAnalog, SignalPathWeightingFilterType, OutputChannelIndex, MeasurandType,HighpassFilterMode
from AudioPrecision.API import *


class ChangeMode(enum.Enum):
    """
    切换模式
    """
    bench_mode = APxOperatingMode.BenchMode
    sequence_mode = APxOperatingMode.SequenceMode


class APxConnectorType(enum.Enum):
    AnalogUnbalanced = OutputConnectorType.AnalogUnbalanced
    AnalogBalanced = OutputConnectorType.AnalogBalanced
    # AnalogBalancedAdcTest = OutputConnectorType.AnalogBalancedAdcTest
    DigitalUnbalanced = OutputConnectorType.DigitalUnbalanced
    DigitalBalanced = OutputConnectorType.DigitalBalanced
    DigitalOptical = OutputConnectorType.DigitalOptical
    TransducerInterface = OutputConnectorType.TransducerInterface
    ASIO = OutputConnectorType.ASIO
    # none = eval('OutputConnectorType.' + 'None')


class InputConnectorTypeEnum(enum.Enum):
    AnalogUnbalanced = InputConnectorType.AnalogUnbalanced
    AnalogBalanced = InputConnectorType.AnalogBalanced
    # AnalogBalancedAdcTest = OutputConnectorType.AnalogBalancedAdcTest
    DigitalUnbalanced = InputConnectorType.DigitalUnbalanced
    DigitalBalanced = InputConnectorType.DigitalBalanced
    DigitalOptical = InputConnectorType.DigitalOptical
    TransducerInterface = InputConnectorType.TransducerInterface
    ASIO = InputConnectorType.ASIO


class BenchModeMeterTypeEnum(enum.Enum):
    """
     AverageJitterLevelMeter Average Jitter Level
Public fieldStatic member BandpassLevelMeter Bandpass Level
Public fieldStatic member BitErrorMeter Error Rate
Public fieldStatic member BitsMeter Bits
Public fieldStatic member CrestFactorMeter Crest Factor
Public field DataAxis Describes the type of data displayed in the meter.
Public fieldStatic member DcLevelMeter DC Level
Public fieldStatic member DcxOhmsMeter Resistance (DCX)
Public fieldStatic member DcxVoltsMeter DC Level (DCX)
Public fieldStatic member DigitalInterfaceLevelMeter Digital Interface Level
Public fieldStatic member Elements Returns the collection of BenchModeMeterTypes
Public fieldStatic member FrequencyMeter Frequency
Public fieldStatic member GainMeter Gain
Public fieldStatic member ImdRatioMeter IMD Ratio
Public field IsSettled Returns true if this meter offers settled readings, otherwise false.
Public fieldStatic member LevelRatioMeter RMS Level Ratio
Public field Name Returns the default name of this meter.
Public fieldStatic member PeakLevelMeter Peak Level
Public fieldStatic member PhaseMeter Phase
Public fieldStatic member RmsLevelMeter RMS Level
Public fieldStatic member SampleRateMeter Input Sample Rate
Public fieldStatic member SinadRatioMeter SINAD
Public fieldStatic member ThdNLevelMeter THD+N Level
Public fieldStatic member ThdNRatioMeter THD+N Ratio

    """
    AverageJitterLevelMeter = BenchModeMeterType.AverageJitterLevelMeter
    BandpassLevelMeter = BenchModeMeterType.BandpassLevelMeter
    BitErrorMeter = BenchModeMeterType.BitErrorMeter
    BitsMeter = BenchModeMeterType.BitsMeter
    RmsLevelMeter = BenchModeMeterType.RmsLevelMeter
    ThdNRatioMeter = BenchModeMeterType.ThdNRatioMeter
    FrequencyMeter = BenchModeMeterType.FrequencyMeter
    DcLevelMeter = BenchModeMeterType.DcLevelMeter
    GainMeter = BenchModeMeterType.GainMeter



class InputFrequencyScalingTypeEnum(enum.Enum):
    InputRate = InputFrequencyScalingType.InputRate
    OutputSampleRate = InputFrequencyScalingType.OutputSampleRate
    FixedRate = InputFrequencyScalingType.FixedRate


class APxInputSelectionEnum(enum.Enum):
    input_1 = APxInputSelection.Input1
    input_2 = APxInputSelection.Input2


class SingleInputChannelIndexEnum(enum.Enum):
    Ch1 = SingleInputChannelIndex.Ch1
    Ch2 = SingleInputChannelIndex.Ch2


class AnalogInputTerminationEnum(enum.Enum):
    InputTermination_600 = AnalogInputTermination.InputTermination_600


class SwitcherAddressEnum(enum.Enum):
    Switcher0 = SwitcherAddress.Switcher0
    Switcher1 = SwitcherAddress.Switcher1
    Switcher2 = SwitcherAddress.Switcher2
    Switcher3 = SwitcherAddress.Switcher3
    Switcher4 = SwitcherAddress.Switcher4
    Switcher5 = SwitcherAddress.Switcher5
    Switcher6 = SwitcherAddress.Switcher6
    Switcher7 = SwitcherAddress.Switcher7
    Switcher8 = SwitcherAddress.Switcher8
    Switcher9 = SwitcherAddress.Switcher9
    Switcher10 = SwitcherAddress.Switcher10
    Switcher11 = SwitcherAddress.Switcher11
    Switcher12 = SwitcherAddress.Switcher12
    Switcher13 = SwitcherAddress.Switcher13
    Switcher14 = SwitcherAddress.Switcher14
    Switcher15 = SwitcherAddress.Switcher15


class SwitcherChannelSelectionEnum(enum.Enum):
    Ch1 = SwitcherChannelSelection.Ch1
    Ch2 = SwitcherChannelSelection.Ch2
    Ch3 = SwitcherChannelSelection.Ch3
    Ch4 = SwitcherChannelSelection.Ch4
    Ch5 = SwitcherChannelSelection.Ch5
    Ch6 = SwitcherChannelSelection.Ch6
    Ch7 = SwitcherChannelSelection.Ch7
    Ch8 = SwitcherChannelSelection.Ch8
    Ch9 = SwitcherChannelSelection.Ch9
    Ch10 = SwitcherChannelSelection.Ch10
    Ch11 = SwitcherChannelSelection.Ch11
    Ch12 = SwitcherChannelSelection.Ch12
    Chnone = getattr(SwitcherChannelSelection, 'None')


class LowpassFilterModeAnalogEnum(enum.Enum):
    """
    low pass
    """
    AdcPassband = LowpassFilterModeAnalog.AdcPassband
    LpAes17_20k = LowpassFilterModeAnalog.LpAes17_20k
    LpAes17_40k = LowpassFilterModeAnalog.LpAes17_40k
    Butterworth = LowpassFilterModeAnalog.Butterworth
    Elliptic = LowpassFilterModeAnalog.Elliptic


class SignalPathWeightingFilterTypeEnum(enum.Enum):
    wt_A = SignalPathWeightingFilterType.wt_A
    wt_B = SignalPathWeightingFilterType.wt_B
    wt_C = SignalPathWeightingFilterType.wt_C
    wt_None = SignalPathWeightingFilterType.wt_None


class OutputChannelIndexEnum(enum.Enum):
    Ch1 = OutputChannelIndex.Ch1
    Ch2 = OutputChannelIndex.Ch2
    Ch3 = OutputChannelIndex.Ch3
    Ch4 = OutputChannelIndex.Ch4
    Ch5 = OutputChannelIndex.Ch5
    Ch6 = OutputChannelIndex.Ch6
    Ch7 = OutputChannelIndex.Ch7
    Ch8 = OutputChannelIndex.Ch8
    Ch9 = OutputChannelIndex.Ch9
    Ch10 = OutputChannelIndex.Ch10
    Ch11 = OutputChannelIndex.Ch11
    Ch12 = OutputChannelIndex.Ch12
    Ch13 = OutputChannelIndex.Ch13
    Ch14 = OutputChannelIndex.Ch14
    Ch15 = OutputChannelIndex.Ch15
    Ch16 = OutputChannelIndex.Ch16


class MeasurandTypeEnum(enum.Enum):
    auto = MeasurandType.Auto
    voltage = MeasurandType.Voltage


class HighpassFilterModeEnum(enum.Enum):
    """
    high pass
    """
    DC = HighpassFilterMode.DC
    AC = HighpassFilterMode.AC
    Butterworth = HighpassFilterMode.Butterworth
    Elliptic = HighpassFilterMode.Elliptic
    JitterAes3 = HighpassFilterMode.JitterAes3


class LowpassFilterAnalogEnum(enum.Enum):
    AdcPassband = LowpassFilterModeAnalog.AdcPassband
    LpAes17_20k = LowpassFilterModeAnalog.LpAes17_20k
    LpAes17_40k = LowpassFilterModeAnalog.LpAes17_40k
    Butterworth = LowpassFilterModeAnalog.Butterworth
    Elliptic = LowpassFilterModeAnalog.Elliptic


class LowpassFilterModeDigitalEnum(enum.Enum):
    """
    low pass
    """
    LpFsOver2 = LowpassFilterModeDigital.LpFsOver2
    Butterworth = LowpassFilterModeDigital.Butterworth
    Elliptic = LowpassFilterModeDigital.Elliptic


class SignalPathWeightingFilterTypeEnum(enum.Enum):
    wt_None = SignalPathWeightingFilterType.wt_None
    wt_A = SignalPathWeightingFilterType.wt_A
    wt_B = SignalPathWeightingFilterType.wt_B
    wt_C = SignalPathWeightingFilterType.wt_C
    wt_Ccir = SignalPathWeightingFilterType.wt_Ccir
    wt_Dolby2k = SignalPathWeightingFilterType.wt_Dolby2k
    wt_Ccitt = SignalPathWeightingFilterType.wt_Ccitt
    wt_CMessage = SignalPathWeightingFilterType.wt_CMessage
    wt_Deemph50us = SignalPathWeightingFilterType.wt_Deemph50us
    wt_Deemph75us = SignalPathWeightingFilterType.wt_Deemph75us
    wt_Deemph50usA = SignalPathWeightingFilterType.wt_Deemph50usA
    wt_Deemph75usA = SignalPathWeightingFilterType.wt_Deemph75usA


class AdcBandwidthEnum(enum.Enum):
    """
    bw1p75k 0 1.75 kHz (4 kHz SR)
bw3k 1 2.75 kHz (6 kHz SR)
bw3p5k 2 3.5 kHz (8 kHz SR)
bw5k 3 5.5 kHz (12 kHz SR)
bw7k 4 7 kHz (16 kHz SR)
bw10k 5 11 kHz (24 kHz SR)
bw20k44kHz 6 20 kHz (44.1 kHz SR)
bw20k 7 22.4k (48 kHz SR)
bw40k88kHz 8 40 kHz (88.2 kHz SR)
bw45k 9 45k (96 kHz SR)
bw80k176kHz 10 80 kHz (176.4 kHz SR)
bw90k 11 90k (192 kHz SR)
bw250k 12 250k (624 kHz SR)
bw500k 13 500k (1.248 MHz SR)
bw1M 14 1M (2.496 MHz SR)
    """
    bw1p75k = AdcBandwidth.bw1p75k
    bw3k = AdcBandwidth.bw3k
    bw3p5k = AdcBandwidth.bw3p5k
    bw5k = AdcBandwidth.bw5k
    bw7k = AdcBandwidth.bw7k
    bw10k = AdcBandwidth.bw10k
    bw20k44kHz = AdcBandwidth.bw20k44kHz
    bw20k = AdcBandwidth.bw20k
    bw40k88kHz = AdcBandwidth.bw40k88kHz
    bw45k = AdcBandwidth.bw45k
    bw80k176kHz = AdcBandwidth.bw80k176kHz
    bw90k = AdcBandwidth.bw90k
    bw250k = AdcBandwidth.bw250k
    bw500k = AdcBandwidth.bw500k
    bw1M = AdcBandwidth.bw1M