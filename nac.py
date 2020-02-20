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

#Delete all emails with "Subject" or "Body " containing these tags
kws  = ['QlikView', 'Tableau', 'Hadoop Admin', '.Net',  'Hadoop Architect', 'Power BI Administrator','Pro C',
'Production Support Lead', 'Oracle DBA', 'Cognos', 'Talend', 'HCM Cloud Technical', 'Business System Analyst',
'Splunk Developer', 'MongoDB Clustering and Mongo DB scaling', 'Microstrategy Developer','Informatica Developer',
'Django and Flask', 'JavaScript and HTML5', 'Oracle Cloud CRM Functional Architect', 'Oracle Architect',
'PowerCenter', 'Content Management Analyst', 'JAVA, Kafka', 'PySpark Expert', 'Hadoop, Map Reduce, Yarn',
'Administrative Assistant', 'Oracle Fusion Cloud Financials','Java Backend Developer',
'Security Engineer', 'Django and JavaScript', 'Data Modeler', 'Java Developer', 'Application Security Analyst',
'JAVA and Python', 'Oracle Functional Consultant', 'Informatica Lead', 'Clover experience','Big Data Engineer',
'Business or System Analyst', 'Corporate Accountant', 'Support Engineer', 'Project Manager', 'SQL Developer', 'Full Stack',
'Oracle Application', 'ServiceNow', 'Business Analyst', 'Automation Tester', 'Sybase DBA', 'Senior Software Engineer']

locs = ['Garden City, NY', 'Arizona', 'Washington','Albertville, AL', 'Columbus OH', 'Denver, CO', 'Dallas',
'RENTON, Washington','Branchburg, NJ', 'Whippany, NJ', 'Baltimore, MD', 'Phoenix, AZ',
'St. Paul, MN', 'Renton, WA', 'Providence, RI', 'Westin, NJ','Atlanta, GA', 'Stow, MA', 'Frisco, TX',
'McLean, VA', 'Berwyn, PA', 'Dedham, MA','Louisville', 'Dublin, OH', 'San Ramon,CA', 'San Diego', 'Seattle, WA',
'Sunnyvale, CA', 'Houston, TX', 'Alpharetta, GA', 'Pittsburgh PA', 'Quincy, MA', 'Dedham, MA', 'Carry, NC',
'Columbus, OH', 'Chandler, AZ', 'Nashville, TN', 'Minneapolis', 'Fremont, CA','Princeton, NJ', 'Charlotte', 'Hillsboro',
'Glenivew, IL','Miami', 'Tampa, FL', 'Smithfield', 'Boston, MA', 'Columbus, IN', 'Malvern, PA', 'Raleigh', 'Danbury, CT',
'Fort Worth, TX','San Jose, CA', 'Baton Rouge, LA', 'Pleasanton, CA', 'Mahwah', 'Rosemont','Stamford, CT', 'Richfield','Suitland',
'Detroit', 'KANSAS CITY', 'Cincinnati', 'Des Moines','Madison, NJ', 'Richmond, VA','Camphill, PA','SPRING HOUSE',
'Walnut Creek, CA', 'Deerfield, IL','Richardson, TX','Austin','Basking Ridge','St. Louis','El Segundo, CA',
'Chesterfield, MO', 'Exton, PA', 'Santa Monica', 'Glen Allen, VA', 'Albany, NY', 'Edison, NJ', 'Woonsocket, RI',
'Peoria, IL','Playa Vista','Betheseda, MD', 'Reston, VA','Iowa City', 'Dearborn, MI','North Wales, PA','Salisbury, NC',
'San Antonio', 'Portsmouth, NH', 'Milwaukee, WI', 'Albuquerque', 'Newark , CA', 'Dresher, PA','Memphis','Cleveland',
'Greenville, SC','Greensboro', 'Bloomington, MN', 'Jacksonville','Winston, NC',' Austin, TX','West Jefferson','Tempe, AZ','Playa Vista',
'Milford, CT','Englewood, CO', 'Plano, TX', 'Dearborn, MI', 'Carlsbad, CA','Indianapolis', 'Saint Louis', 'St Louis', 'Hartville, SC',
 'Franklin, WI', 'Westborough, MA']



#Label all emails with "From" containing these tags
lbls = ['Remote','Etsy','Google','Snowflake', 'Hilton', 'CBS', 'Slice', 'Facebook', 'Amazon', 'Quora', 'Pafa',
'Linkedin', 'Elliot', 'Cybercoders', 'UBS', 'Oracle', 'VOLIACABLE', 'KFORCE', 'JOBSEARCHINFO',
'HUXLEY','LAMP.CODER', 'Staffing', 'HEROLD.COM', 'job.com', 'Craigslist', 'Hotmail', 'Sans.com','buzaleks','NAZARENKO']

#Override delete if following tags are present	
keep = ['New York', 'Remote', 'Jersey City', 'San Francisco', 'Chicago', 'Los Angeles',  'Seattle']
letgo =['Hadoop', 'Data Modeler','Fulltime', 'Junior Oracle Developer','Full time']
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
			#pp(decode)
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
	#pp(mov)
	#pp(data)	
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
	#pp(result)	
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

def delete_from_inbox(mail):


		mail.select('inbox')

		typ, data = mail.search(None, '(UNSEEN)')
		mail_ids = data[0]

		id_list = mail_ids.split() 

		if not id_list:
			return
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
								print (i, 'Keep "%s"' % loc, frm, subj[:20],list(map(lambda x: x.upper() in subj, keep))) 
								if not any(list(map(lambda x: x.upper() in subj, letgo))):
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
				#keep unread if not deleted 
				mail.uid('STORE', msg_uid, '-FLAGS', '(\\SEEN)')
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
		
		print('Done.')
		#e()
		
if __name__=='__main__':
	if 1:
		mail = imaplib.IMAP4_SSL(IMAP_SERVER)

		mail.login(FROM_EMAIL,FROM_PWD)
		
	delete_from_inbox(mail)
	while True:
		time.sleep(300)
		delete_from_inbox(mail)
	
	mail.logout()
		
		
		
