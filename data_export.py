from pyexcelerate import Workbook


def export_data(
    file_name,
    aging_data,
    cvs_before,
    cvs_after,
    eis_before,
    eis_after,
):

    export_wb = Workbook()

    if aging_data:

        values = [aging_data.ccd_curves.columns] + list(aging_data.ccd_curves.values)
        export_wb.new_sheet(f"Aging Data CCD curves", data=values)

        values2 = [aging_data.aging_df.columns] + list(aging_data.aging_df.values)
        export_wb.new_sheet(f"Aging Data", data=values2)

    if cvs_before:
        for key in cvs_before:
            values = [cvs_before[key].cvs_df.columns] + list(
                cvs_before[key].cvs_df.values
            )
            export_wb.new_sheet(f"CVs before aging {key} mV/s", data=values)

    if cvs_after:
        for key in cvs_after:
            values = [cvs_after[key].cvs_df.columns] + list(
                cvs_after[key].cvs_df.values
            )
            export_wb.new_sheet(f"CVs after aging {key} mV/s", data=values)

    if eis_before:
        for key in eis_before:
            values = [eis_before[key].eis_df.columns] + list(
                eis_before[key].eis_df.values
            )
            export_wb.new_sheet(f"EIS before aging {key}", data=values)

    if eis_after:
        for key in eis_after:
            values = [eis_after[key].eis_df.columns] + list(
                eis_after[key].eis_df.values
            )
            export_wb.new_sheet(f"EIS after aging {key}", data=values)

    export_wb.save(f"{file_name}")
