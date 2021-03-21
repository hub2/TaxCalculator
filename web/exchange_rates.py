import csv
import datetime
from typing import Dict
from decimal import Decimal
import re


class Exchange:
    def __init__(self, file_name: str = "archiwum_tab_a_2020.csv"):
        self.nbp_day_ratios = {} #"WALUTA" -> [data] -> value]

        with open(file_name, "r") as f:
            reader = csv.reader(f, delimiter=';')
            self.header = next(reader)

            rows = list(reader)
            for i, currency_header in enumerate(self.header[1:-3]):
                groups = re.search(r"([0-9]+)(.*)", currency_header).groups()
                currency_name, multiplicator = groups[1], int(groups[0])
                self.nbp_day_ratios[currency_name] = {}
                for row in rows:
                    date = datetime.datetime.strptime(row[0], '%Y%m%d')
                    # print(date)
                    self.nbp_day_ratios[currency_name][date] = float(row[i+1].replace(",",".")) / multiplicator


    def ratio(self, day: datetime.datetime, currency: str, n: int = 15) -> Decimal:
        day = day - datetime.timedelta(days=1)
        day_with_no_hours = day.replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            return self.nbp_day_ratios[currency][day_with_no_hours]
        except KeyError as e:
            if n <= 0:
                raise e
            return self.ratio(day, currency,  n=n-1)