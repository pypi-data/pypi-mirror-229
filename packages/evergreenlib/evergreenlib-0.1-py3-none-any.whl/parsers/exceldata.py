import win32com.client as client
import pandas as pd
from pywintypes import com_error
import time
from pathlib import Path
from evergreenlib.clean.cleaner import DataframeCleaner 


from win32com.client import makepy
makepy.GenerateFromTypeLibSpec('Excel.Application')

class ExcelParser:
    """
    This class should be reading data from .xlsx files
    """

    def __init__(self, filepath:str, sheet_name:str, index_value:str):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.index_value = index_value


    def read_data(self):
        start = time.perf_counter() 
        try:
            xlapp = client.GetActiveObject('Excel.Application')
            print("There is current Excel instance running on your machine. No need to initialize new instance")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value

        except com_error as e:
            if e.args[1] == 'Operation unavailable':
                print("Initializing new Excel Instance as there is no current one running on your machine")
            xlapp = client.gencache.EnsureDispatch('Excel.Application')
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
        df = pd.DataFrame(used_rng)
        wkb.Close(SaveChanges=False)
        xlapp.Quit()             
        cleaner = DataframeCleaner(df)
        if self.index_value == 'Rus Account':
            cleaner.adj_by_row_index(value=self.index_value)
        else:
            cleaner.adj_by_row_index(value=self.index_value)
            cleaner.remove_duplicated_cols()


        end = time.perf_counter() 
        print(
            f'Reading file {Path(self.filepath).name} '
            f'from file: {Path(__file__).name} took {round((end - start), 2)} seconds'
        )

        return cleaner.df  

class ExcelParser_retain_duplicates:
    """
    This class should be reading data from .xlsx files
    """

    def __init__(self, filepath:str, sheet_name:str, index_value:str):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.index_value = index_value


    def read_data(self):
        start = time.perf_counter() 
        try:
            xlapp = client.GetActiveObject('Excel.Application')
            print("There is current Excel instance running on your machine. No need to initialize new instance")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value

        except com_error as e:
            if e.args[1] == 'Operation unavailable':
                print("Initializing new Excel Instance as there is no current one running on your machine")
            xlapp = client.gencache.EnsureDispatch('Excel.Application')
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
        df = pd.DataFrame(used_rng)
        wkb.Close(SaveChanges=False)
        xlapp.Quit()             
        cleaner = DataframeCleaner(df)
        if self.index_value == 'Rus Account':
            cleaner.adj_by_row_index(value=self.index_value)
        else:
            cleaner.adj_by_row_index(value=self.index_value)
            # cleaner.remove_duplicated_cols()


        end = time.perf_counter() 
        print(
            f'Reading file {Path(self.filepath).name} '
            f'from file: {Path(__file__).name} took {round((end - start), 2)} seconds'
        )

        return cleaner.df  


if __name__ == '__main__':
    x = ExcelParser_retain_duplicates(
        r"V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD07_2023\Оборотно-сальдовая ведомость за January 2023 - July 2023 ООО  ХЕНДЭ МОБИЛИТИ ЛАБ.xls",
        'TDSheet',
        'Счет')
    print(x.read_data())