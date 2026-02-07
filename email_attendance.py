import pandas as pd
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# -------- CONFIGURATION --------

SUBJECT = "Attendance Alert"

BODY_TEMPLATE = """Dear Parent or Student,

This is an automated attendance notification.

Our records show that {Name} was marked ABSENT today.

Date: {Date}

Please ensure regular attendance.
Regular attendance is essential for academic progress and discipline.  
Kindly ensure that necessary steps are taken to maintain consistent attendance.

This is a system-generated email. Please do not reply.

Regards  
School Administration"""

ATTENDANCE_FILE = "attendance_logs/Attendance.csv"
MASTER_LIST_FILE = "master_list.csv"

# ------------------------------


def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES
    )

    creds = flow.run_local_server(port=0, open_browser=True)
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(to, subject, body):
    msg = MIMEMultipart()
    msg['to'] = to
    msg['subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}


def send_emails():
    print("Starting Gmail authentication...")
    service = authenticate_gmail()

    try:
        df = pd.read_csv(ATTENDANCE_FILE)
    except:
        print("Attendance file not found!")
        return

    try:
        master_df = pd.read_csv(MASTER_LIST_FILE)
    except:
        print("master_list.csv not found!")
        return

    print("Processing absentees...")

    absent_df = df[df['Status'] == 'Absent']

    if absent_df.empty:
        print("No absentees today. No emails sent.")
        return

    for _, row in absent_df.iterrows():
        name = row['Name']
        date = row['Date']

        # REAL EMAIL MAPPING FROM MASTER LIST
        email_row = master_df[
            master_df['Name'].str.strip().str.lower() == name.strip().lower()
        ]

        if email_row.empty:
            print(f"No email found for: {name}")
            continue

        email = email_row.iloc[0]['Email']

        body = BODY_TEMPLATE.replace("{Name}", name).replace("{Date}", date)

        message = create_message(email, SUBJECT, body)

        try:
            service.users().messages().send(userId='me', body=message).execute()
            print(f"Email sent to: {name} -> {email}")
        except Exception as e:
            print(f"Failed to send to {email}: {str(e)}")

    print("All absentee emails processed.")


if __name__ == '__main__':
    send_emails()
