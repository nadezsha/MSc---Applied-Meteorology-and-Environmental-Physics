clear all
close all
clc

station = 'LGTS';

% List of dates to process
%dates = {'20240201', '20240202', '20240203', '20240204', '20240205', '20240206', '20240207', '20240208', '20240209', '20240210','20240211', '20240212', '20240213', '20240214','20240215', '20240216', '20240217', '20240218','20240219', '20240220', '20240221', '20240222','20240223', '20240224', '20240225', '20240226','20240227', '20240228', '20240229'};  
%dates = {'20240701', '20240702', '20240703', '20240704', '20240705', '20240706', '20240707', '20240708', '20240709', '20240710','20240711', '20240712', '20240713', '20240714','20240715', '20240716', '20240717', '20240718','20240719', '20240720', '20240721', '20240722','20240723', '20240724', '20240725', '20240726','20240727', '20240728', '20240729', '20240730', '20240731'};  
dates = {'20240212'};

%% Initial variables

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

% Initialize array to store daily weather binary (1 if "RA" or "DZ", 0 otherwise)
daily_weather_binary = NaN(1, length(dates));

% types of precipitation
weather_conditions = {'RA', 'DZ', '+RA', '-RA', '+DZ', '-DZ', 'TSRA', '+TSRA', '-TSRA', 'SHRA', '-SHRA', '+SHRA'};

% Initialize an array to store the daily cloud coverage (numeric values)
daily_cloud_coverage = NaN(1, length(dates));


%% For loop for the month
for i = 1:length(dates)
    DATE = dates{i};  
    filename = ['SFC_' station '_' DATE '.htm'];

    % download file
    %downloadSFC(station, DATE)

    % import matrix
    [formatSpec, nvars, startRow, endRow] = read_SFC_html(filename);
    mat = importfile(filename, formatSpec, nvars, startRow, endRow);

    PRES = str2double(mat(:, 3));
    TEMP = str2double(mat(:, 4));
    TDEW = str2double(mat(:, 5));
    RHUM = str2double(mat(:, 6));
    WDIR = str2double(mat(:, 7));  
    WSPD = str2double(mat(:, 8));  


    %Check if any of the rain or drizzle variants exist in the whole mat array
    if any(ismember(mat(:), weather_conditions))
        daily_weather_binary(i) = 1; % At least one condition found
    else
        daily_weather_binary(i) = 0; % None of the conditions found
    end

    % Check if the "CLOUDS" column exists (assuming columns 10, 11, 12, etc., are cloud information)
    if size(mat, 2) >= 10
        cloud_data = mat(:, 10:end);  % Extract all columns starting from the 10th
    else
        cloud_data = cell(size(mat, 1), 1); % Create an empty column for consistency
        warning(['File ', filename, ' does not contain a 10th column.']);
    end

    % Initialize an array to store the cloud types extracted from the "CLOUDS" data
    cloud_types = cell(size(cloud_data));

    % Extract the first 3 characters of the "CLOUDS" data, handling empty or short strings
    for j = 1:length(cloud_data)
        for k = 1:size(cloud_data, 2)
            % Only extract the first 3 characters if the string has at least 3 characters
            if ~isempty(cloud_data{j, k}) && length(cloud_data{j, k}) >= 3
                cloud_types{j, k} = cloud_data{j, k}(1:3);
            else
                cloud_types{j, k} = '';  % Assign empty string if less than 3 characters
            end
        end
    end

    % Map cloud types to numerical values
    cloud_mapping = containers.Map({'FEW', 'SCT', 'BKN', 'OVC'}, {25, 50, 87.5, 100});

    % Initialize an array to store the numerical cloud values for this date
    cloud_values = NaN(size(cloud_types));

    % Convert cloud types into their respective numeric values
    for j = 1:size(cloud_types, 1)
        for k = 1:size(cloud_types, 2)
            if isKey(cloud_mapping, cloud_types{j, k})
                cloud_values(j, k) = cloud_mapping(cloud_types{j, k});
            end
        end
    end

    % Find the maximum cloud coverage for the day across all columns
    daily_cloud_coverage(i) = max(max(cloud_values, [], 2), [], 'omitnan');

    
    % Initialize matrices for daily WSPD and WDIR
    daily_wspd_matrix = NaN(length(dates), size(mat, 1)); 
    daily_wdir_matrix = NaN(length(dates), size(mat, 1));

    % Extract WSPD and WDIR for the current day
    WSPD = str2double(mat(:, 8)); % Assuming column 8 is WSPD
    WDIR = str2double(mat(:, 7)); % Assuming column 7 is WDIR

    % Store them in the respective matrices
    daily_wspd_matrix(i, 1:length(WSPD)) = WSPD;
    daily_wdir_matrix(i, 1:length(WDIR)) = WDIR;
 

    daytime = split(mat(:, 2), '/');
    time1 = str2double(daytime(:, 2));
    hour = floor(time1 / 100);
    minute = (time1 - 100 * hour) / 60;
    tstamp = hour + minute;


