import gspread
import pandas as pd


def projects(creds):
    file_id = '1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ'

    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(0)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def projects_finance(creds):
    file_id = '1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ'

    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(1)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def organizations(creds):
    file_id = '1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg'

    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(0)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def organizations_finance(creds):
    file_id = '1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg'

    gc = gspread.authorize(creds)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(1)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def isvav_projects():
    df = pd.read_csv('https://www.isvavai.cz/dokumenty/open-data/CEP-projekty.csv')
    return df


def isvav_organizations():
    df = pd.read_csv('https://www.isvavai.cz/dokumenty/open-data/CEP-ucastnici.csv')
    return df
