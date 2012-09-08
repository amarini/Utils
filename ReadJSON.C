#include <cstdio>
#include <map>
#include <set>

using namespace std;
#ifndef READ_JSON_H
#define READ_JSON_H

#define ERR_NOFILE 1
#define ERR_JSON 2
#define ERR_NOTEND 2
#define CONT -1
#define END 0

class JSON {
public:
	int ReadJSON(const char * fileName="json.txt");
	bool Find(long Run,long Lumi);
private:
	map <long,set<pair<long,long> > >  J;
	FILE *fr;
	int LeggiLumis();
	int LeggiLumi();
	int LeggiRun();
	long RunNum;
	
	
};

#endif

int JSON::ReadJSON(const char * fileName)
{
fr=fopen(fileName,"r");
if(fr==NULL){fprintf(stderr,"No such file or directory: %s\n",fileName);return ERR_NOFILE;};
//RunNum, Set<pair<lumiRange>>
char c;
	//try to find '{'
	bool start=false;
	while ( fscanf(fr,"%c",&c)!=EOF){if(c=='{') start=true;break;}
	if(!start){fprintf(stderr,"Not well formatted JSON\n"); return ERR_JSON;}
	//loop
	while( fscanf(fr,"%c",&c) !=EOF ){
		if(c=='}'){start =false; return 0;} //until end
		//Leggi RUN
		int status=CONT;
		while( status == CONT ){
					int R;
					if(  (R=LeggiRun()) ) {return R;} ;
					status = LeggiLumis();
					}
		if(status == END) return END;
			
	}
fprintf(stderr,"JSON don't end\n");
return ERR_NOTEND;
}

int JSON::LeggiRun(){ // "RunNum":
	char c;
	bool open=false;
	while( fscanf(fr,"%c",&c)!=EOF) //look for open "
		{
		if(c=='"'){if(fscanf(fr,"%ld",&RunNum)==EOF)return ERR_JSON;else {open=true;break;}}
		}
	//look for close "
	while( fscanf(fr,"%c",&c)!=EOF) { if(c=='"'){open=false;break;}}
	if(open) return ERR_JSON;
	open=false;
	while( fscanf(fr,"%c",&c)!=EOF) { if(c==':'){open=true;break;}}
	if(!open)return ERR_JSON;
	return 0;	
	}
int JSON::LeggiLumis() // [ ....], RETURN -1= continue; 0 NOT CONTINUE (comma)
	{
	bool open=false;
	char c;
	while( fscanf(fr,"%c",&c)!=EOF) {
					if(c=='['){open=true;break;}
					}
	int R=CONT;
	while( (R=LeggiLumi() ) == CONT ) {}
	if(R==END) {//Look for a comma or a }
			while( fscanf(fr,"%c",&c) !=EOF ){if( c=='}'){return END;}
							  if(c==','){return CONT;}
							}
			return ERR_JSON;
			}
	else return R; //error
	
	}
int JSON::LeggiLumi() //leggi [A,B],[A,B] ] <-- return -1 continue (,) 0 (])
	{
	char c;
	bool open = false;
	while (fscanf(fr,"%c",&c) != EOF) { if(c=='['){open=true;break;} }
	if(!open) return ERR_JSON;
	long lumi1,lumi2;
	if(fscanf(fr,"%ld",&lumi1) ==EOF) return ERR_JSON;
	bool comma=false;
	while (fscanf(fr,"%c",&c) != EOF) { if(c==','){comma=true;break;} }  ;  if(!comma) return ERR_JSON;
	if(fscanf(fr,"%ld",&lumi2) ==EOF) return ERR_JSON;
	
	//map <long,set<pair<long,long> > >  J; 
	J[RunNum].insert(pair<long,long>(lumi1,lumi2));

	while (fscanf(fr,"%c",&c) != EOF) { if(c==']'){open=false;break;} }  ; if(open) return ERR_JSON;
	bool cont=false,end=false;
	while (fscanf(fr,"%c",&c) != EOF) { if(c==']'){end=true;break;} if(c==',') {cont=true;break;}}  ; 
	if(cont)return CONT;	
	if(end) return END;
	return ERR_JSON;
	}

bool JSON::Find(long Run,long Lumi)
	{
	//if(J[Run] == 0)return false;
	if(J[Run].empty())return false;
	//map <long,set<pair<long,long> > >  J; 
	for( set<pair<long,long> >::iterator it=J[Run].begin();it!=J[Run].end();it++)
		{
		long Lumi1=it->first;	
		long Lumi2=it->second;
		if((Lumi > Lumi1) && (Lumi<Lumi2) ) return true;
		}
	return false;
	}

/*
{
"RunNum" : [ [],[],[] ],

"RunNum" : [ [],[],[] ],

"RunNum" : [ [],[],[] ],

"RunNum" : [ [],[],[] ]
}
*/