% Convert dates to datetime
dates_dt = datetime(dates, 'InputFormat', 'yyyyMMdd');

%% TASK 1a : max/min/mean temp,wspd,rh

% Store the daily temperatures
    daily_max_temp(i) = max(TEMP);
    daily_min_temp(i) = min(TEMP);
    daily_mean_temp(i) = mean(TEMP,'omitnan');
    

    % Store the daily windspeeds
    daily_max_wspd(i) = max(WSPD);
    daily_min_wspd(i) = min(WSPD);
    daily_mean_wspd(i) = mean(WSPD,'omitnan');

    % Store the daily relative humidities
    daily_max_rhum(i) = max(RHUM);
    daily_min_rhum(i) = min(RHUM);
    daily_mean_rhum(i) = mean(RHUM,'omitnan');
  
%end % uncomment for task 1a

% figure;
% subplot(3,1,1)
% % Plot daily temperatures
% plot(dates_dt, daily_max_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'r','DisplayName', 'Max Temp');
% hold on;
% plot(dates_dt, daily_min_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'm','DisplayName', 'Min Temp ');
% plot(dates_dt, daily_mean_temp, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'b','DisplayName', 'Mean Temp');
% xlabel('Date');
% ylabel('Temperature (°C)');
% title('Daily Maximum, Minimum and Mean Temperatures');
% xtickangle(45); 
% grid on;
% legend('Location', 'best');
% 
% subplot(3,1,2)
% % Plot daily windspeeds
% plot(dates_dt, daily_max_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'r','DisplayName', 'Max Wspd');
% hold on;
% plot(dates_dt, daily_min_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'm','DisplayName', 'Min Wspd');
% plot(dates_dt, daily_mean_wspd, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'b','DisplayName', 'Mean Wspd');
% xlabel('Date');
% ylabel('Wind Speed (m/s)');
% title('Daily Maximum, Minimum and Mean Wind Speeds');
% xtickangle(45); 
% grid on;
% legend('Location', 'best');
% 
% subplot(3,1,3)
% % Plot daily relative humidities
% plot(dates_dt, daily_max_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'r','DisplayName', 'Max RH');
% hold on;
% plot(dates_dt, daily_min_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'm','DisplayName', 'Min RH');
% plot(dates_dt, daily_mean_rhum, '-o', 'LineWidth', 2, 'MarkerSize', 8, ...
%      'Color', 'b','DisplayName', 'Mean RH)');
% xlabel('Date');
% ylabel('Relative Humidity (%)');
% title('Daily Maximum, Minimum and Relative Humidity (%)');
% xtickangle(45); 
% grid on;
% legend('Location', 'best');


%% TASK 1b: Rainfall and Cloudiness (monthly)

end %uncomment for task 1b
% figure;
% bar(dates_dt, daily_weather_binary, 'FaceColor', 'b', 'EdgeColor', 'k', 'BarWidth', 0.6);
% xlabel('Date');
% ylabel('Rainfall Presence');
% title('Daily Presence of Rain or Drizzle');
% set(gca, 'YTick', [0 1]); 
% ylim([-0.05, 1.05]);  
% xticks(dates_dt); 
% xtickangle(45);          
% grid on;

% figure;
% bar(dates_dt, daily_cloud_coverage, 'FaceColor', 'b', 'EdgeColor', 'k', 'BarWidth', 0.6);
% xlabel('Date');
% ylabel('Cloud Coverage (%)');
% title('Daily Maximum Cloud Coverage');
% ylim([0, 100]);
% grid on;
% xtickangle(45); 


%% TASK 1c: G wind rose

% % Flatten matrices into 1D arrays
% all_wspd = daily_wspd_matrix(:);
% all_wdir = daily_wdir_matrix(:);
% 
% % Remove NaN values
% valid_indices = ~isnan(all_wspd) & ~isnan(all_wdir);
% all_wspd = all_wspd(valid_indices);
% all_wdir = all_wdir(valid_indices);
% 
% % Plot the wind rose
% WindRose(all_wdir, all_wspd,'ndirections',16,'anglenorth',0,'angleeast',90,'labels',{'N (0�)','S (180�)','E (90�)','W (270�)'},'freqlabelangle',22.5);
% set(gca,'Fontsize',16)

%% TASK 2: Pick four days

