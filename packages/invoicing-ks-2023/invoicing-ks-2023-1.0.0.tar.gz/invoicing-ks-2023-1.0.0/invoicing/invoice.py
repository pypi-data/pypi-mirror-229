import pandas as pd
import glob
import os
from fpdf import FPDF
from pathlib import Path


def generate(invoices_path, pdfs_path, image_path, product_id, product_name, amount_purchased, price_per_unit,
             total_price):
    """
    This function converts invoice Excel files into PDF invoices.
    :param invoices_path:
    :param pdfs_path:
    :param product_id:
    :param image_path:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :return:
    """

    filepaths = glob.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=False, margin=0)

        pdf.add_page()
        filename = Path(filepath).stem
        invoice_nr, invoice_date = filename.split("-")
        pdf.set_font(family="Times", style="B", size=16)
        pdf.cell(w=20, h=8, txt=f"Invoice nr: {invoice_nr}", align="L", ln=1)

        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=20, h=8, txt=f"Date: {invoice_date.replace('.', '-')}", align="L", ln=1)

        df = pd.read_excel(filepath, sheet_name="Sheet 1")
        # Header
        table_header = list(df.columns)
        pdf.set_font(family="Times", size=12, style="B")
        pdf.cell(w=30, h=8, txt=table_header[0].title().replace("_", " "), border=1)
        pdf.cell(w=60, h=8, txt=table_header[1].title().replace("_", " "), border=1)
        pdf.cell(w=40, h=8, txt=table_header[2].title().replace("_", " "), border=1)
        pdf.cell(w=30, h=8, txt=table_header[3].title().replace("_", " "), border=1)
        pdf.cell(w=30, h=8, txt=table_header[4].title().replace("_", " "), border=1, ln=1)

        # Read Excel Files
        for index, row in df.iterrows():
            pdf.set_font(family="Times", size=12)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=60, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=40, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        total_sum = df[total_price].sum()
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=60, h=8, txt="", border=1)
        pdf.cell(w=40, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), ln=1, border=1)

        # Total Sum
        pdf.set_font(family="Times", size=12, style="B")
        pdf.cell(w=60, h=8, txt=f"The total price is {total_price} euros", ln=1)

        # Add Company Name and Logo
        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=28, h=8, txt="Python Now")
        pdf.image(image_path, w=10)

        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)

        pdf.output(f"{pdfs_path}/{filename}.pdf")
