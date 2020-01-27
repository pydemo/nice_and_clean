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

import imaplib, getpass, re




FROM_EMAIL  = os.environ.get('FROM_EMAIL').strip("'")
FROM_PWD 	= os.environ.get('FROM_PWD').strip("'")
IMAP_SERVER = os.environ.get('IMAP_SERVER').strip("'")

assert FROM_EMAIL
assert FROM_PWD
assert IMAP_SERVER

#Delete all emails with "Subject" or "Body" containing these tags
kws  = ['QlikView', 'Tableau', 'Hadoop Admin', '.Net',  'Hadoop Architect', 'Power BI Administrator','Pro C',
'Production Support Lead', 'Oracle DBA', 'Cognos', 'Talend', 'HCM Cloud Technical', 'Business System Analyst',
'Splunk Developer', 'MongoDB Clustering and Mongo DB scaling', 'Microstrategy Developer','Informatica Developer',
'Django and Flask', 'JavaScript and HTML5', 'Oracle Cloud CRM Functional Architect', 'Oracle Architect',
'PowerCenter', 'Content Management Analyst', 'JAVA, Kafka', 'PySpark Expert', 'Hadoop, Map Reduce, Yarn',
'Administrative Assistant', 'Oracle Fusion Cloud Financials','El Segundo, CA','Java Backend Developer',
'Security Engineer', 'Django and JavaScript' ]

locs = ['Garden City, NY', 'Arizona', 'Washington','Albertville, AL', 'Columbus OH', 'Denver, CO', 'Dallas TX',
'RENTON, Washington','Branchburg, NJ', 'Whippany, NJ', 'Baltimore, MD', 'Phoenix, AZ',
'St. Paul, MN', 'Renton, WA', 'Providence, RI', 'Westin, NJ','Atlanta, GA', 'Stow, MA', 'Frisco, TX','Dallas, TX',
'McLean, VA', 'Berwyn, PA', 'Dedham, MA','Louisville', 'Dublin, OH', 'San Ramon,CA', 'San Diego, CA', 'Seattle, WA',
'Sunnyvale, CA', 'Houston, TX', 'Alpharetta, GA', 'Pittsburgh PA', 'Quincy, MA', 'Dedham, MA', 'Carry, NC',
'Columbus, OH', 'Chandler, AZ', 'Nashville, TN', 'Charlotte, NC', 'Fremont, CA','Princeton, NJ', 'Charlotte', 'Hillsboro',
'Glenivew, IL','Miami', 'Tampa, FL']



#Label all emails with "From" containing these tags
lbls = ['Remote','Etsy','Google','Snowflake', 'Hilton', 'CBS', 'Slice', 'Facebook', 'Amazon', 'Quora', 'Pafa',
'Linkedin', 'Elliot', 'Cybercoders', 'UBS', 'Oracle', 'VOLIACABLE', 'KFORCE', 'JOBSEARCHINFO',
'HUXLEY','LAMP.CODER', 'Staffing', 'HEROLD.COM', 'job.com', 'Craigslist', 'Hotmail', 'Sans.com','buzaleks','NAZARENKO']

#Override delete if following tags are present	
keep = ['New York', 'Remote', 'Jersey City', 'San Francisco', 'Chicago', 'Los Angeles',  'Seattle']

#Clear \\Trash		
erase = False
		
def get_body(msg): 
	if msg.is_multipart(): 
		return get_body(msg.get_payload(0)) 
	else: 
		return str(msg.get_payload(None, True).replace(str.encode(os.linesep), b''))
def get_subject(msg): 
		sub = msg.get('Subject')
		if type(sub) is str:		
			return sub.replace(os.linesep, '') if sub else ''
		elif type(sub) is email.header.Header:
			decode = email.header.decode_header(msg['Subject'])[0]
			pp(decode)
			sub = str(decode[0])
			return sub.replace(os.linesep, '') if sub else ''
		else:
			return ''
			#raise Exception('Unknown subject type')
def get_from(msg): 
		frm = msg.get('From')
		if type(frm) is str:		
			return frm.replace(os.linesep, '') if frm else ''
		elif type(frm) is email.header.Header:
			decode = email.header.decode_header(msg['From'])[0]
			pp(decode)
			frm = str(decode[0])
			return frm.replace(os.linesep, '') if frm else ''
		else:
			return ''
			#raise Exception('Unknown subject type')
			
def get_emails(result_bytes): 
	msgs = [] 
	for num in result_bytes[0].split(): 
		typ, data = con.fetch(num, '(RFC822)') 
		msgs.append(data) 

def delete_message(mail, msg_uid):	
	#mail.store(id, '+X-GM-LABELS', '\\Trash')
	#mail.store(id, '+FLAGS', '\\Deleted')
	#mail.expunge()
	#mail.close()
	mov, data = mail.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
	pp(mov)
	pp(data)	
	mail.expunge()

