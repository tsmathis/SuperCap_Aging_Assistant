from pyexcelerate import Workbook


def export_data(
    destination,
    aging_data=None,
    cvs_before=None,
    cvs_after=None,
    eis_before=None,
    eis_after=None,
):

    aging_wb = Workbook()
    cvs_before_wb = Workbook()
    cvs_after_wb = Workbook()
    eis_before_wb = Workbook()
    eis_after_wb = Workbook()
