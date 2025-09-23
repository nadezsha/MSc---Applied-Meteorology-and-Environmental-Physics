clear all;
close all;
clc;

station = 17220;
station_2 = 'LTBJ';  
YY = 2024;  
MM = 07;   
%dates = {'20240201', '20240202', '20240203', '20240204', '20240205', '20240206', '20240207', '20240208', '20240209', '20240210','20240211', '20240212', '20240213', '20240214','20240215', '20240216', '20240217', '20240218','20240219', '20240220', '20240221', '20240222','20240223', '20240224', '20240225', '20240226','20240227', '20240228', '20240229'};  
dates = {'20240701', '20240702', '20240703', '20240704', '20240705', '20240706', '20240707', '20240708', '20240709', '20240710','20240711', '20240712', '20240713', '20240714','20240715', '20240716', '20240717', '20240718','20240719', '20240720', '20240721', '20240722','20240723', '20240724', '20240725', '20240726','20240727', '20240728', '20240729', '20240730', '20240731'};  

gamma_d = 0.0098;  %adiabatic lapse rate (K/m)
gamma_dew = 0.0018; % dew point lapse rate(K/m)

num_days = eomday(YY, MM);


heights_rh100 = NaN(1, num_days);      % cloud base
precipitable_water = NaN(num_days, 1); 
inversion_thickness = NaN(num_days, 1);   
saturation_layer_thickness = NaN(num_days, 1);
zlcl = NaN(1, num_days);               % calculated LCL


lifted_index = NaN(1, num_days);
k_index = NaN(1, num_days);
total_totals_index = NaN(1, num_days);
sweat_index = NaN(1, num_days);

rain_categories = NaN(1, length(dates));

% Define rain condition categories for SFC data
no_rain = [];
light_rain_conditions = {'RA', 'DZ', '-RA', '+DZ', '-DZ', 'SHRA', '-SHRA'};
heavy_rain_conditions = {'+RA', '+TSRA', '+SHRA','TS','TSRA','-TSRA'};


for DD = 1:num_days
    HH = 0; % Ώρα
    fprintf('Data analysis for: %04d-%02d-%02d\n', YY, MM, DD);
    filename = ['RWS_' num2str(station) '_' datestr(datenum(YY, MM, DD), 12) '.htm'];

    try
        downloadUA('europe', station, YY, MM, DD, HH);
    catch
        warning('File for date %04d-%02d-%02d not found.', YY, MM, DD);
        continue;
    end

    try
        [startRow, endRow] = read_UA_html(filename);
        mat = importfile(filename, startRow, endRow);
    catch
        warning('Failed to read data for %04d-%02d-%02d.', YY, MM, DD);
        continue;
    end

     fileContent = fileread(filename);
    
    PRES = table2array(mat(:,1)); % (hPa)
    HGHT = table2array(mat(:,2)); % (m)
    TEMP = table2array(mat(:,3)); % (°C)
    DWPT = table2array(mat(:,4)); % (°C)
    RHUM = table2array(mat(:,5)); % (%)
    MIXR = table2array(mat(:,6)); % (g/kg)

    [z0, idx0] = min(HGHT); % z₀: lowest height
    if ~isempty(idx0)
        T_o = TEMP(idx0);       % temp on the lowest height
        RH_o = RHUM(idx0);      % RH on the lowest height
        T_do = DWPT(idx0);      % dew point temp on the lowest height
        zlcl(DD) = (T_o - T_do) / (gamma_d - gamma_dew);
    else
        zlcl(DD) = NaN; 
    end

     % Calculate indexes
    liftedString = "Lifted index:";
    idx1 = strfind(fileContent, liftedString);
    kString = "K index:";
    idx2 = strfind(fileContent, kString);
    totalsString = "Totals totals index:";
    idx3 = strfind(fileContent, totalsString);
    sweatString = "SWEAT index:";
    idx4 = strfind(fileContent, sweatString);

    % Lifted index
    if ~isempty(idx1)
        liftedStr = regexp(fileContent(idx1:end), ':\s*(-?[\d.]+)', 'tokens', 'once');
        if ~isempty(liftedStr)
            lifted_index(DD) = str2double(liftedStr{1});
        else
            lifted_index(DD) = NaN;
        end
    else
        lifted_index(DD) = NaN;
    end

    % K index
    if ~isempty(idx2)
        kStr = regexp(fileContent(idx2:end), ':\s*(-?[\d.]+)', 'tokens', 'once');
        if ~isempty(kStr)
            k_index(DD) = str2double(kStr{1});
        else
            k_index(DD) = NaN;
        end
    else
        k_index(DD) = NaN;
    end

    % Totals totals index
    if ~isempty(idx3)
        totalsStr = regexp(fileContent(idx3:end), ':\s*(-?[\d.]+)', 'tokens', 'once');
        if ~isempty(totalsStr)
            total_totals_index(DD) = str2double(totalsStr{1});
        else
            total_totals_index(DD) = NaN;
        end
    else
        total_totals_index(DD) = NaN;
    end

    % SWEAT index
    if ~isempty(idx4)
        sweatStr = regexp(fileContent(idx4:end), ':\s*(-?[\d.]+)', 'tokens', 'once');
        if ~isempty(sweatStr)
            sweat_index(DD) = str2double(sweatStr{1});
        else
            sweat_index(DD) = NaN;
        end
    else
        sweat_index(DD) = NaN;
    end

