# Libraries
from time import sleep
import shutil
from ..classes.CustomTqdm import CustomTqdm
from colorama import Fore
import pandas as pd

# Dataset Manager Class
class DatasetManager:
    def __init__(self, data, headers):
        self.df = pd.DataFrame(data, columns=headers)
        self.terminal_width, _ = shutil.get_terminal_size(fallback=(80, 24))
        self.dash_length = self.terminal_width - 1

    def display_loading(self):
        with CustomTqdm(total=7, 
                        ncols=self.terminal_width, 
                        bar_format="{l_bar}" + Fore.WHITE + "{bar}" + Fore.RESET + "{r_bar}") as pbar:
            for _ in range(7):
                sleep(0.2)
                pbar.update(1)

    def get_dataset_names(self):
        return self.df["DATASET"].tolist()

    def display_dataframe(self):
        pd.set_option("display.max_columns", None)
        print(self.dash_length * "_")
        print(self.df.to_string(index=False))
        print(self.dash_length * "_")

if __name__ == "__main__":
    # Sample data
    data = [
        {"ID": "1", "DATASET": "dataset 1", "VERSION": "1.0", "DATE": "5/5"},
        {"ID": "2", "DATASET": "dataset 2", "VERSION": "2.1", "DATE": "8/7"},
        {"ID": "3", "DATASET": "fire_smoke", "VERSION": "8.0", "DATE": "8/7"}
    ]

    # Corresponding headers
    headers = ["ID", "DATASET", "VERSION", "DATE"]

    manager = DatasetManager(data, headers)
    manager.display_loading()
    manager.display_dataframe()
