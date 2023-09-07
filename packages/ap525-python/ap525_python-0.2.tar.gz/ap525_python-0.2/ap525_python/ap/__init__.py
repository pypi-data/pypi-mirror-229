import clr
import os


clr.AddReference(os.path.join(os.path.dirname(__file__), 'ap_dll', 'AudioPrecision.API.dll'))  # Adding Reference to the APx API
clr.AddReference(os.path.join(os.path.dirname(__file__), 'ap_dll', 'AudioPrecision.API2.dll'))  # Adding Reference to the APx API
