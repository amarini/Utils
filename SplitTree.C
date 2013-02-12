#include "TFile.h"
#include "TTree.h"
#include <stdio.h>

int SplitTree(const char *fileName,const char *treeName,const char *outFileName,const int size=10000000)
{
TFile *fIn=TFile::Open(fileName);
if(fIn==NULL)  return 1;
TFile *fOut=TFile::Open(outFileName,"RECREATE");
if(fOut==NULL) return 2;
TTree *tIn=(TTree*)fIn->Get(treeName);
if(tIn==NULL)    return 3;
TTree::SetMaxTreeSize(size);
fOut->cd();
TTree *tOut=tIn->CloneTree();
tOut->Write();
fOut->Close();
return 0;

}

int main(int argc, char**argv)
{
if(argc<4){fprintf(stderr,"Usage:\n     %s filename treeName outFileName size",argv[0]);return -1;}
if(argc<5)
return SplitTree(argv[1],argv[2],argv[3]);

int i; sscanf(argv[4],"%d",&i);
return SplitTree(argv[1],argv[2],argv[3],i);
}
