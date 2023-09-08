import clr
import os

try:
    clr.AddReference(
        os.path.join(os.path.dirname(__file__), 'ap_dll', 'AudioPrecision.API.dll'))  # Adding Reference to the APx API
    clr.AddReference(
        os.path.join(os.path.dirname(__file__), 'ap_dll', 'AudioPrecision.API2.dll'))  # Adding Reference to the APx API
except:
    clr.AddReference(r"D:\AudioPrecision.API2.dll")  # Adding Reference to the APx API
    clr.AddReference(r"D:\AudioPrecision.API.dll")  # Adding Reference to the APx API
