#!/usr/bin/python

import sys, os, array
import subprocess
from glob import glob
from optparse import OptionParser
import time
import random

#global
preCommand=[]
submitOptions=[]

random.seed()
suffix="."+str(random.randint(0,10000))
print "-- suffix is "+suffix+" --"

user=os.environ['USER']

import signal
def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])


#---------------------------  (1)
#| crab_fqq0.50_x1 |
#---------------------------  (2)
#DONE    = 1000     (100.00%)
#---------------------------  (3)
#[=========================]
#---------------------------  (4)

def FixedSize(line,size):
	n=len(line);
	if '\033' in line: n-=12
	for i in range(n,size):
		line+=' '
	return line

def PrintSummary(Summary):
	(w,h)= getTerminalSize();
	lines = Summary.split('\n')
	#maxlen = len( max(lines, key=len) ) # python 2.5
	maxlen=0;
	for l in lines:
		n=len(l)
		if '\033' in l: n-=12
		if n> maxlen:  maxlen=n
	nCol = w/(maxlen+4);
	Output = ""

	ListOfBox=[]
	count=0
	begin=-1
	for i in range(0,len(lines)):
		if '------------------' in lines[i]: count += 1;
		if count == 1 and begin<0: begin = i
		if count == 4: 
			ListOfBox.append( (begin,i) )
			begin=-1
			count=0
	#add empty boxes at the end
	mod=len(ListOfBox)%nCol
	for i in range(mod,nCol):
		ListOfBox.append( (0,-1)  )
	#take ListOfBox and place them togheter
	for BoxLine in range(0,len(ListOfBox)/nCol ): 
		#computed the number of lines to print
		nL=0
		for iCol in range(0,nCol):
			if nL < ListOfBox[iCol+BoxLine][1]- ListOfBox[iCol+BoxLine][0] + 1: nL =  ListOfBox[iCol+BoxLine][1]- ListOfBox[iCol+BoxLine][0] + 1
		for iLine in range(0,nL):
		   for iCol in range(0,nCol):
			Output += " | "
			current = ListOfBox[iCol+BoxLine][0] + iLine
			if current > ListOfBox[iCol+BoxLine][1]:  Output += FixedSize("",maxlen)
			else: 
				Output +=  FixedSize( lines[ current ],maxlen )
			#Output += lines[ ListOfBox[iCol+BoxLine][0] + iLine ]
		   Output += " |\n"
	print Output
	return Output
	

def CrabStatus(dirName):
	out=subprocess.call("crab -status -c "+dirName+" > /tmp/"+user+"/monitor.status"+suffix,shell=True)

def CrabGet(dirName):
	out=subprocess.call("crab -get -c "+dirName+" > /tmp/"+user+"/monitor.get"+suffix,shell=True)

def Status(dirName):
	Result={}
	#out=subprocess.check_output(["crab","-status","-c",dirName],shell=True)
	#out=subprocess.check_output("crab -status -c "+dirName,shell=True)
	#out,err = p.communicate()
	CrabStatus(dirName)
	return ReadStatus("/tmp/"+user+"/monitor.status"+suffix)

def FullStatus(dirName):
	CrabStatus(dirName)
	CrabGet(dirName)
	CrabStatus(dirName)
	return ReadStatus("/tmp/"+user+"/monitor.status"+suffix)
	

def ReadStatus(txtName):
	Result={}
	out=open(txtName,'r')

	for line in out:
		R={}
		parts=line.split()
		try:
			R['jobId']=int(parts[0])
			R['end']=parts[1]
			R['status']=parts[2]
			R['action']=parts[3]
			try:
				R['exeExit']=int(parts[4])
				R['jobExit']=int(parts[5])
				R['host']=parts[6]
			except (ValueError,IndexError):
				R['exeExit']=int(-1)
				R['jobExit']=int(-1)
				try:
					R['host']=parts[4]
				except (ValueError,IndexError):
					R['host']=""
			Result[ R['jobId'] ] = R
		except (ValueError,IndexError): pass
	return Result

