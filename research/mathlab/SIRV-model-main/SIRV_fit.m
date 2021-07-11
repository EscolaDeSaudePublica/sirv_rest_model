%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATLAB Code for the fitting of the SIRV model proposed
% in the following work:
% Modeling the Effect of Population-Wide Vaccination on the Evolution of COVID-19 epidemic in Canada
% by Intissar Harizi, Soulaimane Berkane, and Abdelhamid Tayebi
% Soulaimane Berkane, Jan 15, 2021
% Contact: soulaimane.berkane@uqo.ca
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Load data
clear all;clc;close all
population='Canada';
data = xlsread('COVID19-Data-Canada',population);
N=data(1,1);
I=data(:,2);
R=data(:,3);
D=data(:,4);
S=N*ones(size(I))-R-I;
startDate= datenum('17-Jul-2020'); %start day of the data
endDate=datenum('08-Jan-2021'); %end day of the data
tmonths=startDate:30:(endDate);
%% Fitting R0;
clear x y
yS=log(S/S(1)); 
yS=yS(1:end);
xS=R(1:end)-R(1)*ones(size(R(1:end)));
R0=-(xS\yS)*N;
%% Fitting for gamma
idx=1;
for t=2:length(I)
   
    xR(idx)=trapz(1:t,I(1:t));
    yR(idx)=R(t)-R(1);
    idx=idx+1;
end
gamma=xR'\yR';
beta=gamma*R0;
%% Fitting for mu
xD=R(1:end)-R(1);
yD=D(1:end)-D(1);
mu=xD\yD;
yDfit=mu*xD;
%% Simulate the identified model
dt=1/24;
T=length(I)-1+dt;
[par,rms]=fminsearch(@(par)RMS_SIRV(par,I(1:end)/N,R(1:end)/N,T,dt),[beta gamma]);
beta=par(1);
gamma=par(2);
R0=beta/gamma;
[~,x2,x3,~] = SIRV_model(0,beta,gamma,I(1)/N,R(1)/N,0,T,dt,zeros(1,T/dt));
Dfit=mu*(x3-x3(1))*N+D(1);
t=startDate:dt:endDate;

% Plot the figures
figure(4)
plot(t,x2*N,'LineWidth',1.5);grid on; hold on; box on;
stem(startDate:endDate,I(1:end),'o')
ylabel('Infected $I(t)$','Interpreter','latex','fontsize',15)
title(population,'Interpreter','latex','fontsize',15)
legend({'Fitted Model','Real Data'},'Interpreter','latex','fontsize',15)
ax=gca;
ax.XTick=tmonths;
xtickangle(90)
datetick('x','mmm-yy')
set(gca,'TickLabelInterpreter','latex','fontsize',15)
xlim([startDate endDate])
ax.YAxis.Exponent = 3;
ySfit = -R0*xS/N;
axes('position',[.25 .6 .25 .25])
hold on;grid on;box on
plot(xS+R(1),ySfit,'-.','LineWidth',2); 
scatter(xS+R(1),yS)
xlim([R(1) R(end)])
ylabel('$\log(S(t)/S(t_0))$','Interpreter','latex','fontsize',14)
xlabel('$R(t)$','Interpreter','latex','fontsize',14)


figure(5)
plot(t,x3*N,'LineWidth',1.5);grid on; hold on; box on;
stem(startDate:endDate,R(1:end),'o')
ylabel('Removed $R(t)$','Interpreter','latex','fontsize',15)
title(population,'Interpreter','latex','fontsize',15)
legend({'Fitted Model','Real Data'},'Interpreter','latex','fontsize',15)
ax=gca;
ax.XTick=tmonths;
xtickangle(90)
datetick('x','mmm-yy')
set(gca,'TickLabelInterpreter','latex','fontsize',15)
xlim([startDate endDate])
axes('position',[.25 .6 .25 .25])
hold on;grid on;box on
yRfit = gamma*xR;
plot(xR,yRfit+R(1),'-.','LineWidth',2); 
scatter(xR,yR+R(1))
ylabel('$R(t)$','Interpreter','latex','fontsize',14)
xlabel('$\int_{t_0}^tI(\tau)d\tau$','Interpreter','latex','fontsize',14)

figure(6)
plot(t,Dfit,'LineWidth',1.5);grid on; hold on; box on;
stem(startDate:endDate,D(1:end),'o')
ylabel('Deaths $D(t)$','Interpreter','latex','fontsize',15)
title(population,'Interpreter','latex','fontsize',15)
legend({'Fitted Model','Real Data'},'Interpreter','latex','fontsize',15)
ax=gca;
ax.YAxis.Exponent = 3;
ax.XTick=tmonths;
xtickangle(90)
datetick('x','mmm-yy')
set(gca,'TickLabelInterpreter','latex','fontsize',15)
xlim([startDate endDate])
axes('position',[.25 .6 .25 .25])
hold on;grid on;box on;
plot(xD+R(1),yDfit+D(1),'-.','LineWidth',2); 
scatter(xD+R(1),yD+D(1))
xlim([R(1) R(end)])
ylabel('$D(t)$','Interpreter','latex','fontsize',14)
xlabel('$R(t)$','Interpreter','latex','fontsize',14)

