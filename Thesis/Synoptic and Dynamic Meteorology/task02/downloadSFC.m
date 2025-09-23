function downloadSFC(station,DATE)
% Save the SFC html files from UNIWYO for selected time and location

%years=[2012:2012]
%months=[1:12]
%station='LGTS'
%region='europe'
%DATE='20171104'

%%%%%%%%%%%%%%%%%%%%%

%for Y=years
 %   for M=months
        while 1
            %eom= num2str(eomday(Y, M));
            
            url=['http://weather.uwyo.edu/cgi-bin/wyowx.fcgi?TYPE=sflist&DATE=' DATE '&HOUR=00&UNITS=M&STATION=' station]
            filename=['SFC_' station '_' DATE '.htm'];
            urlwrite(url,filename);
            % Control of file dimension!
            DR=dir(filename);
            if DR.bytes>500
                disp('Ok...')
                break%Continue only if dimension exceed 550 bytes. In case not, restart the same request
            else
                disp('Server too busy! Try again in 100 s')
                pause(100)
            end
        end
%     pause
%    end
%end