def CallSubmit(jobList,dirName,Resubmit=False):
	cmd=[]+preCommand
	if Resubmit:
		cmd += ['crab','-resubmit']
	else:
		cmd += ['crab','-submit']
	jobs=''
	for iJob in jobList:
		jobs=jobs+str(iJob)+','
	#delete last
	jobs=jobs[:-1]
	cmd=cmd+[jobs,"-c",dirName]
	cmd=cmd+submitOptions
	subprocess.call(cmd)

def Submit(jobList,dirName,Resubmit=False):
	for i in range(0,len(jobList),450):
		CallSubmit(jobList[i:i+450],dirName,Resubmit);

def CallForceResubmit(jobList,dirName):
	cmd=[]+preCommand
	cmd += ['crab','-forceResubmit']
	jobs=''
	for iJob in jobList:
		jobs=jobs+str(iJob)+','
	#delete last
	jobs=jobs[:-1]
	cmd=cmd+[jobs,"-c",dirName]
	cmd=cmd+submitOptions
	subprocess.call(cmd)
	print " -- GOING TO SLEEP FOR 60s --"
	time.sleep(60)
	print " -- WAKE UP --"

def ForceResubmit(jobList,dirName):
	for i in range(0,len(jobList),450):
		CallForceResubmit(jobList[i:i+450],dirName);

def SubmitAll(Result,dirName,Resubmit=False):
	jobList=[]
	for key in Result:
		jobList.append(key)
	Submit(jobList,dirName,Resubmit)	

def ReSubmitES(exitN,Result,dirName):
	jobList=[]
	sites={}
	for key in Result:
		if Result[key]['exeExit']==exitN or Result[key]['jobExit']==exitN:
			jobList.append(key)
			if exitN == 8020: ## site error: ban T2
				SE=subprocess.check_output("cat "+dirName+"/res/CMSSW_"+str(key)+".stdout | grep '^SyncSite='  | tail -n 1 | cut -d '=' -f2", shell=True)	
				try:
					sites[ SE ] += 1
				except KeyError:
					try: sites[ SE ] = 1
					except KeyError: pass
	for se in sites:
		if sites[ se ] > 10 and len(se) >4 : #avoid malformed strings
			print " BANNING SE " + se
			found=False
			for i in range(0,len(submitOptions)):
				if "se_black_list" in submitOptions[i]:
					if not se in submitOptions[i]:submitOptions[i]+=","+se
					found=True
			if not Found:
				submitOptions.append("-GRID.se_black_list="+se)
			
	Submit(jobList,dirName,True)

def ReSubmitCA(Result,dirName):
	jobList=[]
	for key in Result:
		if Result[key]['status']=="Cancelled" or Result[key]['status']=='Aborted':
			jobList.append(key)
	Submit(jobList,dirName,True)

def ForceReSubmitSubmitted(Result,dirName):
	jobList=[]
	for key in Result:
		if Result[key]['status']=="Submitted":
			jobList.append(key)
	ForceResubmit(jobList,dirName)

def PrintStatus(Result,dirName=""):
	DONE=0
	NOTDONE=0
	Cancelled=0
	Aborted=0
	Submitted=0
	Running=0
	Exit={}
	line=""
	for key in Result:
		try:
			Exit[ Result[key]['jobExit'] ] += 1
		except KeyError:
			Exit[ Result[key]['jobExit'] ] = 1
		if Result[key]['status'] =="Cancelled":
			Cancelled += 1
		if Result[key]['status'] =="Aborted":
			Aborted += 1
		if Result[key]['status'] =="Submitted":
			Submitted += 1
		if Result[key]['status'] =="Running":
			Running += 1
		if Result[key]['end'] == "Y" and Result[key]['jobExit'] ==0:
			DONE += 1
		else:
			NOTDONE += 1
	
	if DONE+NOTDONE == 0: NOTDONE=-1
	
	line+= "---------------------------\n"
	line+= "* " +dirName + " *\n"
	line+= "---------------------------\n"
	line+= "\033[01;32mDONE    = %4d     (%.2f%%)\033[0m\n"%(DONE,float(DONE)/(DONE+NOTDONE)*100)
	if NOTDONE != 0: line+= "\033[01;31mNOTDONE = %4d     (%.2f%%)\033[0m\n"%(NOTDONE,float(NOTDONE)/(DONE+NOTDONE)*100)
	line+= "---------------------------\n"
	line+="\033[01;34m["
	tot=25
	dash=int(tot*float(DONE)/(DONE+NOTDONE) )
	space=tot-dash-1
	for i in range(0,dash):line += '='
	if dash<tot: line+='>'
	for i in range(0,space):line+= ' '
	line +=']\033[0m\n'
	line += "---------------------------\n"
	print line
	print "Cancelled: %d"%(Cancelled)
	print "Aborted: %d"%(Aborted)
	print "Submitted: %d"%(Submitted)
	print "Running: %d"%(Running)
	for key in Exit:
		print "ExitStatus %d: %d"%(key,Exit[key])
	print "---------------------------"
	return line