end

% Rainfall (SFC data)
for i = 1:length(dates)
    DATE = dates{i};   

    filename = ['SFC_' station_2 '_' DATE '.htm'];
    downloadSFC(station_2, DATE)

    [formatSpec, nvars, startRow, endRow] = read_SFC_html(filename);
    mat = importfileSFC(filename, formatSpec, nvars, startRow, endRow);

    % Rainfall categorisation
    if any(ismember(mat(:), heavy_rain_conditions))
        rain_categories(i) = 2; % Heavy rain
    elseif any(ismember(mat(:), light_rain_conditions))
        rain_categories(i) = 1; % Light rain
    else
        rain_categories(i) = 0; % No rain
        no_rain = [no_rain, datetime(DATE, 'InputFormat', 'yyyyMMdd')];
    end
end

dates_dt = datetime(dates, 'InputFormat', 'yyyyMMdd');


figure;

% K Index with Rainfall
subplot(2,2,1)
yyaxis left
bar(1:num_days, rain_categories, 'FaceColor', 'blue', 'EdgeColor', 'black');
ylabel('Rainfall');
set(gca, 'YTick', [0 1 2], 'YTickLabel', {'No Rain', 'Light Rain', 'Heavy Rain'});
ax = gca;  
ax.YColor = 'blue';  % change right y axis colour
yyaxis right
plot(1:num_days, k_index, '-o', 'LineWidth', 1.5, 'Color', [0, 0.5, 0]);
xlabel('Days of the Month');
ylabel('K Index');
title('K Index');
ax.YColor = [0, 0.5, 0]; 
ax.XColor = 'black';  
xticks(0:5:num_days);
grid on;


% Lifted Index with Rainfall
subplot(2,2,2)
yyaxis left
bar(1:num_days, rain_categories, 'FaceColor', 'blue', 'EdgeColor', 'black');
ylabel('Rainfall');
set(gca, 'YTick', [0 1 2], 'YTickLabel', {'No Rain', 'Light Rain', 'Heavy Rain'});
ax = gca;  
ax.YColor = 'blue';  
yyaxis right
plot(1:num_days, lifted_index, '-o', 'LineWidth', 1.5, 'Color', [0, 0.5, 0]);
xlabel('Days of the month');
ylabel('Lifted Index');
title('Lifted Index');
ax.YColor = [0, 0.5, 0]; 
ax.XColor = 'black';  
xticks(0:5:num_days);
grid on;


% Total Totals Index Index with Rainfall
subplot(2,2,3)
yyaxis left
bar(1:num_days, rain_categories, 'FaceColor', 'blue', 'EdgeColor', 'black');
ylabel('Rainfall');
set(gca, 'YTick', [0 1 2], 'YTickLabel', {'No Rain', 'Light Rain', 'Heavy Rain'});
ax = gca;  
ax.YColor = 'blue'; 
yyaxis right
plot(1:num_days, total_totals_index, '-o', 'LineWidth', 1.5, 'Color', [0, 0.5, 0]);
xlabel('Days of the month');
ylabel('Totals Totals Index');
title('Totals Totals Index');
ax.YColor = [0, 0.5, 0];  
ax.XColor = 'black';
xticks(0:5:num_days);
grid on;


% SWEAT Index with Rainfall
subplot(2,2,4)
yyaxis left
bar(1:num_days, rain_categories, 'FaceColor', 'blue', 'EdgeColor', 'black');
ylabel('Rainfall');
set(gca, 'YTick', [0 1 2], 'YTickLabel', {'No Rain', 'Light Rain', 'Heavy Rain'});
ax = gca; 
ax.YColor = 'blue';  
yyaxis right
plot(1:num_days, sweat_index, '-o', 'LineWidth', 1.5, 'Color', [0, 0.5, 0]);
xlabel('Days of the month');
ylabel('SWEAT Index');
title('SWEAT Index');
ax.YColor = [0, 0.5, 0]; 
ax.XColor = 'black';  
xticks(0:5:num_days);


sgtitle('Indexes and Rainfall', 'FontWeight', 'Bold');
