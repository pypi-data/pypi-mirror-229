import time
import pandas as pd
import win32com.client as client
from custompacks.cleaninputdata.clean import DataframeCleaner
from pathlib import Path

from win32com.client import makepy
makepy.GenerateFromTypeLibSpec('Excel.Application')


pd.options.display.width = None

class ExcelParser:
    def __init__(self, *args: list[str:str:str]):
        self.filepath = args[0]
        self.sht = args[1]
        self.value = args[2]
    def read_data(self):
        start = time.perf_counter()
        try:
            xlapp = client.GetActiveObject("Excel.Application")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sht]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            wkb.Close(SaveChanges=False)
        except:
            xlapp = client.Dispatch('Excel.Application')
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sht]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            wkb.Close(SaveChanges=False)
            xlapp.Quit()

        cleaner = DataframeCleaner(df)
        if self.value == 'Rus Account':
            cleaner.adj_by_row_index(value=self.value)
        else:
            cleaner.adj_by_row_index(value=self.value)
            cleaner.remove_duplicated_cols()
        end = time.perf_counter()
        print(
            f'Reading file {Path(self.filepath).name} '
            f'from file: {Path(__file__).__fspath__()} took {round((end - start), 2)} seconds'
        )
        return cleaner.df


class ExcelParser_retain_duplicates:
    def __init__(self, *args: list[str:str:str]):
        self.filepath = args[0]
        self.sht = args[1]
        self.value = args[2]

    def read_data(self):
        start = time.perf_counter()
        try:
            xlapp = client.GetActiveObject("Excel.Application")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sht]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            wkb.Close(SaveChanges=False)
        except:
            xlapp = client.Dispatch('Excel.Application')
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sht]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            wkb.Close(SaveChanges=False)
            xlapp.Quit()

        cleaner = DataframeCleaner(df)
        if self.value == 'Rus Account':
            cleaner.adj_by_row_index(value=self.value)
        else:
            cleaner.adj_by_row_index(value=self.value)
        end = time.perf_counter()
        print(
            f'Reading file {Path(self.filepath).name} '
            f'from file: {Path(__file__).__fspath__()} took {round((end - start), 2)} seconds'
        )
        return cleaner.df


x = ExcelParser(
    r"V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD07_2023\Оборотно-сальдовая ведомость за January 2023 - July 2023 ООО  ХЕНДЭ МОБИЛИТИ ЛАБ.xls",
    'TDSheet',
    'Счет')

if __name__ == '__main__':

    print(x.read_data().info())