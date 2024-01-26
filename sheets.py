import gspread

# Open a sheet from a spreadsheet in one go
# Update a range of cells using the top left corner address
# wks.update('A1', [[1, 2], [3, 4]])
# # Or update a single cell
# wks.update('B42', "it's down there somewhere, let me take another look.")
# # Format the header
# wks.format('A1:B1', {'textFormat': {'bold': True}})

def add_to_sheets(data:list, row_id=None):
    gc = gspread.service_account()
    wks = gc.open("VetBot").sheet1
    if row_id == None:
        values_list = wks.col_values(1)
        row_id = len(values_list) + 1
    wks.update(range_name=f'A{row_id}', values=[data])
    return row_id

def add_price(price):
    gc = gspread.service_account()
    wks = gc.open("VetBot").sheet1
    values_list = wks.col_values(1)
    row_id = len(values_list) + 1
    wks.update(range_name=f'D{row_id}', values=[[price]])
