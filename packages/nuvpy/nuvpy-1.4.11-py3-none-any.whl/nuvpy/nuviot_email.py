import os
import json
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

from sendgrid.helpers.mail.attachment import Attachment
import base64
from sendgrid.helpers.mail.file_content import FileContent
from sendgrid.helpers.mail.file_type import FileType
from sendgrid.helpers.mail.file_name import FileName
from sendgrid.helpers.mail.disposition import Disposition

reports_from_name = os.environ.get('Smtp__FromName')
reports_from_email = os.environ.get('Smtp__FromAddress')
sendgrid_api_key = os.environ.get('Smtp__Token')

job_server = os.environ.get('JOB_SERVER_URL')

def send_report_to_distribution(distribution_list_id, file_with_path, file_name, msg_subject, msg_content):
    """
    Sends a report/file to a distribution list as identified within NuvIot.

    Parameters
    ----------
    distribution_list_id : string
        distribution list identifier to download

    file_with_path : string
        entire path including file, used to load report output

    file_name : string
        name of the file, used to name the file as it is attached to the email

    msg_subject : string
        subject fo the message to be sent

    msg_content : string
        content to be included in the message
    """

    getJobUri = job_server + '/api/distro/' + distribution_list_id

    r = requests.get(getJobUri)
    if(r.status_code > 299):
        raise Exception("Could not get distribution list with id=%s " % (distribution_list_id))

    distro_list = json.loads(r.text)
    print(distro_list)

    for email in distro_list:
        send_report(email, file_with_path, file_name, msg_subject, msg_content)
  
def send_report(to_email_address, file_with_path, file_name, msg_subject, msg_content):
    """
    Sends a report/file to an email address

    Parameters
    ----------
    to_email_address : string
        email address to send the file

    file_with_path : string
        entire path including file, used to load report output

    file_name : string
        name of the file, used to name the file as it is attached to the email

    msg_subject : string
        subject fo the message to be sent

    msg_content : string
        content to be included in the message
    """

    message = Mail(
        from_email=Email(reports_from_email, reports_from_name),
        to_emails=to_email_address,
        subject=msg_subject,
        html_content=msg_content)

    with open(file_with_path, 'rb') as f:
        data = f.read()
        f.close()

    encoded_file = base64.b64encode(data).decode()

    message.attachment = Attachment(FileContent(encoded_file), FileName(file_name), FileType('application/pdf'), Disposition('attachment'))

    sg = SendGridAPIClient(sendgrid_api_key)
    response = sg.send(message)
    if(response.status_code >= 200 and response.status_code < 300):
        print("success sending: " + file_with_path + " to " + to_email_address + " ok")
    else:
        print("could not send email")
        print(response.status_code, response.body, response.headers)
