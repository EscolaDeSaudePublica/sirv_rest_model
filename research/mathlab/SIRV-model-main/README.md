# SIRV-model
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATLAB Code for COVID-19 pandemic prediction with the SIRV model proposed
% in the following work:
% Modeling the Effect of Population-Wide Vaccination on the Evolution of COVID-19 epidemic in Canada
% by Intissar Harizi, Soulaimane Berkane, and Abdelhamid Tayebi
% Soulaimane Berkane, Jan 15, 2021
% Contact: soulaimane.berkane@uqo.ca
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

This folder includes the following Matlab scripts that can be used to reproduce the results in the above mentioned paper. 

* SIRV_prediction.m
Matlab script to simulate the evolution of the SIRV epidemic model
under different vaccination rates and efficacy. The script contains the data and parameters to simulate the case study of COVID-19 epidemic in Canada but 
the parameters can be adapted to suit any other case study.

* SIRV_fit.m
Matlab script to for fitting the SIRV model to the data. The script reads the data from
the excel file 'COVID19-Data-Canada' directly and calculates the infection rate beta, the 
removal rate gamma, the reproduction number R0, and the mortality rate mu. It plots also 
the fitted model versus the real data.


* SIRV_model.m and RMS_SIRV.m and vaccine_pulse.m are Matlab functions that are used by the 
Matlab scripts described above.
