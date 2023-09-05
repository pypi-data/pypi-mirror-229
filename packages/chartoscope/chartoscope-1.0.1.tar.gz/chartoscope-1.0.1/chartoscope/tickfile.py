import ctypes
import os
from .global_constants import *
from .currency_pair import CurrencyPair

class TickFileHeader(ctypes.Structure):
        _fields_ = [('ticker_symbol', ctypes.c_char * 6),
                ('record_count', ctypes.c_long),
                ('beginning_timestamp', ctypes.c_size_t),
                ('ending_timestamp', ctypes.c_size_t),
                ('checksum', ctypes.c_longlong)
                ]

class TickFileItem(ctypes.Structure):
        _fields_ = [('timestamp', ctypes.c_size_t),
                ('bid', ctypes.c_float),
                ('ask', ctypes.c_float)
                ]        
                
                
class TickFile():
        @staticmethod
        def open_for_reading(currency_pair_enum, working_directory = '.'):
                chartoscope_dll = ctypes.cdll.LoadLibrary(GlobalConstants.default_lib_path)
                tick_file = chartoscope_dll.CsTickFile_init()
                file_path = os.path.abspath(os.path.join(working_directory, f'{currency_pair_enum.value.symbol}.tck'))
                encoded_path = file_path.encode('utf-8')
                chartoscope_dll.CsTickFile_open_for_reading(tick_file, ctypes.c_char_p(encoded_path))
                return TickFileReader(chartoscope_dll, tick_file)
        @staticmethod
        def open_for_writing(currency_pair_enum, working_directory = '.'):
                chartoscope_dll = ctypes.cdll.LoadLibrary(GlobalConstants.default_lib_path)
                chartoscope_dll.CsTickFile_init.restype = ctypes.c_void_p
                tick_file = chartoscope_dll.CsTickFile_init()                
                encoded_symbol = currency_pair_enum.value.symbol.encode('utf-8')                
                chartoscope_dll.CsTickFile_open_for_writing(tick_file, ctypes.c_char_p(encoded_symbol))
                return TickFileWriter(chartoscope_dll, tick_file)
                        

class TickFileReader():
        def __init__(self, chartoscope_dll, file_handle):
                self.chartoscope_dll = chartoscope_dll
                self.file_handle = file_handle
                self.chartoscope_dll.CsTickFile_header.restype = ctypes.c_void_p
                self.header = TickFileHeader.from_address(self.chartoscope_dll.CsTickFile_header(file_handle))
                self.is_open = True
        def __enter__(self):                
                return self
        def __exit__(self, exc_type, exc_value, exc_traceback):
                self.close()                
        def read(self):
                self.chartoscope_dll.CsTickFile_read.restype = ctypes.c_void_p
                return TickFileItem.from_address(self.chartoscope_dll.CsTickFile_read(self.file_handle))
        def block_read(self, block_size = 10000):
                self.chartoscope_dll.CsTickFileItemBlock_init(self.file_handle);
                items_read = self.chartoscope_dll.CsTickFile_block_read(self.file_handle);
                items = []
                self.chartoscope_dll.CsTickFileItemBlock_read.restype = ctypes.c_void_p
                for i in range(0, items_read-1):                        
                        items.append(TickFileItem.from_address(self.chartoscope_dll.CsTickFileItemBlock_read(self.file_handle, i)))
                        
                self.chartoscope_dll.CsTickFileItemBlock_deinit(self.file_handle);
                return items        
        def create_item(self, ts_datetime, ts_milliseconds, bid, ask):                
                tick_file_item = TickFileItem()
                tick_file_item.timestamp.datetime = ts_datetime
                tick_file_item.timestamp.milliseconds = ts_milliseconds
                tick_file_item.bid = bid
                tick_file_item.ask = ask
                return tick_file_item
        def close(self):
                if self.is_open:
                        self.chartoscope_dll.CsTickFile_close(self.file_handle);
                        self.chartoscope_dll.CsTickFile_deinit(self.file_handle);
                        self.is_open = False
        

class TickFileWriter():
        def __init__(self, chartoscope_dll, file_handle):                
                self.chartoscope_dll = chartoscope_dll
                self.chartoscope_dll.CsTickFile_header.restype = ctypes.c_void_p                
                self.file_handle = file_handle
                self.header = TickFileHeader.from_address(self.chartoscope_dll.CsTickFile_header(self.file_handle))
                self.is_open = True
        def __enter__(self):                
                return self
        def __exit__(self, exc_type, exc_value, exc_traceback):
                self.close()                
        def block_write(self, tick_file_item_list):
                self.chartoscope_dll.CsTickFileItemBlock_init(self.file_handle);
                for tick_file_item in tick_file_item_list:
                        self.chartoscope_dll.CsTickFileItemBlock_write(self.file_handle, ctypes.c_size_t(tick_file_item.timestamp),
                                                                       ctypes.c_float(tick_file_item.bid),
                                                                       ctypes.c_float(tick_file_item.ask))
                self.chartoscope_dll.CsTickFile_block_write(self.file_handle)
                self.chartoscope_dll.CsTickFileItemBlock_deinit(self.file_handle);
        def close(self):
                if self.is_open:
                        self.chartoscope_dll.CsTickFile_rewrite_header(self.file_handle);
                        self.chartoscope_dll.CsTickFile_close(self.file_handle);
                        self.chartoscope_dll.CsTickFile_deinit(self.file_handle);
                        self.is_open = False
                


