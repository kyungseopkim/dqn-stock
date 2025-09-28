
from abc import ABC, abstractmethod
import pandas as pd

class DataSource(ABC):
    @abstractmethod
    def fetch_data(self, symbol:str, start_date:str, end_date:str ) -> pd.DataFrame:
        """Fetch data from the source."""
        pass

    @abstractmethod
    def fetch_one_day_data(self, symbol:str, date:str, interval:str) -> pd.DataFrame:
        """Fetch data for a single day."""
        pass