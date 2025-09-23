function [formatSpec, nvars, startRow, endRow] = read_SFC_html(filein)

% Open file for reading
fid = fopen(filein, 'r');
if fid == -1
    error('File could not be opened.');
end

% Step 1: Find the number of header rows (lines before data)
nheader = 0;
endlabel = [];
while true
    tline = fgetl(fid);  % Read a line from the file
    if ~ischar(tline)
        break;  % End of file
    end
    endlabel = strfind(tline, '=');  % Find line containing '='
    if length(endlabel) > 3
        break;  % Exit loop when line with '=' is found
    end
    nheader = nheader + 1;  % Count header lines
end

% Set the start row after headers
startRow = nheader + 2;

% Step 2: Determine the number of variables (columns) and their lengths
% We need to carefully handle the last column by considering any extra spaces
space_id = strfind(tline, ' ');  % Find spaces in the last header line
var_len = [space_id(1) - 1, diff(space_id)];  % Calculate variable widths
nvars = length(var_len);

% Ensure that the last column is included by considering the space after the last variable
if tline(end) ~= ' '  % Check if there's no space after the last column
    var_len = [var_len, length(tline) - sum(var_len)];  % Include the last column as the remainder
    nvars = nvars + 1;  % Increase column count
end

% Step 3: Build the formatSpec string dynamically
formatSpec = '';
for i = 1:nvars
    formatSpec = [formatSpec, '%', num2str(var_len(i)), 's'];  % Concatenate format string
end
formatSpec = [formatSpec, '%[^\n\r]'];  % Add the rest of the line format

% Step 4: Read through the file again to determine the last row of data
frewind(fid);  % Move the file pointer to the beginning
nheader = 0;  % Reset header count
while true
    tline = fgetl(fid);  % Read a line from the file
    if ~ischar(tline)
        break;  % End of file
    end
    nheader = nheader + 1;  % Count rows
end

% Set the end row before data
endRow = nheader - 1;

% Close the file
fclose(fid);

end
