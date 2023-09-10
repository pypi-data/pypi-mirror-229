import os
import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path


def generate(input_path, output_path, image_path, product_id, product_name, amount_purchased, price_per_unit, total_price):
    """
    This function converts invoice Excel files into PDF invoices
    :param input_path:
    :param output_path:
    :param image_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :return:
    """
    filepaths = glob.glob(f"{input_path}/*.xlsx")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for filepath in filepaths:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        filename = Path(filepath).stem
        invoice_nr, date = filename.split("-")
        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_nr}", ln=1)
        pdf.cell(w=50, h=8, txt=f"Date {date}", ln=1)

        pdf.ln(8)

        # Add header
        pdf.set_font(family="Times", size=10, style="B")
        df = pd.read_excel(filepath, sheet_name="Sheet 1")
        columns = list(df.columns)
        columns = [item.replace("_", " ").title() for item in columns]

        pdf.cell(w=30, h=8, txt=columns[0], border=1)
        pdf.cell(w=75, h=8, txt=columns[1], border=1)
        pdf.cell(w=33, h=8, txt=columns[2], border=1)
        pdf.cell(w=30, h=8, txt=columns[3], border=1)
        pdf.cell(w=30, h=8, txt=columns[4], border=1, ln=1)

        # Add rows
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)
        for index, row in df.iterrows():
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=75, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=33, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        total = df[total_price].sum()
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=75, h=8, txt="", border=1)
        pdf.cell(w=33, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total), border=1, ln=1)

        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=30, h=8, txt=f"The total price is ${total}", ln=1)
        pdf.cell(w=50, h=8, txt="Blackhawk Technology Group")
        pdf.image(image_path, w=10)

        pdf.output(f"{output_path}/{filename}.pdf")
