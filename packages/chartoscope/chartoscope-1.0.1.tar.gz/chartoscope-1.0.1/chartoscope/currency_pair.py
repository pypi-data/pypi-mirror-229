import ctypes
from .global_constants import *
from enum import Enum

class CurrencyPairItem():
        def __init__(self, symbol):                
                chartoscope_dll = ctypes.cdll.LoadLibrary(GlobalConstants.default_lib_path)
                chartoscope_dll.CsCurrencyPair_init()
                encoded_symbol = symbol.encode('utf-8')
                self.id = chartoscope_dll.CsCurrencyPair_get_id(ctypes.c_char_p(encoded_symbol))
                self.symbol = symbol

class CurrencyPair(Enum):
        EURUSD = CurrencyPairItem("EURUSD")
        GBPUSD = CurrencyPairItem("GBPUSD")
