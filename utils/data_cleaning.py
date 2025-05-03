import pandas as pd
import re


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    # Find the header row and clean the data
    header_row = data[data.eq('תאריך').any(axis=1)].index[0]
    data_cleaned = data.iloc[header_row:].reset_index(drop=True)
    data_cleaned.columns = data_cleaned.iloc[0]
    data_cleaned = data_cleaned[1:].reset_index(drop=True)

    # remove extra spaces and new lines
    data_cleaned = data_cleaned.map(
        lambda x: re.sub(r'[\s]{2,}|\n', ' ', x) if isinstance(x, str) else x
    )
    # fill the missing values with 0
    data_cleaned[["זכות", "חובה"]] = data_cleaned[["זכות", "חובה"]].fillna(0)

    # convert the date column to proper format
    data_cleaned["תאריך"] = pd.to_datetime(data_cleaned["תאריך"]).dt.strftime("%d/%m/%Y")
    # sort the data by date
    # data_cleaned = data_cleaned.sort_values(by="תאריך", ascending=True)
    # data_cleaned.to_csv("cleaned_data.csv", index=False)
    return data_cleaned


def improve_data(df: pd.DataFrame) -> pd.DataFrame:

    # first create רווח column, and get rid of זכות and חובה
    # fill זכות and חובה with 0
    df[["זכות", "חובה"]] = df[["זכות", "חובה"]].fillna(0)
    df["רווח"] = df["זכות"] - df["חובה"]
    df.drop(columns=["זכות", "חובה"], inplace=True)
    # if פרטים is empty, then fill it with the value of הפעולה  
    df["פרטים"] = df["פרטים"].fillna(df["הפעולה"])
    # if מהות contains סיליקון, fill מהות with משכורת
    df["מהות הפעולה"] = df.apply(lambda row: 
    "משכורת" if "סיליקון" in row["פרטים"] or 'מופ"ת חובה' in row["הפעולה"] else
    "מס הכנסה" if "מס הכנסה" in row["פרטים"] else 
    "מעמ" if 'מע"מ' in row["פרטים"] else 
    "ביטוח לאומי" if "ביטוח לאומי" in row["פרטים"] else 
    "רואה חשבון" if "לטובת: רו ח" in row["פרטים"] else 
    "כרטיס אשראי" if "כאל" in row["פרטים"] or "כרטיסי אשראי" in row["פרטים"] else 
    "אחר" if "אחר" in row["פרטים"] else 
    "עמלות חשבון" if "ע.מפעולות" in row["פרטים"] else 
    # if לטובת is not empty, then fill מהות הפעולה with העברה יוצאת
    "העברה יוצאת" if row["לטובת"] is not None and row["רווח"] < 0 else
    "העברה נכנסת" if row["לטובת"] is not None and row["רווח"] > 0 else
    row["פרטים"], 
    axis=1)
    # if "לטובת" is not empty, then fill פרטים with with value is פרטים
    df["הפעולה"] = df.apply(lambda row:
    "העברה יוצאת" if not pd.isna(row["לטובת"]) and row["רווח"] < 0 else
    "העברה נכנסת" if not pd.isna(row["לטובת"]) and row["רווח"] > 0 else
    row["הפעולה"], axis=1)
    df["פרטים"] = df.apply(lambda row: row["לטובת"] if not pd.isna(row["לטובת"]) else row["פרטים"], axis=1)
    
    # keep only those columns
    df = df[["תאריך", "הפעולה", "פרטים", "מהות הפעולה", "רווח"]]
    df.to_csv("improved_data.csv", index=False)
    return df




if __name__ == "__main__":
    data = pd.read_excel("excelNewTransactions.xlsx")
    clean_data(data)