figure
subplot(2, 3, 1)
plot(tstamp, TEMP, 'o'); xlabel('Hour of the day'); ylabel('TEMP (C)'); hold on
p = polyfit(tstamp, TEMP, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
[~, imax] = max(y1); t1 = tstamp(imax);
[~, imin] = min(y1); t2 = tstamp(imin);
DTR = max(TEMP) - min(TEMP);
set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

subplot(2, 3, 2)
plot(tstamp, RHUM, 'o'); xlabel('Hour of the day'); ylabel('RHUM (%)'); hold on
p = polyfit(tstamp, RHUM, 4); y1 = polyval(p, tstamp); plot(tstamp(1:end-1), y1(1:end-1))
[~, imax] = max(y1); t5 = tstamp(imax);
[~, imin] = min(y1); t6 = tstamp(imin);
set(gca, 'XTick', 0:3:24, 'XGrid', 'on', 'FontSize', 14); xlim([0 24])

subplot(2,3,3)
plot(tstamp,WSPD,'o');xlabel('Hour of the day');ylabel('WSPD (m/s)');hold on
p = polyfit(tstamp,WSPD,4);y1 = polyval(p,tstamp);plot(tstamp(1:end-1),y1(1:end-1))
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24])

subplot(2,3,4)
tf=find(WSPD>0);
histogram(WDIR(tf),11.25:22.5:360,'Normalization','probability')
xlabel('WDIR (deg)');ylabel('Probability')
set(gca,'XTick',0:45:360,'XGrid','on','FontSize',14);xlim([0 360])

subplot(2,3,5)
histogram(WDIR, 'BinWidth', 10, 'FaceColor', [0.2, 0.6, 0.8], 'EdgeColor', 'k');
xlabel('WDIR (deg)');
ylabel('Hours of the day');
set(gca, 'XTick', 0:30:360, 'XGrid', 'on', 'FontSize', 14); 
xlim([0 360]); ylim([0 24])
set(gca, 'YTick', 0:3:24);


% Define rain types and assign numerical values for plotting
rain_mapping = containers.Map({'No Rain', 'Drizzle', 'Shower', 'Thunderstorm'}, {0, 1, 2, 3});
rain_types_per_hour = NaN(24, 1);

% Populate rain_types_per_hour for the date
for h = 0:23
    indices = (hour == h);
    if any(indices)
        % Check the rain type for the hour
        if any(ismember(mat(indices, 9), {'DZ', '+DZ', '-DZ'})) 
            rain_types_per_hour(h + 1) = rain_mapping('Drizzle');
        elseif any(ismember(mat(indices, 9), {'SHRA', '+SHRA', '-SHRA'}))
            rain_types_per_hour(h + 1) = rain_mapping('Shower');
        elseif any(ismember(mat(indices, 9), {'TSRA', '+TSRA', '-TSRA'}))
            rain_types_per_hour(h + 1) = rain_mapping('Thunderstorm');
        else
            rain_types_per_hour(h + 1) = rain_mapping('No Rain');
        end
    else
        rain_types_per_hour(h + 1) = rain_mapping('No Rain');
    end
end

% Plot Rain Types Per Hour
hour_labels = arrayfun(@(x) sprintf('%02d:00', x), 0:23, 'UniformOutput', false);
subplot(2,3,6)
stairs(0:23, rain_types_per_hour, 'LineWidth', 2, 'Color', 'b');
yticks([0 1 2 3]);
yticklabels({'No Rain', 'Drizzle', 'Shower', 'Thunderstorm'});
xlabel('Hour of the Day');
ylabel('Rain Type');
grid on;
set(gca,'XTick',0:3:24,'XGrid','on','FontSize',14);xlim([0 24])


%% Cloud plot for the specific date 

% cloud_types = cell(size(cloud_data));
% 
% % Extract only the first 3 characters from the "CLOUDS" columns
% for j = 1:length(cloud_data)
%     for k = 1:size(cloud_data, 2)
%         if ~isempty(cloud_data{j, k}) && length(cloud_data{j, k}) >= 3
%             cloud_types{j, k} = cloud_data{j, k}(1:3); 
%         else
%             cloud_types{j, k} = ''; 
%         end
%     end
% end
% 
% % Map cloud types to numerical values
% cloud_mapping = containers.Map({'FEW', 'SCT', 'BKN', 'OVC'}, {25, 50, 87.5, 100});
% 
% % Initialize an array to store the numerical cloud values for this date
% cloud_values = NaN(size(cloud_types));
% 
% % Convert cloud types into their respective numeric values
% for j = 1:size(cloud_types, 1)
%     for k = 1:size(cloud_types, 2)
%         if isKey(cloud_mapping, cloud_types{j, k})
%             cloud_values(j, k) = cloud_mapping(cloud_types{j, k});
%         end
%     end
% end
% 
% cloud_per_hour = NaN(24, 1);
% 
% % Calculation of cloudiness for each hour
% for h = 0:23
%     indices = (hour == h);
%     hourly_data = cloud_values(indices, :);
%     cloud_per_hour(h + 1) = max(hourly_data(:), [], 'omitnan');
% end
% 
% hour_labels = arrayfun(@(x) sprintf('%02d:00', x), 0:23, 'UniformOutput', false);
% 
% figure;
% bar(0:23, cloud_per_hour, 'FaceColor', 'b', 'EdgeColor', 'k', 'BarWidth', 0.6);
% set(gca, 'XTick', 0:23, 'XTickLabel', hour_labels);
% xlabel('Hour');
% ylabel('Cloud Coverage (%)');
% title(['Cloud Coverage (%) for the date: ', dates]);
% ylim([0, 100]); 
% grid on;
% xtickangle(45);


