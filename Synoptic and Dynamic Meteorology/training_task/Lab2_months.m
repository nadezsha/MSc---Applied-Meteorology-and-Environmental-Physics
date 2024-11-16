clear all
close all
clc

station = 'LGTS';

% List of dates to process
%dates = {'20240201', '20240202', '20240203', '20240204', '20240205', '20240206', '20240207', '20240208', '20240209', '20240210','20240211', '20240212', '20240213', '20240214','20240215', '20240216', '20240217', '20240218','20240219', '20240220', '20240221', '20240222','20240223', '20240224', '20240225', '20240226','20240227', '20240228', '20240229'};  
dates = {'20240701', '20240702', '20240703', '20240704', '20240705', '20240706', '20240707', '20240708', '20240709', '20240710','20240711', '20240712', '20240713', '20240714','20240715', '20240716', '20240717', '20240718','20240719', '20240720', '20240721', '20240722','20240723', '20240724', '20240725', '20240726','20240727', '20240728', '20240729', '20240730', '20240731'};  


% Initialize an array to store the daily maximum, minimum and mean temperatures
daily_max_temp = NaN(1, length(dates));
daily_min_temp = NaN(1, length(dates));
daily_mean_temp = NaN(1, length(dates));

% Initialize an array to store the daily maximum, minimum and mean
% windspeed
daily_max_wspd = NaN(1, length(dates));
daily_min_wspd = NaN(1, length(dates));
daily_mean_wspd = NaN(1, length(dates));

% Initialize an array to store the daily maximum, minimum and mean relative
% humidity
daily_max_rhum = NaN(1, length(dates));
daily_min_rhum = NaN(1, length(dates));
daily_mean_rhum = NaN(1, length(dates));
daily_weather_binary = NaN(1, length(dates));

