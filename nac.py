#coding: utf-8

'''

set FROM_EMAIL='test@gmail.com'
set FROM_PWD='test'
set IMAP_SERVER='imap.gmail.com'

Usage: python nac.py

'''


import imaplib
import os, sys, time
from pprint import pprint as pp
e=sys.exit
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import message
#message.EmailMessage import iter_parts

import smtplib

FROM_EMAIL  = os.environ.get('FROM_EMAIL').strip("'")
FROM_PWD 	= os.environ.get('FROM_PWD').strip("'")
IMAP_SERVER = os.environ.get('IMAP_SERVER').strip("'")

assert FROM_EMAIL
assert FROM_PWD
assert IMAP_SERVER

#Delete all emails with "Subject" or "Body" containing these tags
kws  = ['QlikView', 'Garden City, NY', 'Arizona', 'Washington DC', 'Hadoop Admin', 'Branchburg, NJ', 'Whippany, NJ']

#Label all emails with "From" containing these tags
lbls = ['Etsy']
		
keep = ['New York']
		
		
def get_body(msg): 
	if msg.is_multipart(): 
		return get_body(msg.get_payload(0)) 
	else: 
		return str(msg.get_payload(None, True).replace(str.encode(os.linesep), b''))
def get_subject(msg): 	
		return msg.get('Subject').replace(os.linesep, '')
def get_emails(result_bytes): 
	msgs = [] 
	for num in result_bytes[0].split(): 
		typ, data = con.fetch(num, '(RFC822)') 
		msgs.append(data) 

def delete_message(mail, id):	
	mail.store(id, '+X-GM-LABELS', '\\Trash')
	#mail.store(id, '+FLAGS', '\\Deleted')
	#mail.expunge()
	#mail.close()

def label_message(mail, id, label):	
	mail.store(id, '+X-GM-LABELS', '\\%s' % label)
	
def delete_trash(mail):
	#time.sleep(5)
	out = mail.select('[Gmail]/Trash')  # select all trash
	assert out[0]  == 'OK'
	if len(out[1]) > 0:
		
		mail.store("1", '+FLAGS', '\\Deleted')
		print ('Trash deleted (%s)' % len(out[1]))
		mail.expunge()	
		
		
	else:
		print ('Trash is empty')
		time.sleep(1)
		
		
	
def delete_from_inbox():

		mail = imaplib.IMAP4_SSL(IMAP_SERVER)
		mail.login(FROM_EMAIL,FROM_PWD)
		mail.select('inbox')

		typ, data = mail.search(None, 'ALL')
		mail_ids = data[0]

		id_list = mail_ids.split()   
		first_email_id = int(id_list[0])
		latest_email_id = int(id_list[-1])

		subj=body=frm=None
		for i in mail_ids.split():
			deleted = False
			typ, data = mail.fetch(i, '(RFC822)' )

			for response_part in data:
				if isinstance(response_part, tuple):
					
					msg = email.message_from_bytes(response_part[1])
					subj = get_subject(msg).upper()
					body = get_body(msg).upper()
					frm  = msg.get('From').upper()
					
				
					if 1:
						for kw in kws:
							if kw.upper() in subj:
								print (int(i), 'Subj "%s"' % kw)
								deleted = True
								
							elif kw.upper() in body:
								print (int(i), 'Body "%s"' % kw)
								deleted = True

							else:
								pass
			if deleted: 
				if any(list(map(lambda x: x.upper() in subj or x.upper() in body, keep))):
					print (i, 'Keep "%s"' % x) 
				else:
					delete_message(mail, i)
					delete_trash(mail)
					deleted = False
			else:
				for lbl in lbls:
					if lbl.upper() in frm:
						print('Label "%s"' % lbl,  frm)							
						label_message(mail, i, lbl)									
						
					
		#delete_trash(mail)
		
		mail.logout()
				
		#e()
		
if 1:
	delete_from_inbox()
if 0:
	args = dict([arg.split('=') for arg in sys.argv[1:]])

	print("Logging into GMAIL with user %s\n" % args['username'])
	box = imaplib.IMAP4_SSL('imap.gmail.com')
	pp(args)
	box.login('olek.buzu@gmail.com', '198Morgan;')
	box.select('Inbox')
	typ, data = box.search(None, 'ALL')
	assert typ in ['OK'], typ
	mids = data[0].split()
	print(mids[0])
	typ, mail = box.fetch(mids[0], '(RFC822)' )
	pp(type(mail[0]))
	response_part = ''.join([str(row) for row in mail[0][1:]])
	#print (response_part)
	if isinstance(response_part, str):
		msg = email.message_from_string(response_part)
		pp(msg.keys())
		if 1:
			
			email_subject = msg['subject']
			email_from = msg['from']
			print ('From : ' , email_from )
			print ('Subject : ' , email_subject)

#box.store(num, '+FLAGS', '\\Trash')
#box.expunge()
#box.close()
#box.logout()


def send_mail(to_address, subject, body):
	smtp_user = "olek.buzu@gmail.com"
	smtp_password = "198Morgan;"
	server = "smtp.gmail.com"
	port = 587

	msg = MIMEMultipart("alternative")
	msg["Subject"] = subject
	msg["From"] = smtp_user
	msg["To"] = to_address
	msg.attach(MIMEText(body, "html"))
	s = smtplib.SMTP(server, port)
	s.connect(server, port)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(smtp_user, smtp_password)
	s.sendmail(smtp_user, to_address, msg.as_string())
	s.quit()
	
if 0:
	send_mail('olek.buzu@gmail.com', 'test', 'test')
	
	
if 0:
	args = dict([arg.split('=') for arg in sys.argv[1:]])

	print("Logging into GMAIL with user %s\n" % args['username'])
	server = imaplib.IMAP4_SSL('imap.gmail.com')
	pp(args)
	connection_message = server.login('olek.buzu@gmail.com', '198Morgan;')
	pp(connection_message)
	#e()
	if args.get('label'):
		print("Using label: %s" % args['label'])
		server.select(args['label'])
	else:
		print("Using inbox")
		server.select("inbox")

	print("Searching emails from %s" % args['sender'])
	result_status, email_ids = server.search(None, '(FROM "%s")' % args['sender'])
	email_ids = email_ids[0].split()

	if len(email_ids) == 0:
		print("No emails found, finishing...")

	else:
		print("%d emails found, sending to trash folder..." % len(email_ids))
		server.store('1:*', '+X-GM-LABELS', '\\Trash')
		server.expunge()

	print("Done!")