% Optionally log results for debugging
%fprintf('Processed %s: Weather Binary = %d\n', DATE, daily_weather_binary(i));

% Optionally, save the plot with the date
% saveas(gcf, ['SFC_' station '_' DATE '.png']);


%% Monthly Statistics

% % Temperature
% monthly_max_temp = max(daily_max_temp, [], 'omitnan');
% monthly_min_temp = min(daily_min_temp, [], 'omitnan');
% monthly_mean_temp = mean(daily_mean_temp, 'omitnan');
% monthly_std_temp = std([daily_max_temp, daily_min_temp, daily_mean_temp], 'omitnan');
% 
% % Wind Speed
% monthly_max_wspd = max(daily_max_wspd, [], 'omitnan');
% monthly_min_wspd = min(daily_min_wspd, [], 'omitnan');
% monthly_mean_wspd = mean(daily_mean_wspd, 'omitnan');
% monthly_std_wspd = std([daily_max_wspd, daily_min_wspd, daily_mean_wspd], 'omitnan');
% 
% % Relative Humidity
% monthly_max_rhum = max(daily_max_rhum, [], 'omitnan');
% monthly_min_rhum = min(daily_min_rhum, [], 'omitnan');
% monthly_mean_rhum = mean(daily_mean_rhum, 'omitnan');
% monthly_std_rhum = std([daily_max_rhum, daily_min_rhum, daily_mean_rhum], 'omitnan');
% 
% % Display results
% fprintf('Monthly Statistics:\n');
% fprintf('Temperature (°C): Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%     monthly_max_temp, monthly_min_temp, monthly_mean_temp, monthly_std_temp);
% fprintf('Wind Speed (m/s): Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%     monthly_max_wspd, monthly_min_wspd, monthly_mean_wspd, monthly_std_wspd);
% fprintf('Relative Humidity (%%): Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%     monthly_max_rhum, monthly_min_rhum, monthly_mean_rhum, monthly_std_rhum);
% 

%% Daily Statistics 

% % Define the specific date 
% specific_date_str = '20240715'; 
% specific_date = datetime(specific_date_str, 'InputFormat', 'yyyyMMdd');
% 
% % Find the index of the specific date in the dates array
% date_index = find(dates_dt == specific_date, 1);
% 
% if ~isempty(date_index)
%     % Extract max, min, mean values for the specific date
%     specific_max_temp = daily_max_temp(date_index);
%     specific_min_temp = daily_min_temp(date_index);
%     specific_mean_temp = daily_mean_temp(date_index);
% 
%     specific_max_wspd = daily_max_wspd(date_index);
%     specific_min_wspd = daily_min_wspd(date_index);
%     specific_mean_wspd = daily_mean_wspd(date_index);
% 
%     specific_max_rhum = daily_max_rhum(date_index);
%     specific_min_rhum = daily_min_rhum(date_index);
%     specific_mean_rhum = daily_mean_rhum(date_index);
% 
%     % Calculate standard deviations for the specific date
%     specific_std_temp = std(TEMP, 'omitnan');
%     specific_std_wspd = std(WSPD, 'omitnan');
%     specific_std_rhum = std(RHUM, 'omitnan');
% 
%     % Display the results
%     fprintf('Weather Data for %s:\n', specific_date_str);
%     fprintf('  Temperature: Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%         specific_max_temp, specific_min_temp, specific_mean_temp, specific_std_temp);
%     fprintf('  Wind Speed:  Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%         specific_max_wspd, specific_min_wspd, specific_mean_wspd, specific_std_wspd);
%     fprintf('  Humidity:    Max = %.2f, Min = %.2f, Mean = %.2f, Std Dev = %.2f\n', ...
%         specific_max_rhum, specific_min_rhum, specific_mean_rhum, specific_std_rhum);
% else
%     fprintf('Date %s not found in the data.\n', specific_date_str);
% end