for i = 1:length(dates)
    DATE = dates{i};   % Current date in the loop

    % Create the filename based on the current date
    filename = ['SFC_' station '_' DATE '.htm'];

    %% A download file
    %downloadSFC(station, DATE)

    %% B import matrix
    [formatSpec, nvars, startRow, endRow] = read_SFC_html(filename);
    mat = importfile(filename, formatSpec, nvars, startRow, endRow);

    PRES = str2double(mat(:, 3));
    TEMP = str2double(mat(:, 4));
    TDEW = str2double(mat(:, 5));
    RHUM = str2double(mat(:, 6));
    WDIR = str2double(mat(:, 7));  
    WSPD = str2double(mat(:, 8));  
    weather = mat(:, end);

    daytime = split(mat(:, 2), '/');
    time1 = str2double(daytime(:, 2));
    hour = floor(time1 / 100);
    minute = (time1 - 100 * hour) / 60;
    tstamp = hour + minute;

    % weather column for rainfall
    
    weather_binary = cellfun(@(x)~isempty(x),weather); % 0 if empty, 1 otherwise
    

    %% C plot matrix
    %figure
    %subplot(2, 3, 1)
    %plot(tstamp, TEMP, 'o'); xlabel('Hour of the day'); ylabel('TEMP (C)'); hold on
    %p = polyfit(tstamp, TEMP, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
    %[~, imax] = max(y1); t1 = tstamp(imax);
    %[~, imin] = min(y1); t2 = tstamp(imin);
    %DTR = max(TEMP) - min(TEMP);
    %set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

    %subplot(2, 3, 2)
    %plot(tstamp, TDEW, 'o'); xlabel('Hour of the day'); ylabel('TDEW (C)'); hold on
    %p = polyfit(tstamp, TDEW, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
    %[~, imax] = max(y1); t3 = tstamp(imax);
    %[~, imin] = min(y1); t4 = tstamp(imin);
    %set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

    %subplot(2, 3, 3)
    %plot(tstamp, RHUM, 'o'); xlabel('Hour of the day'); ylabel('RHUM (%)'); hold on
    %p = polyfit(tstamp, RHUM, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
    %[~, imax] = max(y1); t5 = tstamp(imax);
    %[~, imin] = min(y1); t6 = tstamp(imin);
    %set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

    %subplot(2, 3, 4)
    %plot(tstamp, PRES, 'o'); xlabel('Hour of the day'); ylabel('PRES (hPa)'); hold on
    %p = polyfit(tstamp, PRES, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
    %set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

    %subplot(2, 3, 5)
    %plot(tstamp, WSPD, 'o'); xlabel('Hour of the day'); ylabel('WSPD (m/s)'); hold on
    %p = polyfit(tstamp, WSPD, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
    %set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

    %subplot(2, 3, 6)
    %tf = find(WSPD > 0);
    %histogram(WDIR(tf), 11.25:22.5:360, 'Normalization', 'probability')
    %xlabel('WDIR (deg)'); ylabel('Probability')
    %set(gca, 'XTick', 0:45:360, 'XGrid', 'on', 'FontSize', 14); xlim([0 360])

    %disp(['Results for date: ' DATE])
    %disp('Timing of peak values:')
    %disp(['TMIN  at ', num2str(t2, '%10.2f\n'), 'Z and TMAX  at ', num2str(t1, '%10.2f\n'), 'Z'])
    %disp(['SDMIN at ', num2str(t4, '%10.2f\n'), 'Z and SDMAX at ', num2str(t3, '%10.2f\n'), 'Z'])
    %disp(['RHMIN at ', num2str(t6, '%10.2f\n'), 'Z and RHMAX at ', num2str(t5, '%10.2f\n'), 'Z'])

    %disp('Indices:')
    %disp(['DTR = ', num2str(DTR, '%10.2f\n')])

    % Store the daily temperatures
    daily_max_temp(i) = max(TEMP);
    daily_min_temp(i) = min(TEMP);
    daily_mean_temp(i) = mean(TEMP,'omitnan')

    % Store the daily windspeeds
    daily_max_wspd(i) = max(WSPD);
    daily_min_wspd(i) = min(WSPD);
    daily_mean_wspd(i) = mean(WSPD,'omitnan')

    % Store the daily relative humidities
    daily_max_rhum(i) = max(RHUM);
    daily_min_rhum(i) = min(RHUM);
    daily_mean_rhum(i) = mean(RHUM,'omitnan')

    % Rainfall of the day
    daily_weather_binary(i) = any(weather_binary);

    % Optionally, save the plot with the date
    % saveas(gcf, ['SFC_' station '_' DATE '.png']);
end

% Convert dates to datetime
dates_dt = datetime(dates, 'InputFormat', 'yyyyMMdd');

% % Plot the daily temperatures across all dates
% figure;
% subplot(3,3,1);
% plot(dates_dt, daily_max_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Maximum Temperature (°C)');
% title('Daily Maximum Temperature for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,2);
% plot(dates_dt, daily_min_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Minimum Temperature (°C)');
% title('Daily Minimum Temperature for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,3);
% plot(dates_dt, daily_mean_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Mean Temperature (°C)');
% title('Daily Mean Temperature for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% % Plot the daily windspeeds across all dates
% subplot(3,3,4);
% plot(dates_dt, daily_max_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Maximum Windspeed (m/s)');
% title('Daily Maximum Windspeed for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,5);
% plot(dates_dt, daily_min_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Minimum Windspeed (m/s)');
% title('Daily Minimum Windspeed for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,6);
% plot(dates_dt, daily_mean_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Mean Windspeed (m/s)');
% title('Daily Mean Windspeed for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% % Plot the daily relative humidities across all dates
% subplot(3,3,7);
% plot(dates_dt, daily_max_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Maximum Relative Humidity (%)');
% title('Daily Maximum Relative Humidity for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,8);
% plot(dates_dt, daily_min_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Minimum Relative Humidity (%)');
% title('Daily Minimum Relative Humidity for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;
% 
% subplot(3,3,9);
% plot(dates_dt, daily_mean_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8);
% xlabel('Date');
% ylabel('Daily Mean Relative Humidity (%)');
% title('Daily Mean Relative Humidity for Each Date');
% xtickangle(45); % Rotate date labels for readability
% grid on;


%% D plot binary weather data

figure;
stem(dates_dt, daily_weather_binary, 'LineWidth',2);
xlabel('Date');
ylabel('Rainfall');
set(gca, 'YTick', [0 1]);
ylim([-0.1,1.1]);
title('Daily Rainfall');
grid on;
xtickangle(45);