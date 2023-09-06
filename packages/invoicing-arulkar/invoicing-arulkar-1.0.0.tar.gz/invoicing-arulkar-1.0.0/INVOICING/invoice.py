import os

import pandas as pd
# As we are having bnumer of files We must go with the global library/Module
import glob
# for conversion in pdf
from fpdf import FPDF
# for getting the file
from pathlib import Path


def generate(invoices_path, pdfs_path, product_id, product_name, amount_purchased, price_per_unit, total_price):
    """
    This Function Converts invoice Excel Files into Pdf  invoices
    :param invoices_path:
    :param pdfs_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :return:
    """
    # Provide The filepaths
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")
    # For Reading and then just convert it into the

    for filepath in filepaths:

        # now rest is for  pdf paper
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        # to add pages
        pdf.add_page()
        # for extracting file path
        filename = Path(filepath).stem
        # for  extracting invoice  page the extracting of this list is done by the [0]
        invoice_nr, date = filename.split("-")
        # for extraction of date
        #    invoice_nr = filename.split("-")[1] for  first methord
        # for information of font for whole page
        pdf.set_font(family="Arial", size=18, style="B")
        # for the cell  working the ln=1 shows the line  break
        pdf.cell(w=50, h=8, txt=f"Invoice nr.{invoice_nr}", ln=1)
        # for information of font for whole page
        pdf.set_font(family="Arial", size=18, style="B")
        # for the cell  working of date
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)
        # for reading the date frame
        df = pd.read_excel(filepath, sheet_name="Sheet1")
        # for adding header of column
        columns = df.columns
        columns = [item.replace("_", " ").title() for item in columns]
        pdf.set_font(family="Arial", size=8, style="I")
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt=columns[0], border=1)
        pdf.cell(w=70, h=8, txt=columns[1], border=1)
        pdf.cell(w=40, h=8, txt=columns[2], border=1)
        pdf.cell(w=30, h=8, txt=columns[3], border=1)
        pdf.cell(w=30, h=8, txt=columns[4], border=1, ln=1)

        # now extracting the data i.e.reading the file from the part
        for index, row in df.iterrows():
            pdf.set_font(family="Arial", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=40, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)
        # txt required the only str in place
        total_sum = df[total_price].sum()
        pdf.set_font(family="Arial", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=40, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=1)
        # Adding total sum Sentence
        pdf.set_font(family="Arial", size=10, style="UB")
        pdf.cell(w=30, h=8, txt=f"The Total price is {total_sum}", ln=1)
        # Adding company Name and logo
        #pdf.set_font(family="Arial", size=20, style="UB")
        #pdf.cell(w=65, h=10, txt=f"Godfather")
        #pdf.image("Company - Copy.png")

        # for saving the pdf file
        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}.pdf")
