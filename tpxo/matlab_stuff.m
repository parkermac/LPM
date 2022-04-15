%% tide-specific code

% define needed files
t_dir = ['/Users/pm8/Documents/LiveOcean_data/tide','/TPXO/'];


date_string = '2019.07.04';
%% parse the time in date_string for the nodal corrections
yrs = date_string(1:4);
mos = date_string(6:7);
dys = date_string(9:10);
yr = str2double(yrs);
mo = str2double(mos);
dy = str2double(dys);
tref_datenum = datenum(yr,mo,dy);

% get sizes and initialize the NetCDF file
% specify the constituents to use
c_data =  ['m2  ';'s2  ';'k1  ';'o1  '; 'n2  ';'p1  ';'k2  ';'q1  '];

if 0
    np = size(c_data,1);
else
    % limit number of constituents (first = M2)
    np = 1;
end

% get set up to find constituent and nodal correction info
path(path,[t_dir,'/tmd_toolbox']);
% specify the tidal model to use
mod_name = 'tpxo7.2';
model = [t_dir,'/DATA7p2/Model_',mod_name];
for ii = 1:np
    cons = c_data(ii,:);
    cons_nb = deblank(cons);
    [junk,junk,ph,om,junk,junk] = constit(cons);
    disp(['Working on ',cons_nb,' period = ', num2str(2*pi/(3600*om)),' hours']);
    % get nodal corrections centered on the middle
    % of the run time period, relative to day 48622 mjd (1/1/1992)
    trel = tref_datenum - datenum(1992,1,1);
    disp(['trel = ',num2str(trel)])
    [pu,pf] = nodal(trel + 48622, cons);
    
    disp([' ph = ',num2str(ph)])
    disp([' pu = ',num2str(pu)])
    disp([' pf = ',num2str(pf)])
    % tide_period(ii) = 2*pi/(3600*om); % hours
    % tide_Eamp(ii,:,:) = pf*Eamp; % m
    % tide_Ephase(ii,:,:) = Ephase - 180*ph/pi - 180*pu/pi;% + phase_shift; % deg
    
end
