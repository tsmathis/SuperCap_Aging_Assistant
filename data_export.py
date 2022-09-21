from pyexcelerate import Workbook


def export_data(
    # destination,
    # aging_data=None,
    # cvs_before=None,
    # cvs_after=None,
    # eis_before=None,
    # eis_after=None,
):
    export_wb = Workbook()

    export_wb.new_sheet("Aging Data", values=None)
    export_wb.new_sheet("Aging Data", values=None)
    export_wb.new_sheet("Aging Data", values=None)
    export_wb.new_sheet("Aging Data", values=None)
    export_wb.new_sheet("Aging Data", values=None)

    export_wb.save(f"{file_name}.xlsx")


wb = Workbook()
ws = wb.new_sheet("test")
ws.range("B1", "C2").value = [[1, 2], [3, 4]]
wb.save("output.xlsx")