def label_message(mail, id, msg_uid, label):	
	#mail.store(id, '-X-GM-LABELS', '\\inbox')
	lbl = '_%s' % label.split(' ')[0]
	try:
		mail.store(id, '+X-GM-LABELS', lbl)
	except:
		pp(lbl)
		raise
	result = mail.uid('COPY', msg_uid, lbl)
	pp(result)	
	delete_message(mail, msg_uid)

	
	
def delete_trash(mail, erase=erase):

	out = mail.select('[Gmail]/Trash')  # select all trash
	assert out[0]  == 'OK'
	if len(out[1]) > 0:
		
		mail.store("1", '+FLAGS', '\\Deleted')
		print ('Trash deleted (%s)' % len(out[1]))
		if erase:
			mail.expunge()	
		
		
	else:
		print ('Trash is empty')
		time.sleep(1)
		
def parse_uid(data):
	pattern_uid = re.compile(b'\d+ \([A-Z\(\) a-z]?UID (\d+)\)')

	try:
		match = pattern_uid.match(data)
	except:
		pp(pattern_uid, data)
		raise
	grps = match.groups()
	assert len(grps)>0, grps
	return grps[0]		
def unseen():
	conn = imaplib.IMAP4_SSL(imap_server)

	try:
		(retcode, capabilities) = conn.login(imap_user, imap_password)
	except:
		 
		print(sys.exc_info()[1])
		sys.exit(1)

	conn.select(readonly=1) # Select inbox or default namespace
	(retcode, messages) = conn.search(None, '(UNSEEN)')
	if retcode == 'OK':
		for num in messages[0].split(' '):
			print ('Processing :', message)
			typ, data = conn.fetch(num,'(RFC822)')
			msg = email.message_from_string(data[0][1])
			typ, data = conn.store(num,'-FLAGS','\\Seen')
			if ret == 'OK':
				print (data,'\n',30*'-')
				print (msg)

	conn.close()

def delete_from_inbox():

		mail = imaplib.IMAP4_SSL(IMAP_SERVER)

		mail.login(FROM_EMAIL,FROM_PWD)
		mail.select('inbox')

		typ, data = mail.search(None, '(UNSEEN)')
		mail_ids = data[0]

		id_list = mail_ids.split()   
		first_email_id = int(id_list[0])
		latest_email_id = int(id_list[-1])

		subj=body=frm=None
		mids=mail_ids.split()
		#mids = [b'%d' % x for x in range(1, 30000)]
		for id in reversed(range( len(mids))):
			i=mids[id]
			deleted = False
			typ, data = mail.fetch(i, '(RFC822)' )
			if 1:
				resp, dt = mail.fetch(i, "(UID)")
				assert resp == 'OK', resp
				print(i, dt, frm, subj)
				assert dt[0], dt
				msg_uid = parse_uid(dt[0])

			result = mail.fetch(i, '(X-GM-MSGID)')
			gm_msgid = re.findall(b"X-GM-MSGID (\d+)", result[1][0])[0]

			for response_part in data:
				if isinstance(response_part, tuple):
					
					msg = email.message_from_bytes(response_part[1])
					subj = get_subject(msg).upper()
					body = get_body(msg).upper()
					frm  = get_from(msg).upper() 
					

					if 1:
						for kw in kws:
							if kw.upper() in subj:
								print (int(i), 'Key Subj "%s"' % kw)
								deleted = True
								
							elif kw.upper() in body:
								print (int(i), 'Key Body "%s"' % kw)
								deleted = True

							else:
								pass
						if not deleted:
							for loc in locs:
								if loc.upper() in subj:
									print (int(i), 'Loc Subj "%s"' % loc)
									deleted = True
									
								elif loc.upper() in body:
									print (int(i), 'Loc Body "%s"' % loc)
									deleted = True
									
							if any(list(map(lambda x: x.upper() in subj, keep))):
								print (i, 'Keep "%s"' % loc, frm, subj[:20]) 
								deleted = False
							
									
				
			if deleted: 				
				delete_message(mail, msg_uid)
				#delete_trash(mail)
				deleted = False
			else:

				labelled = False	
				for lbl in lbls:
					if lbl.upper() in frm:
						print('Label "%s"' % lbl,  frm)	
						labelled = True
						label_message(mail, i, msg_uid, lbl)
						break
				if 0 and not labelled:
					lbl=None
					
					tmp=frm.split('<')
					assert len(tmp)>0, tmp
					if len(tmp) ==1:
						sp = tmp[0].split('@')
						try:
							assert len(sp) ==2, sp
							lbl = sp[1].strip()
						except:
							lbl = tmp[0].split(' ')[0]
						
					else:
						if '@' in tmp[1]:
							try:
								sp = tmp[1].split('@')
							except:
								pp(frm)
								pp(tmp)
								raise
							lbl= sp[1].strip().strip('"').strip('>')
							
						else:
							lbl= tmp[1].strip().strip('"').strip('>')
					if lbl:
						try:
							label_message(mail, i, msg_uid, lbl)
						except:
							print("#"*40,  frm, lbl)
							raise
				labelled = False
					
		#delete_trash(mail)
		
		mail.logout()
				
		#e()
		
if 1:
	delete_from_inbox()
