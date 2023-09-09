import gspread
import pandas as pd


def gs_load_projects(creds):
    file_id = '1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ'

    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(0)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df
