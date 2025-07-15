
import os
from pathlib import Path
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv
load_dotenv()

def get_latest_report_path():
    """Get the path to the latest report file."""
    # reports_dir = Path(__file__).parent.parent / "tradingagents" / "reports"
    reports_dir = DEFAULT_CONFIG["report_dir"]
    files = os.listdir(reports_dir)
    files = [f for f in files if f.endswith(".md") or f.endswith(".pdf")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
    if files:
        return os.path.join(reports_dir, files[0])
    return None

def send_email_with_body(body: str):
    """Send an email with the body content."""
    smtp_server    = os.getenv("SMTP_SERVER")
    smtp_port      = int(os.getenv("SMTP_PORT", 587))
    sender_email   = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password       = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Warning - From Crypto Trading Agents"
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully with body content.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email_with_pdf(file_path: str):
    """Send an email with the file attached."""
    if not file_path or not os.path.exists(file_path) or not file_path.endswith(".pdf"):
        print("No report file found to send or file is not a PDF.")
        return

    smtp_server    = os.getenv("SMTP_SERVER")
    smtp_port      = int(os.getenv("SMTP_PORT", 587))
    sender_email   = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password       = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Latest Trading Report - From Crypto Trading Agents"
    message.attach(MIMEText("Report attached.", "plain"))

    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "pdf")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file_path)}",
        )
        message.attach(part)
    print(f"Preparing to send email with attachment: {file_path}")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent successfully with attachment: {file_path}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
def send_email_with_markdown(file_path: str):
    """Send an email with the markdown file content."""
    if not file_path or not os.path.exists(file_path) or not file_path.endswith(".md"):
        print("No report file found to send or file is not a Markdown file.")
        return

    smtp_server    = os.getenv("SMTP_SERVER")
    smtp_port      = int(os.getenv("SMTP_PORT", 587))
    sender_email   = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password       = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Latest Trading Report - From Crypto Trading Agents"
    message.attach(MIMEText("Report attached.", "plain"))

    with open(file_path, "rb") as attachment:
        part = MIMEBase("text", "plain")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file_path)}",
        )
        message.attach(part)
    print(f"Preparing to send email with attachment: {file_path}")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent successfully with attachment: {file_path}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send():
    print("Sending latest report via email...")
    print("Environment variables: ")
    print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
    print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
    print(f"SENDER_EMAIL: {os.getenv('SENDER_EMAIL')}")
    print(f"RECEIVER_EMAIL: {os.getenv('RECEIVER_EMAIL')}")
    print(f"EMAIL_PASSWORD: {'*' * len(os.getenv('EMAIL_PASSWORD', ''))}")

    print("Searching for the latest report...")
    report_path = get_latest_report_path()
    if not report_path:
        print("No report file found.")
        exit(1)

    print(f"Latest report found: {report_path}")
    if report_path.endswith(".pdf"):
        send_email_with_pdf(report_path)
    else:
        send_email_with_markdown(report_path)