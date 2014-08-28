import sys,os
from glob import glob
from optparse import OptionParser,OptionGroup
import re

parser= OptionParser()
parser.add_option("-d","--dir",action='append',dest='dirs',help='list of directories to be included. (PART) PART/TITLE/FIGS')
parser.add_option("-e","--exclude",action='append',dest='exclude',help='Exclude regexp on the filename',default=[])
parser.add_option("-o","--output",dest='output',help='Output TeX file. Default=%default',default="output.tex")

bk=OptionGroup(parser,"Backup options")
bk.add_option("-b","--backup",action="store_true",help="Include Backup",default=False)
bk.add_option("","--bdir",action='append',dest='bdirs',help='list of directories to be included in backup. (PART) PART/TITLE/FIGS')
bk.add_option("-i","--b-include",action='append',dest='binclude',help='Include regexp on the filename',default=[])
bk.add_option("","--b-exclude",action='append',dest='bexclude',help='Exclude regexp on the filename',default=[])

parser.add_option_group(bk)

(opts,argv)= parser.parse_args()

partCounter=1

def WritePreamble(f):
	preamble=r"""
	%%%% Created by makePresentation.py %%%%
	\documentclass[mathserif,red,t]{beamer}
	\usepackage{hyperref}
	\usepackage{amsmath}
	\usepackage{microtype}
	\usepackage{graphicx}
	\usepackage{xcolor}
	%\usepackage{multimedia}
	\usepackage[alsoload=hep]{siunitx}
	\usepackage[font=footnotesize,format=hang,indention=-.3cm,labelfont=bf,margin=0.01\textwidth]{caption}
	\usepackage{booktabs}
	\usepackage{multicol}
	\usepackage{xxcolor}
	\usepackage{alltt}
	\usepackage[utf8]{inputenc}
	\usetheme{Pittsburgh}
	\usecolortheme{lily}

	\newcommand{\Pt}{\mbox{$\textup{P}_{\scriptscriptstyle{\textup{T}}}$}}
	\newcommand{\pt}{\mbox{$\textup{P}_{\scriptscriptstyle{\textup{T}}}$}}
	\newcommand{\ptd}{$\textup{P}_{\scriptscriptstyle{\textup{T}}}D$}

	\setbeamertemplate{navigation symbols}{}
	\setbeamertemplate{frametitle}[default][left]
	\setbeamertemplate{blocks}[rounded][shadow=true]
	\setbeamertemplate{footline}[frame number]

	\begin{document}
	\part{1}

	\begin{frame}[c,plain]
        	\begin{center}
                {\Huge \scshape \usebeamercolor[fg]{frametitle} TITLE} \\
     		\bigskip
        	\bigskip
        	\bigskip
		AUTHORS,
        	\end{center}
	\end{frame}
	"""
	f.write(re.sub('\n\t','\n',preamble)) ## remove first tab, which is here for python identation

def WriteTOC(f,part=-1):
	toc=r"""
	\section{Table Of Contents}
	\begin{frame}{Table Of Contents}
	\tableofcontents""" + ("[part=%d]"%part if part>0 else "" ) + r"""
	\end{frame}
	"""
	toc=re.sub("\n\t","\n",toc)
	f.write(toc)

def WriteSection(f,Section):
	Section=re.sub("_","",Section)
	f.write(r"\section{"+Section+"}\n")

def WriteSubSection(f,Section):
	Section=re.sub("_","",Section)
	f.write(r"\subsection{"+Section+"}\n")

def WritePart(f):
	global partCounter
	partCounter+=1
	f.write(r"\part{"+str(partCounter)+"}\n")

def WriteFrameTwoFigs(f,Title,Img1,Img2):
	Title=re.sub('_','',Title)
	Title=re.sub('[^/]*/','',Title)
	frame=r"""
	\begin{frame}[c]{""" + Title + r"""}
	\bigskip	
	\includegraphics[width=0.49\textwidth]{""" + Img1+ r"""}
	\includegraphics[width=0.49\textwidth]{""" + Img2+ r"""}
	\end{frame}
	"""
	frame=re.sub('\n\t','\n',frame)
	f.write(frame)

def WriteFrameOneFig(f,Title,Img1):
	Title=re.sub('_','',Title)
	Title=re.sub('[^/]*/','',Title)
	frame=r"""
	\begin{frame}[c]{""" + Title + r"""}
	\bigskip	
	\includegraphics[width=0.49\textwidth]{""" + Img1+ r"""}
	\end{frame}
	"""
	frame=re.sub('\n\t','\n',frame)
	f.write(frame)

def WritePostamble(f):
	postamble=r"""
	\end{document}
	"""
	postamble=re.sub('\n\t','\n',postamble)
	f.write(postamble)

############################## BACKUP UTILS ################
def WriteBackupSlide(f):
	backup=r"""
	\newcounter{finalframe}
	\setcounter{finalframe}{\value{framenumber}}
	\section{Backup} %%% put a reference for the TOC
	%%\part{2}
	\begin{frame}[c]
	        \begin{center}
	                {\LARGE \scshape \usebeamercolor[fg]{frametitle} Backup Slides}
	        \end{center}
	\end{frame}
	"""
	backup=re.sub('\n\t','\n',backup)
	f.write(backup)
def WriteCloseBackup(f):
	f.write(r"\setcounter{framenumber}{\value{finalframe}}")
	f.write("\n")


if __name__=="__main__":
	f=open(opts.output,"w")	
	WritePreamble(f)
	WriteTOC(f)
	for part in opts.dirs:	
	     titles=glob(part+"/*")
	     #WritePart(f)
	     WriteSection(f,part)
	     for title in titles:
	          WriteSubSection(f,title)
	          figs=glob(title+"/*.pdf")
		  figs2=[]
		  for cand in figs:
			  exclude=False
			  for e in opts.exclude:
				  if re.search(e,cand): exclude=True
			  if not exclude: figs2.append(cand)
		  figs=figs2[:] #copy back in figs
	          while len(figs)>1:
			Img1=figs[0]
			Img2=figs[1]
			figs=figs[2:]
			#print "Adding frame", title, " for figs:",Img1,Img2
			WriteFrameTwoFigs(f,title,Img1,Img2)
	          if len(figs)>0:
	          	WriteFrameOneFig(f,title,Img1)
	if opts.backup: ## activate Backup
		WriteBackupSlide(f)
		WritePart(f) ## put the reference to the backup slides in the previous part
		WriteTOC(f,partCounter)
		for part in opts.bdirs:	
			titles=glob(part+"/*")
			WriteSection(f,part)
	 		for title in titles:
	 		     WriteSubSection(f,title)
	 		     figs=glob(title+"/*.pdf")
	 		     figs2=[]
	 		     for cand in figs:
	 		   	  exclude=False
	 		   	  for e in opts.bexclude:
	 		   		if re.search(e,cand): exclude=True
			          for i in opts.binclude:
			          	if not re.search(i,cand): exclude=True;
	 		   	  if not exclude: figs2.append(cand)
	 		     figs=figs2[:] #copy back in figs
	 		     while len(figs)>1:
	 		   	Img1=figs[0]
	 		   	Img2=figs[1]
	 		   	figs=figs[2:]
	 		   	#print "Adding frame", title, " for figs:",Img1,Img2
	 		   	WriteFrameTwoFigs(f,title,Img1,Img2)
	 		     if len(figs)>0:
	 		     	WriteFrameOneFig(f,title,Img1)
	    	WriteCloseBackup(f) 
	WritePostamble(f)
