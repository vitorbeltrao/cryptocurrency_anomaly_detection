'''
Script to make funcs to send alert messages
in this case, in gmail

Author: Vitor Abdo
Date: Aug/2023
'''

# Import necessary packages
import logging
import smtplib

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def send_gmail_message(
        from_email: str, to_email: str, password: str, subject: str, body: str) -> None:
    '''
    Send an email using a Gmail account.

    Parameters:
        from_email (str): The sender's Gmail email address.
        to_email (str): The recipient's email address.
        password (str): The password for the Gmail account.
        subject (str): The subject of the email.
        body (str): The body of the email.

    Raises:
        smtplib.SMTPAuthenticationError: If the login credentials are incorrect.
        smtplib.SMTPException: If there is an issue sending the email.

    Note:
        Before using this function, make sure you enable 'Allow less secure apps'
        on your Gmail account or use App Passwords if you have two-step verification enabled.
    '''
    try:
        # connect to the SMTP server and login
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)

            # create the message and send the email
            message = f'Subject: {subject}\n\n{body}'
            server.sendmail(from_email, to_email, message)
            logging.info(f"Email sent successfully to {to_email}")

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Authentication error while sending email: {str(e)}")
        raise  # Reraise the exception to notify the calling code about authentication failure

    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {str(e)}")
        # Catch SMTPException and raise a custom exception with more meaningful information
        raise RuntimeError("Failed to send email. Please check the logs for more details.")
