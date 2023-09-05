import ctypes
from .global_constants import *
from enum import Enum

class CurrencyItem():
        def __init__(self, symbol):                
                chartoscope_dll = ctypes.cdll.LoadLibrary(GlobalConstants.default_lib_path)
                chartoscope_dll.CsCurrencies_init()
                encoded_symbol = symbol.encode('utf-8')
                self.id = chartoscope_dll.CsCurrencies_get_id(ctypes.c_char_p(encoded_symbol))                

class Currency(Enum):
        USD = CurrencyItem("USD")
        GBP = CurrencyItem("GBP")
        EUR = CurrencyItem("EUR")
