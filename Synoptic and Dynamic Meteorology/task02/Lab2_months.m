clear all
close all
clc

station = 17220;
region  = 'europe';

YY = 2024;
MM = 7;

numDays = eomday(YY, MM);

%% Preparing the data

pressureLevels = [1000, 925, 850, 700, 500]; % Desired pressure levels in hPa
numLevels = numel(pressureLevels);

% Calculate daily values for each isobaric level
dailyTEMP = NaN(numDays, numLevels);  
dailyHGHT = NaN(numDays, numLevels);  
dailyWSPD = NaN(numDays, numLevels);  
dailyRHUM = NaN(numDays, numLevels);  
dailyThickness = NaN(numDays, 1);   

for DD = 1:numDays
    HH = 0;
    filename = ['RWS_' num2str(station) '_' datestr(datenum(YY, MM, DD), 12) '.htm'];
    
    try
        % Download and process data
        downloadUA(region, station, YY, MM, DD, HH);
        [startRow, endRow] = read_UA_html(filename);
        mat = importfile(filename, startRow, endRow);
        
        PRES = table2array(mat(:, 1));   % hPa
        HGHT = table2array(mat(:, 2));   % m
        TEMP = table2array(mat(:, 3));   % °C
        RHUM = table2array(mat(:, 5));   % %
        WSPD = table2array(mat(:, 8)) * 0.514; % m/s

        % Store data for  ground level
        groundTEMP(DD) = TEMP(1);        
        groundPRES(DD) = PRES(1);        
        groundWSPD(DD) = WSPD(1);       
        groundRHUM(DD) = RHUM(1);     
        

        for ii = 1:numLevels
            pressureLevel = pressureLevels(ii);

            % Find the index for the current pressure level
            [~, idx] = min(abs(PRES - pressureLevel));
            
            % Store daily values at the current pressure level
            dailyTEMP(DD, ii) = TEMP(idx);
            dailyHGHT(DD, ii) = HGHT(idx) / 1000; % Convert to km
            dailyWSPD(DD, ii) = WSPD(idx);
            dailyRHUM(DD, ii) = RHUM(idx);
        end
        
        % Calculate thickness (1000 hPa - 500 hPa)
        [~, idx1000] = min(abs(PRES - 1000));
        [~, idx500] = min(abs(PRES - 500));
        dailyThickness(DD) = (HGHT(idx500) - HGHT(idx1000)) / 1000; % Convert to km
        
    catch ME
        warning('Failed to process %s: %s', datestr(datenum(YY, MM, DD)), ME.message);
    end
end


%% TASK 1a - Timeseries on isobaric levels

% % Generate separate figures for each pressure level
% for ii = 1:numLevels
%     pressureLevel = pressureLevels(ii);
% 
%     figure;
% 
%     % Subplot 1: Temperature
%     subplot(2, 2, 1);
%     plot(1:numDays, dailyTEMP(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Temperature');
%     grid on;
%     xlabel('Day of Month');
%     ylabel('Temperature (°C)');
%     title(sprintf('Timeseries: Temperature at %.0f hPa', pressureLevel));
%     set(gca, 'FontSize', 12);
% 
%     % Subplot 2: Height
%     subplot(2, 2, 2);
%     plot(1:numDays, dailyHGHT(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Height');
%     grid on;
%     xlabel('Day of Month');
%     ylabel('Height (km)');
%     title(sprintf('Timeseries: Height at %.0f hPa', pressureLevel));
%     set(gca, 'FontSize', 12);
% 
%     % Subplot 3: Wind Speed
%     subplot(2, 2, 3);
%     plot(1:numDays, dailyWSPD(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Wind Speed');
%     grid on;
%     xlabel('Day of Month');
%     ylabel('Wind Speed (m/s)');
%     title(sprintf('Timeseries: Wind Speed at %.0f hPa', pressureLevel));
%     set(gca, 'FontSize', 12);
% 
%     % Subplot 4: Relative Humidity
%     subplot(2, 2, 4);
%     plot(1:numDays, dailyRHUM(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Relative Humidity');
%     grid on;
%     xlabel('Day of Month');
%     ylabel('Relative Humidity (%)');
%     title(sprintf('Timeseries: Relative Humidity at %.0f hPa', pressureLevel));
%     set(gca, 'FontSize', 12);
% 
%     % Add Thickness subplot after the 500 hPa figure
%     if pressureLevel == 500
%         figure; 
%         plot(1:numDays, dailyThickness, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Thickness 1000-500 hPa');
%         grid on;
%         xlabel('Day of Month');
%         ylabel('Thickness (km)');
%         title('Thickness between 1000 and 500 hPa');
%         set(gca, 'FontSize', 12);
%     end
% end


%% TASK 1b - Timeseries on the ground

% % Plot daily surface (ground) data
% figure;
% 
% % Subplot 1: Surface Temperature
% subplot(2, 2, 1);
% plot(1:numDays, groundTEMP, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Surface Temperature');
% grid on;
% xlabel('Day of Month');
% ylabel('Temperature (°C)');
% title('Surface Temperature');
% set(gca, 'FontSize', 12);
% 
% % Subplot 2: Surface Pressure
% subplot(2, 2, 2);
% plot(1:numDays, groundPRES, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Surface Pressure');
% grid on;
% xlabel('Day of Month');
% ylabel('Pressure (hPa)');
% title('Surface Pressure');
% set(gca, 'FontSize', 12);
% 
% % Subplot 3: Surface Wind Speed
% subplot(2, 2, 3);
% plot(1:numDays, groundWSPD, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Surface Wind Speed');
% grid on;
% xlabel('Day of Month');
% ylabel('Wind Speed (m/s)');
% title('Surface Wind Speed');
% set(gca, 'FontSize', 12);
% 
% % Subplot 4: Surface Relative Humidity
% subplot(2, 2, 4);
% plot(1:numDays, groundRHUM, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Surface RHUM');
% grid on;
% xlabel('Day of Month');
% ylabel('Relative Humidity (%)');
% title('Surface Relative Humidity');
% set(gca, 'FontSize', 12);