import email,imaplib
import getpass
import re
import time
import os,sys
from subprocess import call
from 


usage = "Connect to a mail address in order to be able to set up a list of speakers"
imapserver='imap.cern.ch'
username='amarini'
mail=None
subject='WGM'
N=20

#ask for password
password=getpass.getpass()

## global
Break=False
Readed=[]


def Connect():
	global mail
	global password
	global username
	mail = imaplib.IMAP4_SSL(imapserver)
	mail.login(username, password)
	mail.list()
	mail.select("inbox",readonly=True) # connect to inbox.



def Loop():
	global Break
	global Readed
	global mail
	global N

	result, data = mail.uid('search', None, "ALL") # search and return uids instead
	#result, data = mail.search( None, "ALL") # search and return uids instead
	
	email_list=[]
	for i in range(1,N):
		uid = data[0].split()[-i]
		if uid not in Readed:
			#result, data2 = mail.uid('fetch', uid, '(RFC822)')
			result, data2 = mail.uid('fetch', uid, '(FLAGS BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])')
			#result, data2 = mail.uid('fetch', uid, '(BODY.PEEK[HEADER.FIELDS(DATE SUBJECT FROM)])')	
			#result, data2 = mail.uid('fetch', uid, '(RFC822.PEEK)')	
			#result, data2 = mail.fetch(uid, 'BODY.PEEK[HEADER.FIELDS(DATE SUBJECT FROM)]')	
			raw_email = data2[0][1]
			if raw_email == None:
				print "mail uid %d not correctly fetched" %uid
				if mail == None:
					print "mail is None ? "
			email_list.append(raw_email)
			Readed.append(uid)
	
	#this command should fetch only the header subject
	
	for raw_email in email_list:
		email_message = email.message_from_string(raw_email)
		if re.search(subject, email_message['Subject']):
		     if re.search('talk',email_message.get_payload()):
				print "Going to unblind:"
				print "From:",email_message["From"],"Sbj:",email_message['Subject']
				Break=True
		     if re.search('delete',email_message.get_payload()):
			     print 'do something'


### MAIN ####
Connect()
while True:
	print "Starting Loop"
	Loop()
	if Break: 
		print "should break"
		break
	else:
		print "*",
		sys.stdout.flush()
	time.sleep(60)

print "Yeah"


