import time

import pandas as pd
import win32com.client as client
from cleaninputdata.clean import DataframeCleaner

pd.options.display.width = None


class ExcelParser:
    def __init__(self, *args: list[str:str:str]):
        start = time.perf_counter()
        self.xlapp = client.Dispatch('Excel.Application')
        self.wkb = self.xlapp.Workbooks.Open(args[0], ReadOnly=True,
                                             UpdateLinks=False)
        self.sht = self.wkb.Sheets[args[1]]
        self.used_rng = self.sht.UsedRange.Value
        self.df = pd.DataFrame(self.used_rng)
        self.cleaner = DataframeCleaner(self.df)
        self.cleaner = self.cleaner.adj_by_row_index(args[2])
        self.xlapp.Quit()
        self.wkb.Close()
        end = time.perf_counter()
        print(end - start)


if __name__ == '__main__':
    x = ExcelParser(
        r"V:\Accounting\Work\Мерц\2023\3 квартал\Июль 2023\Отчетность\!Начисление МСФО_июль 2023.xlsx",
        'для if загрузки',
        'Отдел инициатор')

    print(x.cleaner)
