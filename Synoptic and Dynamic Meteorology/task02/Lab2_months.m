clear all
close all
clc

station = 17220;
region  = 'europe';

YY = 2024;
MM = 2 ;

numDays = eomday(YY, MM);

%% Preparing the data

pressureLevels = [1000, 925, 850, 700, 500]; % hPa
numLevels = numel(pressureLevels);

% Calculate daily values for each isobaric level
dailyTEMP = NaN(numDays, numLevels);  
dailyHGHT = NaN(numDays, numLevels);  
dailyWSPD = NaN(numDays, numLevels);  
dailyRHUM = NaN(numDays, numLevels);  
dailyThickness = NaN(numDays, 1); 
standTEMP = NaN(numDays, 1);  
LCL = NaN(numDays,1);
daily_lw = zeros(1, numDays);
calculatedHeight = NaN(numDays, numLevels);

for DD = 1:numDays
    HH = 0;
    filename = ['RWS_' num2str(station) '_' datestr(datenum(YY, MM, DD), 12) '.htm'];
    
    try
        % Download and process data
        downloadUA_1(region, station, YY, MM, DD, HH);
        [startRow, endRow] = read_UA_html(filename);
        mat = importfile(filename, startRow, endRow);
        
        PRES    = table2array( mat(:,1) );                 % hPa
        HGHT    = table2array( mat(:,2) );                 % m
        TEMP    = table2array( mat(:,3) );                 % C
        DWPT    = table2array( mat(:,4) );                 % C
        RHUM    = table2array( mat(:,5) );                 % g/kg
        MIXR    = table2array( mat(:,6) );                 % g/kg
        DRCT    = table2array( mat(:,7) );                 % deg
        WSPD    = table2array( mat(:,8) ) * 0.514;         % m/s

        EVPR    = (29/18) * PRES .* MIXR/1000;             % h
        


        % Read the file content to find the "Precipitable water [mm]" value
        fileContent = fileread(filename);
        targetString = "Precipitable water [mm] for entire sounding:";
        idx = strfind(fileContent, targetString);
        
        if ~isempty(idx)
            % Extract the value following the target string
            valueStr = regexp(fileContent(idx:end), ':\s*([\d.]+)', 'tokens', 'once');
            if ~isempty(valueStr)
                daily_lw(DD) = str2double(valueStr{1});
            else
                daily_lw(DD) = 0; % If parsing fails, set to zero
            end
        else
            daily_lw(DD) = 0; % If target string not found, set to zero
        end

        
        % Store data for  ground level
        groundTEMP(DD) = TEMP(1);        
        groundPRES(DD) = PRES(1);        
        groundWSPD(DD) = WSPD(1);       
        groundRHUM(DD) = RHUM(1);     
        
        for ii = 1:numLevels
            pressureLevel = pressureLevels(ii);

            % Calculate the height for the current pressure level using ground pressure
            calculatedHeight(DD, ii) = -17 * log(pressureLevel / groundPRES(DD));

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
        
        % Calculate standard atmosphere temp
        standTEMP(DD) = groundTEMP(DD) - 6.5 * (dailyHGHT(DD, 1));


        % Calculate LCL
        if ~isnan(TEMP(1)) && ~isnan(DWPT(1))
            LCL(DD) = ((TEMP(1) - DWPT(1)) * 125); % m
        else
            LCL(DD) = NaN; 
        end

        % % Calculate PW 
        % PW(DD) = sum(0.5 * (MIXR(1:end-1) + MIXR(2:end)) .* (-diff(PRES))) / 100000;

    catch ME
        warning('Failed to process %s: %s', datestr(datenum(YY, MM, DD)), ME.message);
    end
end


%% TASK 1a - Timeseries on isobaric levels

