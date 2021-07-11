%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATLAB Code for COVID-19 pandemic prediction with the SIRV model proposed
% in the following work:
% Modeling the Effect of Population-Wide Vaccination on the Evolution of COVID-19 epidemic in Canada
% by Intissar Harizi, Soulaimane Berkane, and Abdelhamid Tayebi
% Soulaimane Berkane, Jan 15, 2021
% Contact: soulaimane.berkane@uqo.ca
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all; clc;
%% Selection of the population
population='Fortaleza'; 
vaccine_rate_1000=[1]; % possible vaccination rates per 1,000 population
alpha=[0.50]; %possible vaccine efficacies
startDate= datenum('8-Jul-2021'); %start day of the data
endDate=datenum('8-Jul-2021'); %end day of the data, start day of the prediction
predictionEndDate=datenum('12-Dec-2023'); %end day of the prediction
horizon=predictionEndDate-endDate; % prediction horizon
tmonths=startDate:30:(predictionEndDate);
disp(tmonths)
%% Model parameters
%beta: rate of infection
%gamma:  rate of removal
%alpha: vaccine efficacy
%mu: mortality rate
%N: total number of population
%I0: initial infected sub-population at startDate
%R0: initial removed sub-population at startDate
if strcmp(population,'Fortaleza')
    beta = 9.76e-2; 
    gamma =7.81e-2;
    mu=1.9e-2;
    N =6587940;
    I0 = 16089;
    R0 = 0;
end
%% Simulation of the model
vaccine_rate=vaccine_rate_1000*N/1000; % possible vaccination rates
I0=I0/N; R0=R0/N;V0=0; % state variables are normalized
dt=1;% time interval between two integration samples (1 hour)
t0=endDate-startDate+1;
tf=t0+horizon;
disp ("The value of tf is:"), disp (tf)
t=startDate:dt:predictionEndDate;
vaccine_start_day=t0;
% Simulation of the model without vaccination
[S,I,R,~] = SIRV_model(0,beta,gamma,I0,R0,V0,tf-1,dt,zeros(1,(tf-1)/dt));
for i=2:length(I)
   newCases(i-1)=(1/dt)*(I(i)+R(i)-I(i-1)-R(i-1));
   newDeaths(i-1)=(1/dt)*mu*(R(i)-R(i-1));
end
sz=0.5;
figure(1);hold on;plot(t(1:end-1),I*N,'LineWidth',sz,'DisplayName','Without Vaccination');grid on;box on;
ax1=get(gcf,'CurrentAxes');
figure(2);hold on;plot(t(1:end-1),R*N,'LineWidth',sz,'DisplayName','Without Vaccination');grid on;box on;
ax2=get(gcf,'CurrentAxes');
figure(3);hold on;plot(t(1:end-2),newCases*N,'LineWidth',sz,'DisplayName','Without Vaccination');grid on;box on;
ax3=get(gcf,'CurrentAxes');
figure(4);hold on;plot(t(1:end-2),newDeaths*N,'LineWidth',sz,'DisplayName','Without Vaccination');grid on;box on;
ax4=get(gcf,'CurrentAxes');
% Simulation of the model with vaccination at different rates
vaccine_end_day=tf;
for k=1:length(alpha)
    sz=0.5;
    set(ax1,'ColorOrderIndex',2)
    set(ax2,'ColorOrderIndex',2)
    set(ax3,'ColorOrderIndex',2)
    set(ax4,'ColorOrderIndex',2)
    for n=1:length(vaccine_rate)
            u_vacc=vaccine_pulse(vaccine_rate(n),vaccine_start_day,vaccine_end_day,tf,dt,N);
            [S_vacc,I_vacc,R_vacc,~] = SIRV_model(alpha(k),beta,gamma,I0,R0,V0,tf-1,dt,u_vacc); 
            if any(S_vacc==0)
                vaccine_end_day=floor(find(S_vacc==0,1)*dt);
            end
            for i=2:length(I_vacc)
               newCases_vacc(i-1)=24*(I_vacc(i)+R_vacc(i)-I_vacc(i-1)-R_vacc(i-1));
               newDeaths_vacc(i-1)=24*mu*(R_vacc(i)-R_vacc(i-1));
            end
            if k==1   
                txt = [num2str(vaccine_rate_1000(n)),' vaccine per 1,000 (95\% efficacy)'];
                sz=sz+0.5;
                figure(1);plot(t(1:end-1),I_vacc*N,'LineWidth',sz,'DisplayName',txt);
            else
                txt = [num2str(vaccine_rate_1000(n)),' vaccine per 1,000 (60\% efficacy)'];
                sz=sz+0.5;
                figure(1);plot(t(1:end-1),I_vacc*N,'--','LineWidth',sz,'DisplayName',txt);
            end
    end
end

figure(1)
ylim([0 max(I)*N])
line=plot([endDate endDate],[0 max(I)*N],'k--','LineWidth',2);
ylabel('Infected (active cases) $I(t)$','Interpreter','latex','fontsize',14)
ax = gca;
set (ax, "xtick", datenum (1990:5:2005,1,1));
datetick ("x", 2, "keepticks");
datetick('x','mm-YY')

