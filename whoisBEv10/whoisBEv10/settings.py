from   email.mime.multipart import MIMEMultipart
from   django.http          import HttpResponse
from   smtplib              import SMTPDataError
from   email.mime.text      import MIMEText
from   datetime             import datetime
from   django.urls          import resolve
from   pathlib              import Path
import psycopg2
import hashlib
import smtplib
import base64
import random
import json
import os
# nemelt importuud 
###############################
BASE_DIR   = Path(__file__).resolve().parent.parent
t          = os.path.join(BASE_DIR, 'templates')
SECRET_KEY = 'django-insecure-#_966zao2el-7c%hqh=85b*on!y=p*6c^tr8*oo$-akm8my%+4'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*", "202.131.254.138", "192.168.0.15"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app1',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'whoisBEv10.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [t,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'whoisBEv10.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
        'default': {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME'   : BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------ start Bidnii nemsen tohiruulguud

pgDbName   = "dbwhois"
pgUser     = "uwhois"
pgHost     = "202.131.254.138"
pgPassword = "whoispass"
pgPort     = "5938"

verifyEmailSubject = "WhoIs: Имэйл баталгаажуулах"
verifyEmailContent = "Та манай системд бүртгүүлсэн байна. \n\n Доорх холбоос дээр дарж бүртгэлээ баталгаажуулна уу!\n\n"
verifyEmailLink    = "http://whois.mandakh.org/verifyEmail/"



# ------------ end Bidnii nemsen tohiruulguud

# bidnii nemsen function

## Нууц үгийг md5 хашруу хөрвүүлж байгаа
def mandakhHash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()
#   mandakhHash

## Бүртгүүлэхэд автоматаар үүсэх 5 оронтой код
def createPassword(length):
    # Random string of length 5
    result_str = ''.join((random.choice('abcdefghjkmnpqrstuvwxyz123456789$!?') for i in range(length)))
    return result_str
    # Output example: ryxay
#   createPassword

## Хэрэглэгчийн бүртгэл баталгаажуулах код үүсгэнэ. 
## 30 тэмдэгт байгаа. 
## length нь үсгийн урт
def createCodes(length):
    # Random string of length 30
    result_str = ''.join((random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length)))
    return result_str
    # Output example: ryxay
#   createCodes


def base64encode(length):
    return base64.b64encode((createCodes(length-26) + str(datetime.now().time())).encode('ascii')).decode('ascii').rstrip('=')

#   base64encode

def get_view_name_by_path(path):
    result = resolve(path=path)
    return result.view_name
#   get_view_name_by_path

def pth(request):
    return get_view_name_by_path(request.path)
#   pth

def reqValidation(json,keys):
    validReq = True
    for key in keys:
        if(key not in json):
            validReq = False
            break
    return validReq
#   def

def connectDB():
    con = psycopg2.connect(
        dbname   = pgDbName,
        user     = pgUser,
        host     = pgHost,
        password = pgPassword,
        port     = pgPort,
    )
    return con

def disconnectDB(con):
    if(con):
        con.close()
        # is email overlaped
def emailExists(email):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT COUNT(*) FROM "f_user" WHERE "email" = %s', (email,))
    result = userCursor.fetchone()
    userCursor.close()
    disconnectDB(myCon)
    return result[0] > 0
##########################################
#is username overlaped
def userNameExists(username):
    myCon      = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT COUNT(*) FROM "f_user" WHERE "userName" = %s', (username,))
    result     = userCursor.fetchone()
    userCursor.close()
    disconnectDB(myCon)
    return result[0] > 0
####################################

# def sendMail(receiver_address, mail_subject, mail_content):
#     sender_address = "mtaxapp@zohomail.com"
#     sender_pass = "N32sH@fGn2NtZAn"

#     message = MIMEMultipart()
#     message['From'] = sender_address
#     message['To'] = receiver_address
#     message['Subject'] = mail_subject  # The subject line
#     # The body and the attachments for the mail
#     message.attach(MIMEText(mail_content, 'plain'))
#     # Create SMTP session for sending the mail
#     session = smtplib.SMTP_SSL('smtp.zoho.com', 465)  # use gmail with port
#     # session.starttls() #enable security
#     session.login(sender_address, sender_pass)  # login with mail_id and password
#     text = message.as_string()
#     session.sendmail(sender_address, receiver_address, text)
#     session.quit()
# #   sendMail

def sendMail(receiver_address, mail_subject, mail_content):
    sender_address = "mtaxapp@zohomail.com"
    sender_pass    = "N32sH@fGn2NtZAn"

    message = MIMEMultipart()
    message['From']    = sender_address
    message['To']      = receiver_address
    message['Subject'] = mail_subject
    message.attach(MIMEText(mail_content, 'plain'))

    try:
        # Create SMTP session for sending the mail
        session = smtplib.SMTP_SSL('smtp.zoho.com', 465)
        session.login(sender_address, sender_pass)
        session.sendmail(sender_address, receiver_address, message.as_string())
        session.quit()

        # Create a success response
        resp = {
            'message': "Email sent successfully!"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except SMTPDataError as e:
        # Create an error response
        resp = {
            'error': "SMTPDataError occurred: " + str(e)
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except Exception as e:
        # Create an error response
        resp = {
            'error': "An error occurred: " + str(e)
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")


#   sendMail

def runQuery(query):
    myCon      = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute(query)
    result     = userCursor.fetchone()
    userCursor.close()
    disconnectDB(myCon)
    return result[0] > 0


# if runQUery("select * from users") == 0:
    
def reqValidation(json,keys):
    validReq = True
    for key in keys:
        if(key not in json):
            validReq = False
            break
    return validReq
#   def