% %Generate separate figures for each pressure level
% for ii = 1:numLevels
%     pressureLevel = pressureLevels(ii);
% 
%     figure;
% 
%     % Subplot 1: Temperature
%     subplot(2, 2, 1);
%     hold on;
%     plot(1:numDays, dailyTEMP(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Observed Temperature');
%     plot(1:numDays, standTEMP, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Standard Atmosphere Temperature');
%     grid on;
%     xlabel('Day of Month');
%     ylabel('Temperature (°C)');
%     title(sprintf('Timeseries: Temperature at %.0f hPa', pressureLevel));
%     legend('Location','Best')
%     set(gca, 'FontSize', 12);
% 
%     % Subplot 2: Height
%     subplot(2, 2, 2);
%     hold on;
%     plot(1:numDays, dailyHGHT(:, ii), 'o-', 'LineWidth', 1.5, 'DisplayName', 'Height');
%     plot(1:numDays, calculatedHeight(:, ii), 'x-', 'LineWidth', 1.5, 'DisplayName', sprintf('Calculated Height at %.0f hPa', pressureLevel));
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
%         % Add Thickness subplot after the 500 hPa figure
%         if pressureLevel == 500
%             figure;
%             plot(1:numDays, dailyThickness, 'o-', 'LineWidth', 1.5, 'DisplayName', 'Thickness 1000-500 hPa');
%             grid on;
%             xlabel('Day of Month');
%             ylabel('Thickness (km)');
%             title('Thickness between 1000 and 500 hPa');
%             set(gca, 'FontSize', 12);
%         end
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

%% TASK 1c - Timeseries : LCL, pricipitable water, reversal zone,saturation zone
 
%Plot daily LCL
figure;
subplot(2,2,1);
plot(1:numDays, LCL, 'o-', 'LineWidth', 1.5, 'DisplayName', 'LCL');
grid on;
xlabel('Day of Month');
ylabel('LCL (m)');
title('Daily Lifting Condensation Level (LCL)');
set(gca, 'FontSize', 12);

% Plot the daily precipitation water
subplot(2,1,2);
plot(1:numDays, daily_lw, '-o', 'LineWidth', 1.5, 'MarkerSize', 6);
grid on;
xlabel('Day of the Month');
ylabel('Precipitable Water (mm)');
title('Daily Precipitable Water for the Month');
set(gca, 'FontSize', 12);
if ~isempty(valid_lw)
    ylim([min(valid_lw) - 0.5, max(valid_lw) + 0.5]);
else
    disp('No valid data available for daily precipitable water.');
end


% Reversal zones -> where the lapse rate increases with height
lapseRate = NaN(numDays, numLevels - 1);  
increasingLapseLayerHeight = NaN(numDays, 1); 


for DD = 1:numDays
    % Calculate lapse rate for each consecutive pair of levels
    for ii = 1:numLevels - 1
        dT = dailyTEMP(DD, ii) - dailyTEMP(DD, ii+1);  % Temperature difference (°C)
        dZ = dailyHGHT(DD, ii) - dailyHGHT(DD, ii+1);  % Height difference (km)
        lapseRate(DD, ii) = dT / dZ;
    end

   for ii = 1:numLevels - 2
        if lapseRate(DD, ii+1) > lapseRate(DD, ii)  
            increasingLapseLayerHeight(DD) = dailyHGHT(DD, ii+1); 
            break; 
        end
    end
end

subplot(2,2,3);
plot(1:numDays, increasingLapseLayerHeight, 'o-', 'LineWidth', 1.5);
grid on;
xlabel('Day of the Month');
ylabel('Layer Height (km)');
title('Reversal Zones');
set(gca, 'FontSize', 12);


% Saturation zones
RHUM100LayerHeight = NaN(numDays, 1);  

for DD = 1:numDays
    for ii = 1:numLevels
        if dailyRHUM(DD, ii) == 100  
            RHUM100LayerHeight(DD) = dailyHGHT(DD, ii);  
            break;  
        end
    end
end

subplot(2,2,4);
bar(1:numDays, RHUM100LayerHeight, 'FaceColor', 'b');
grid on;
xlabel('Day of the Month');
ylabel('Layer Height (km)');
title('Saturation zones');
set(gca, 'FontSize', 12);

