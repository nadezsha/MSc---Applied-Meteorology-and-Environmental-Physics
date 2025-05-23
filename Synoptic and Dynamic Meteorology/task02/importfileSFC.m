function LGRX = importfile(filename, formatSpec, nvars, startRow, endRow)
%IMPORTFILE Import numeric data from a text file as a matrix.
%   LGRX = IMPORTFILE(FILENAME) Reads data from text file FILENAME for the
%   default selection.
%
%   LGRX = IMPORTFILE(FILENAME, STARTROW, ENDROW) Reads data from rows
%   STARTROW through ENDROW of text file FILENAME.
%
% Example:
%   LGRX = importfile('LGRX.webarchive', 12, 49);
%
%    See also TEXTSCAN.

% Auto-generated by MATLAB on 2018/11/05 20:33:29

%% Initialize variables.
if nargin<=2
    startRow = 12;
    endRow = 49;
end

%% Format for each line of text:
%   column1: text (%s)
%	column2: text (%s)
%   column3: text (%s)
%	column4: text (%s)
%   column5: text (%s)
%	column6: text (%s)
%   column7: text (%s)
%	column8: text (%s)
%   column9: text (%s)
%	column10: text (%s)
%   column11: text (%s)
% For more information, see the TEXTSCAN documentation.
%formatSpec = '%4s%8s%7s%4s%4s%4s%4s%4s%4s%5s%8s%s%[^\n\r]';

%% Open the text file.
fileID = fopen(filename,'r');

%% Read columns of data according to the format.
% This call is based on the structure of the file used to generate this
% code. If an error occurs for a different file, try regenerating the code
% from the Import Tool.
dataArray = textscan(fileID, formatSpec, endRow(1)-startRow(1)+1, 'Delimiter', '', 'WhiteSpace', '', 'TextType', 'string', 'HeaderLines', startRow(1)-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
for block=2:length(startRow)
    frewind(fileID);
    dataArrayBlock = textscan(fileID, formatSpec, endRow(block)-startRow(block)+1, 'Delimiter', '', 'WhiteSpace', '', 'TextType', 'string', 'HeaderLines', startRow(block)-1, 'ReturnOnError', false, 'EndOfLine', '\r\n');
    for col=1:length(dataArray)
        dataArray{col} = [dataArray{col};dataArrayBlock{col}];
    end
end

%% Remove white space around all cell columns.
for i=1:nvars
    dataArray{i} = strtrim(dataArray{i});
end

%% Close the text file.
fclose(fileID);

%% Post processing for unimportable data.
% No unimportable data rules were applied during the import, so no post
% processing code is included. To generate code which works for
% unimportable data, select unimportable cells in a file and regenerate the
% script.

%% Create output variable
LGRX = [dataArray{1:end-1}];
