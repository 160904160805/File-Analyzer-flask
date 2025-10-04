# analyzer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime
import json
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def read_file(filepath):
    """Detect file type and read into a Pandas DataFrame"""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(filepath)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(filepath)
    elif ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif ext == ".txt":
        df = pd.read_csv(filepath, delimiter="\t", engine="python", on_bad_lines="skip")
    elif ext == ".pdf":
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        # Convert PDF text into DataFrame (line by line)
        df = pd.DataFrame(text.splitlines(), columns=["Text"])
    else:
        raise ValueError("Unsupported file format!")

    return df


def generate_summary(df):
    """Generate summary statistics and insights"""
    summary = {
        "Shape": df.shape,
        "Columns": df.columns.tolist(),
        "Missing Values": df.isnull().sum().to_dict(),
        "Duplicates": df.duplicated().sum()
    }

    try:
        desc = df.describe(include="all").to_dict()
        summary["Statistics"] = desc
    except Exception:
        summary["Statistics"] = "Not applicable (non-numeric data)"

    return summary


def save_txt_report(summary, output_path):
    """Save summary as a TXT file"""
    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")


def save_excel_report(df, summary, output_path):
    """Save summary + data into Excel"""
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Summary", index=False)


def save_pdf_report(summary, output_path):
    """Save summary into a simple PDF report"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 10)

    y = height - 40
    c.drawString(30, y, "Data Analysis Report")
    y -= 20

    for key, value in summary.items():
        c.drawString(30, y, f"{key}: {str(value)[:100]}")  # Limit long text
        y -= 15
        if y < 40:  # New page if space runs out
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40

    c.save()


def generate_plot(df, output_folder="static"):
    """Create heatmap of missing values and save it inside static folder"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend (important for Flask)
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap="mako")
    plot_path = os.path.join("static", "plot.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    return plot_path


def analyze_file(filepath, output_folder):
    """Main function: Analyze file and return report filenames"""
    df = read_file(filepath)
    summary = generate_summary(df)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"report_{timestamp}"

    txt_report = os.path.join(output_folder, f"{base}.txt")
    excel_report = os.path.join(output_folder, f"{base}.xlsx")
    pdf_report = os.path.join(output_folder, f"{base}.pdf")

    # Save reports
    save_txt_report(summary, txt_report)
    save_excel_report(df, summary, excel_report)
    save_pdf_report(summary, pdf_report)

    # Save plot
    generate_plot(df, output_folder)

    return [os.path.basename(txt_report), os.path.basename(excel_report), os.path.basename(pdf_report)]
