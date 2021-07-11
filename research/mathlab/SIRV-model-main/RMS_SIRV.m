% function to calculate the normalized RMSE
function e=RMS_SIRV(par,I,R,T,dt)

beta=par(1);
gamma=par(2);
[~,Ifit,Rfit,~] = SIRV_model(0,beta,gamma,I(1),R(1),0,T,dt,zeros(1,T/dt));

e=rms(I-Ifit(1:1/dt:end)')+rms(R-Rfit(1:1/dt:end)');



