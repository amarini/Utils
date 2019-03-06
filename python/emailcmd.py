import email,imaplib
import getpass
import re
import time
import os,sys
from subprocess import call
from optparse import OptionParser

imapserver='imap.cern.ch'
username='amarini'
mail=None
N=20
isDryRun=False

## parse options
parser=OptionParser()
parser.add_option("","--password",dest="password",type="string",help="Pass Password as option. NOT SAFE",default=None)
parser.add_option("","--host",dest="host",type="string",help="Host you connect to. Default=%default",default=imapserver)
parser.add_option("-u","--user",dest="user",type="string",help="User on the remote host. Default=%default",default=username)
parser.add_option("-n","--last-n",dest="N",type="int",help="Number of emails to check. Default=%default",default=N)

(opts,args) = parser.parse_args()

#ask for password
if not opts.password: password=getpass.getpass()
else: password=opts.password

imapserver=opts.host
username=opts.user
N=opts.N

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
	global isDryRun

	result, data = mail.uid('search', None, "ALL") # search and return uids instead
	#result, data = mail.search( None, "ALL") # search and return uids instead
	
	email_list=[]
	for i in range(1,N):
		uid = data[0].split()[-i]
		if uid not in Readed:
			#result, data2 = mail.uid('fetch', uid, '(RFC822)')
			result, data2 = mail.uid('fetch', uid, '(FLAGS BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])')
			raw_email = data2[0][1]
			if raw_email == None:
				print "mail uid %d not correctly fetched" %uid
				if mail == None:
					print "mail is None ? "
			email_list.append( (uid,raw_email) )
	
	#this command should fetch only the header subject
	
	for uid,raw_email in email_list:
		if uid in Readed: continue
		email_message = email.message_from_string(raw_email)
		if 'Subject' not in email_message: 
			print "Error parsing message:"
			print "Original:\n",raw_email
			print "Parsed:\n",email_message
			continue;
		Readed.append(uid)
		if isDryRun: continue ## avoid for the first run any action
		if re.search('CMD:BJOBS', email_message['Subject']) :
				print "Going to send a message with bjobs result:"
				print "From:",email_message["From"],"Sbj:",email_message['Subject']
				cmd="( bjobs -w | grep -v JOBID |wc -l ; echo -n 'Run:' ; bjobs -w | grep RUN | wc -l ;  ) | mail -s 'bjobs results' amarini@cern.ch"
				call(cmd,shell=True)
				#Break=True

Connect()

isDryRun=True
while True:
	print "Starting Loop"
	Loop()
	isDryRun=False
	if Break: 
		print "should break"
		break
	else:
		print "*",
		sys.stdout.flush()
	time.sleep(15)

print "Yeah"

#cmd=["/afs/cern.ch/user/a/amarini/work/ProductionJanuary2014/CMSSW_6_1_1_CategoryFull/src/h2gglobe/unblind.sh"]
#call(cmd)

