from fpdf import FPDF
import io

def create_mission_pdf(mission_data) -> bytes:
    """Generates a PDF report for a completed mission."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Mission Report: {mission_data.call_sign}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Status: {mission_data.final_status}", ln=True)
    # ... add more details to the PDF
    return pdf.output(dest='S').encode('latin-1')

def create_mission_csv(alerts_data) -> io.StringIO:
    """Generates a CSV of alerts triggered during a mission."""
    output = io.StringIO()
    # In a real app, use the `csv` module to write data
    output.write("timestamp,severity,message\n")
    for alert in alerts_data:
        output.write(f"{alert['timestamp']},{alert['severity']},{alert['message']}\n")
    output.seek(0)
    return output