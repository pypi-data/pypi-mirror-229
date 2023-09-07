import base64
import os.path
import smtplib
import uuid
import random
from email.mime.text import MIMEText

from bson import ObjectId
from fastapi import Header
from fastapi import HTTPException, Cookie, Request, Header

from elemental_engine.config import app_config
from elemental_engine.collections.email.smtp_config import smtp_config
from elemental_engine.handlers import binaries

class email:

	def __init__(self, smtp_email, smtp_password, smtp_server, smtp_port, sender=None, destination=None):
		self.sender = sender
		self.destination = destination
		self.smtp_email = smtp_email
		self.smtp_password = smtp_password
		self.smtp_server = smtp_server
		self.smtp_port = smtp_port

	def check_config(self):
		try:
			# Connect to the SMTP server
			smtpServer = smtplib.SMTP(self.smtp_server, int(self.smtp_port))
			smtpServer.starttls()
			try:
				smtpServer.login(self.smtp_email, self.smtp_password)
			except:
				raise Exception("Your smtp looks fine, maybe the problem is on your login information.")

			return True

		except Exception as e:
			raise Exception(f"Error registering e-mail: {e}")

	def send_email(self, subject, message):
		msg = MIMEText(message)
		msg['From'] = self.sender
		msg['To'] = self.destination
		msg['Subject'] = subject

		try:
			# Connect to the SMTP server
			smtpServer = smtplib.SMTP(host=self.smtp_server, port=self.smtp_port)
			smtpServer.starttls()
			# Login to the server
			smtpServer.login(self.smtp_email, self.smtp_password)
			# Send the email
			print(smtpServer.sendmail(self.smtp_email, self.destination, msg.as_string()))
			return {'message': 'E-mail sent successfully.'}

		except Exception as e:
			raise Exception(f"Error sending email: {e}")

class token:

	def generate(length: int):
		token = uuid.uuid4().bytes
		return base64.urlsafe_b64encode(token).rstrip(b'=').decode('utf-8')

	def auth(self, app_key: str = Header(title='Application secret obtained registering.'), app_secret: str = Header(title='Application secret obtained registering.')):

		valid_token = None

		valid_refresh_token_condition = {
			"_id": ObjectId(app_key),
			'app_secret': str(app_secret)
		}

		valid_user = smtp_config().find_one(valid_refresh_token_condition)

		if valid_user is not None:
			result = valid_user
			return result
		else:
			raise HTTPException(status_code=401, detail='Invalid access information.')
