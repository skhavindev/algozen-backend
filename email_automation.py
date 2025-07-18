import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
import os
import pandas as pd

# Editable paths
folder_path = 'sample_pdf_folder'
excel_path = 'sample_contacts.xlsx'

# Function to send email with attachment

def send_email(to_email, subject, body, attachment_path):
    from_email = 'your_email@example.com'  # Replace with your email
    from_password = 'your_password'  # Replace with your email password or app password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    part = MIMEBase('application', 'octet-stream')
    with open(attachment_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
    msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f'Email sent to {to_email} with attachment {os.path.basename(attachment_path)}')
    except Exception as e:
        print(f'Failed to send email to {to_email}. Error: {e}')


# Read Excel file

df = pd.read_excel(excel_path)

# Iterate through each row and send the corresponding PDF
for index, row in df.iterrows():
    email = row['contact email']
    id_value = row['id']
    # Construct the PDF file name pattern
    # Assuming the PDF file name contains the id_value and date range
    # We will find the PDF file that contains the id_value in its name
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf') and str(id_value) in f]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        # Uncomment the next line to actually send emails
        # send_email(email, 'Your PDF Document', 'Please find the attached PDF document.', pdf_path)
        print(f'Would send email to {email} with attachment {pdf_file}')
