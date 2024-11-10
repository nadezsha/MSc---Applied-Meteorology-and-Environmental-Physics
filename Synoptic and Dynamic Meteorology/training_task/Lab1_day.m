clear all
close all
clc

station = 'LGTS';
DATE    = '20241011';   % end time !!

filename = ['SFC_' station '_' DATE '.html'];
%startRow = 13;
%endRow   = 49;

%% A download file

downloadSFC(station,DATE)

%% B import matrix

[formatSpec,nvars,startRow,endRow]=read_SFC_html(filename);

mat = importfile( filename, formatSpec, nvars, startRow, endRow );

PRES    = str2double( mat(:,3) );
TEMP    = str2double( mat(:,4) );
TDEW    = str2double( mat(:,5) );
RHUM    = str2double( mat(:,6) );
WDIR    = str2double( mat(:,7) );  
WSPD    = str2double( mat(:,8) );  

daytime = split( mat(:,2) ,'/');
time1   = str2double( daytime(:,2) );
hour    = floor(time1/100);
minute  = (time1-100*hour)/60;
tstamp  = hour+minute;

%% C plot matrix
figure

subplot(2,3,1)
plot(tstamp,TEMP,'o');xlabel('Hour of the day');ylabel('TEMP (C)');hold on
p = polyfit(tstamp,TEMP,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
[~,imax]=max(y1);t1=tstamp(imax);
[~,imin]=min(y1);t2=tstamp(imin);
DTR=max(TEMP)-min(TEMP);
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24]) 

subplot(2,3,2)
plot(tstamp,TDEW,'o');xlabel('Hour of the day');ylabel('TDEW (C)');hold on
p = polyfit(tstamp,TDEW,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
[~,imax]=max(y1);t3=tstamp(imax);
[~,imin]=min(y1);t4=tstamp(imin);
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24]) 

subplot(2,3,3)
plot(tstamp,RHUM,'o');xlabel('Hour of the day');ylabel('RHUM (%)');hold on
p = polyfit(tstamp,RHUM,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
[~,imax]=max(y1);t5=tstamp(imax);
[~,imin]=min(y1);t6=tstamp(imin);
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24]) 

subplot(2,3,4)
plot(tstamp,PRES,'o');xlabel('Hour of the day');ylabel('PRES (hPa)');hold on
p = polyfit(tstamp,PRES,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24]) 

subplot(2,3,5)
plot(tstamp,WSPD,'o');xlabel('Hour of the day');ylabel('WSPD (m/s)');hold on
p = polyfit(tstamp,WSPD,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24]) 

subplot(2,3,6)
tf=find(WSPD>0);
histogram(WDIR(tf),11.25:22.5:360,'Normalization','probability')
xlabel('WDIR (deg)');ylabel('Probability')
set(gca,'XTick',0:45:360,'XGrid','on','FontSize',14);xlim([0 360])

disp('Timing of peak values:')
disp(['TMIN  at ',num2str(t2,'%10.2f\n'),'Z and TMAX  at ',num2str(t1,'%10.2f\n'),'Z']) 
disp(['SDMIN at ',num2str(t4,'%10.2f\n'),'Z and SDMAX at ',num2str(t3,'%10.2f\n'),'Z']) 
disp(['RHMIN at ',num2str(t6,'%10.2f\n'),'Z and RHMAX at ',num2str(t5,'%10.2f\n'),'Z']) 

disp('Indices:')
disp(['DTR = ',num2str(DTR,'%10.2f\n')]) 

%%
% WindRose(WDIR,WSPD,'ndirections',16,'anglenorth',0,'angleeast',90,'labels',{'N (0�)','S (180�)','E (90�)','W (270�)'},'freqlabelangle',22.5);
% set(gca,'Fontsize',16)
