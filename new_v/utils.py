from datetime import datetime


def get_date_range_input() -> tuple:
    start_date = get_date_input("Enter start date (DD/MM/YYYY) or press Enter for all dates: ")
    end_date = get_date_input("Enter end date (DD/MM/YYYY) or press Enter for all dates: ")
    return start_date, end_date


def get_date_input(prompt: str) -> datetime.date:
    while True:
        date_str = input(prompt)
        if date_str == "":
            return None
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY or press Enter to skip.")