def PrintDatabase(Results):
	for key in Results:
		print str(key)+":"
		print Results[key]


if __name__ == "__main__":
	parser=OptionParser(usage=" %prog [options] dir1 dir2 ...\nProvide help to run/submit/resubmit crab jobs")
	parser.add_option("-l","--loop",help="Run in loop",dest="loop",default=False,action='store_true')
	parser.add_option("-n","--dryrun",help="Dry Run: Print command instead of re/submit",dest="dryrun",default=False,action='store_true')
	parser.add_option("-s","--submit",help="Submit jobs",dest='submit',default=False,action='store_true')
	parser.add_option("-x","--extra",help="Extra Options for submit. E.g. '-GRID.se_black_list=T2;-GRID.ce_black..'",dest='extra',default='',type='string')
	parser.add_option("-e","--exitNumber",help="Resubmit Exit 1,2,3 ...\nDefault=%default",dest='exit',default='127,8020,8021,60317,60318,60307,50664,50115,10034,8001,8022,8028,50800',type='string') 
	parser.add_option("","--forceResubmitSubmittedJobs",help="Force Resubmition of jobs in status submitted",dest="forceResubmit",default=False,action='store_true')
	(options,arg) = parser.parse_args()

	if options.dryrun:
		preCommand=["echo"]
	
	if options.forceResubmit and options.loop:
		print "---> CANT LOOP ON FORCE RESUBMIT <---"
		sys.exit(0)
	
	if options.forceResubmit:
		pwd=random.randint(0,10000)
		line=raw_input('You are going to force resubmit jobs: Enter %d to confirm: '%(pwd))
		if int(line) != pwd:
			print "you have entered '"+line+"' instead of '"+str(pwd)+"': Going to abort execution."
			sys.exit(0)

	if options.extra != '':
		submitOptions=options.extra.split(';')
	
	if options.exit != "":
		numList=[]
		for i in options.exit.split(','):
			numList.append(int(i))
	else:
		numList=[]
	
	#main loop
	if options.loop:
		signal.signal(signal.SIGINT, signal_handler)
		
	if options.loop and options.submit:
		print "-- cannot be loop & submit --"
		sys.exit(0)

	while True:
		Summary=""
		for dir in arg:
			if options.submit:
				Results=Status(dir)
				SubmitAll(Results,dir)
			Results=FullStatus(dir)
			Summary+=PrintStatus(Results,dir) 
			print "-- Resubmit Cancelled & Aborted --"		
			ReSubmitCA(Results,dir)
			for exitStatus in numList:
				print "-- Resubmit Exit "+str(exitStatus)+" --"
				ReSubmitES(exitStatus,Results,dir)

			if options.forceResubmit:
				ForceReSubmitSubmitted(Results,dir)
				sys.exit(0)
		print "\n\n" + Summary + "\n\n"
		print "\n\n"
		PrintSummary(Summary)
		if options.loop : 
			print "--- GOING TO SLEEP ----"
			time.sleep(15*60)
			print "--- WAKE UP ----"
		else: break;

