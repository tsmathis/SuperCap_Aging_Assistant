import pandas as pd


def export_data(
    file_name,
    aging_data,
    cvs_before,
    cvs_after,
    eis_before,
    eis_after,
):

    writer = pd.ExcelWriter(f"{file_name}", engine="xlsxwriter")
    workbook = writer.book
    header_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
        }
    )

    if aging_data:
        aging_data.ccd_curves.to_excel(
            writer,
            sheet_name="Aging Data CCD curves",
            startrow=1,
            header=False,
            index=False,
        )
        worksheet = writer.sheets["Aging Data CCD curves"]
        for col_num, value in enumerate(aging_data.ccd_curves.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)

        aging_data.aging_df.to_excel(
            writer, sheet_name="Aging Data", startrow=1, header=False, index=False
        )
        worksheet = writer.sheets["Aging Data"]
        for col_num, value in enumerate(aging_data.aging_df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)

    if cvs_before:
        for key in cvs_before:
            cvs_before[key].cvs_df.to_excel(
                writer,
                sheet_name=f"CVs before aging {key} mV_s",
                startrow=1,
                header=False,
                index=False,
            )
            worksheet = writer.sheets[f"CVs before aging {key} mV_s"]
            for col_num, value in enumerate(cvs_before[key].cvs_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

    if cvs_after:
        for key in cvs_after:
            cvs_after[key].cvs_df.to_excel(
                writer,
                sheet_name=f"CVs after aging {key} mV_s",
                startrow=1,
                header=False,
                index=False,
            )
            worksheet = writer.sheets[f"CVs after aging {key} mV_s"]
            for col_num, value in enumerate(cvs_after[key].cvs_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

    if eis_before:
        for key in eis_before:
            eis_before[key].eis_df.to_excel(
                writer,
                sheet_name=f"EIS before aging {key}",
                startrow=1,
                header=False,
                index=False,
            )
            worksheet = writer.sheets[f"EIS before aging {key}"]
            for col_num, value in enumerate(eis_before[key].eis_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

    if eis_after:
        for key in eis_after:
            eis_after[key].eis_df.to_excel(
                writer,
                sheet_name=f"EIS after aging {key}",
                startrow=1,
                header=False,
                index=False,
            )
            worksheet = writer.sheets[f"EIS after aging {key}"]
            for col_num, value in enumerate(eis_after[key].eis_df.columns.values):
                worksheet.write(0, col_num, value, header_format)

    writer.save()
