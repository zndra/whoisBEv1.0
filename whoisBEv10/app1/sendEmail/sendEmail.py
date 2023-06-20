from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def sendMail(receiver_address, mail_subject, mail_content):
    sender_address = "mtaxapp@zohomail.com"
    sender_pass = "N32sH@fGn2NtZAn"

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = mail_subject   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('smtp.zoho.com', 465) #use gmail with port
    # session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
#   sendMail


