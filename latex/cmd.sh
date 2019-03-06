

./addlabel.sh -v15pt -la Plot0_norm_both.pdf
./addlabel.sh -v15pt -lb Plot0_norm_both_boost.pdf
./addlabel.sh -v15pt -la Plot1_norm_both.pdf
./addlabel.sh -v15pt -lb Plot1_norm_both_boost.pdf
./addlabel.sh -v15pt -la Plot2_norm_both.pdf
./addlabel.sh -v15pt -lb Plot2_norm_both_boost.pdf
./addlabel.sh -v15pt -h60pt -lc Plot_Ratio0_norm_both.pdf
./addlabel.sh -v15pt -h60pt -ld Plot_Ratio0_norm_boost.pdf
./addlabel.sh -v15pt -h60pt -lc Plot_Ratio1_norm_both.pdf
./addlabel.sh -v15pt -h60pt -ld Plot_Ratio1_norm_boost.pdf
./addlabel.sh -v15pt -h60pt -lc Plot_Ratio2_norm_both.pdf
./addlabel.sh -v15pt -h60pt -ld Plot_Ratio2_norm_boost.pdf


./addlabel.sh -v15pt -la -e'\\vspace{450pt}\\\\(c)' llPt_mu.pdf
./addlabel.sh -v15pt -lb -e'\\vspace{450pt}\\\\(d)' nJets50_mu.pdf

./addlabel.sh -h "510pt" -v "450pt" -l '$\\\\mathcal{F}' -t fig2.tex control_btag_LR_SL_g6jg1t.pdf
./addlabel.sh -h "90pt" -v "38pt" -t fig3.tex -l "{\\\LARGE\\\it~Preliminary}" limits_bbA_2016_width10_biasOK.pdf
