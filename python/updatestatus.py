import os,sys
import re
from glob import glob
import time

def GetSummary(dir ):
    ''' Get summary informations for dir'''
    run  = glob(dir + "/*run")
    fail = glob(dir + "/*fail")
    done = glob(dir + "/*done")
    pend = glob(dir + "/*pend")
    return ( done, run, fail, pend)

from subprocess import check_output
def GetCrabStatus(dir):
    out=check_output("crab status "+ dir, shell=True)
    run=0
    fail=0
    done=0
    pend=0
    tot=0
    #Jobs status:                    finished                 93.3% (336/360)
    #                                running                   6.7% ( 24/360)
    
    for line in out.split('\n'):
        #"(Jobs status:|)[\ \t]*finished"
        if re.match("(Jobs status:|)[\ \t]*finished",line):   done=int(re.sub('/.*','',re.sub('.*\(','',line)))
        if re.match("(Jobs status:|)[\ \t]*running",line):    run+=int(re.sub('/.*','',re.sub('.*\(','',line)))
        if re.match("(Jobs status:|)[\ \t]*failed",line):     fail=int(re.sub('/.*','',re.sub('.*\(','',line)))
        if re.match("(Jobs status:|)[\ \t]*pending",line):    pend=int(re.sub('/.*','',re.sub('.*\(','',line)))
        if re.match("(Jobs status:|)[\ \t]*transferring",line): run+=int(re.sub('/.*','',re.sub('.*\(','',line)))

        if re.match("Jobs status:",line): tot= int(re.sub('.*/','',re.sub('\)','',line)))

    return ( done, run, fail, pend,tot)


from optparse import OptionParser

usage="prog opts dirs"
parser=OptionParser(usage=usage)
parser.add_option("-d","--dir",help="output dir. [%default]",default=os.environ["HOME"]+"/www/status")
parser.add_option("-l","--loop",type='int',help="Loop every n seconds. [%default]",default=-1)
parser.add_option("-c","--crab",action='store_true',help="Monitor crab [%default]",default=False)
opts,args=parser.parse_args()

dirs=[]
try:
    os.mkdir(opts.dir)
except: pass

while True:
    index=open(opts.dir+"/index.html","w")
    
    index.write("<!DOCTYPE html>\n")
    index.write("<html>\n")
    index.write("<h1> Status </h1>\n")
    index.write('<meta http-equiv="refresh" content="5" />\n')
    
    index.write('''<style type="text/css">
    progress[value] {
          /* Reset the default appearance */
          width: 250px;
          height: 20px;
    }
    </style>
    ''')
    
    #index.write('</br>\n') ## new line
    
    index.write("<body>\n")
    ## First col
    index.write('<table style="width:100%">\n')
    index.write("<tr>\n") ## line
    index.write('<td><h3> Directory</h3> </td>\n')
    index.write('<td><h3> Success  </h3> </td>\n')
    index.write('<td><h3> Running  </h3> </td>\n')
    index.write('<td><h3> Failed   </h3> </td>\n')
    index.write('</tr>\n') ## end line
    
    # consider *, so will be updated in the loops
    args2=[]
    for dir in args: args2.extend(glob(dir))
    
    for dir in args2:
        print "considering",dir
        if opts.crab:
            done,run,fail,pend,tot = GetCrabStatus(dir)
            value=done
            #tot= done+run+fail+pend
        else:
            done,run,fail,pend = GetSummary( dir ) 
            value=len(done)
            tot = len(done) + len(run) + len(fail) + len(pend)
            run=len(run)
            done=len(done)
            fail=len(fail)
            pend=len(pend)
        #print "DEBUG: DIR",dir,"TOT",tot,value,run,fail,pend
        if tot==0 : 
            continue
        index.write('<tr>\n')
        index.write('<td>\n')
        name=""
        idx =  len(dir.split('/')) -1
        while ('PU' in name or name == "") and idx>=0:
            name=dir.split('/')[idx]
            idx-=1
        if name == "":
            name = dir.split('/')[-1]
        
        index.write( name + ": \n")
        index.write('</td>\n') ## close left
        ## success
        index.write('<td>\n')
        index.write('<progress value="%d" max="%d"></progress>\n'%(value,tot))
        index.write('</td>\n') ## close left
        ##
        index.write('<td>\n')
        index.write('<progress value="%d" max="%d"></progress>\n'%(run,tot))
        index.write('</td>\n') ## close left
        ##
        index.write('<td>\n')
        index.write('<progress value="%d" max="%d"></progress>\n'%(fail,tot))
        index.write('</td>\n') ## close left
        #index.write("</br>\n")
        index.write('</tr>\n') ## close wrap
        #index.write('</br>\n') ## new line
    
    index.write("</body>\n")
    index.write("</html>\n")
    index.close()
    
    if opts.loop < 0 : exit(0)
    time.sleep(opts.loop)
