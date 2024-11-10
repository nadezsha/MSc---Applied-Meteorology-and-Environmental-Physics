function [formatSpec,nvars, startRow,endRow]=read_SFC_html(filein)


%first step to find the number of empty rows at the beginning of data block (considered header lines):
fid=fopen(filein);
nheader=0;
endlabel=[];
while 1
    tline = fgetl(fid);
    endlabel=strfind(tline,'=');%Find first line containing '=' to find the number of header lines
    if length(endlabel)>3,break, end
    nheader=nheader+1;
end
fclose(fid);
startRow=nheader+2;

space_id=strfind(tline, ' ');
var_len=[space_id(1)-1 diff(space_id)];
nvars=length(var_len);
%formatSpec = '%4s%8s%7s%4s%4s%4s%4s%4s%4s%5s%8s%s%[^\n\r]';
formatSpec='';
for i=1:nvars
    formatSpec=strcat(formatSpec,'%',num2str(var_len(i)),'s');
end
formatSpec=strcat(formatSpec,'%[^\n\r]');

fid=fopen(filein);
nheader=0;
endlabel=[];
while 1
    tline = fgetl(fid);
    if ~ischar(tline),   break,   end
    nheader=nheader+1;
end
fclose(fid);
endRow=nheader-1;

