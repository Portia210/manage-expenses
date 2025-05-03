# main.py

import pandas as pd
from utils.data_cleaning import clean_data, improve_data
from utils.generate_full_excel import generate_full_excel


def main():
    # Load and process data
    raw_data = pd.read_excel('bank.xlsx', header=None)
    cleaned_data = clean_data(raw_data)
    improved_data = improve_data(cleaned_data)
    generate_full_excel(improved_data)




if __name__ == "__main__":
    main()

