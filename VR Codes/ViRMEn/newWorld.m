function code = newWorld
% newWorld   Code for the ViRMEn experiment newWorld.
%   code = newWorld   Returns handles to the functions that ViRMEn
%   executes during engine initialization, runtime and termination.


% Begin header code - DO NOT EDIT
code.initialization = @initializationCodeFun;
code.runtime = @runtimeCodeFun;
code.termination = @terminationCodeFun;
% End header code - DO NOT EDIT


% --- INITIALIZATION code: executes before the ViRMEn engine starts.
function vr = initializationCodeFun(vr)
    vr.currentWorld = eval(vr.exper.variables.startWorld);
    vr.worldRadius = eval(vr.exper.variables.arenaRadius);
    vr.debug = eval(vr.exper.variables.debug);
    vr.simulated = eval(vr.exper.variables.simulated);

    % Get computer name (or simulate the PC)
    if vr.simulated
        vr.myComputerName = eval(vr.exper.variables.simulatedPC);
    else
        vr.myComputerName = getenv("COMPUTERNAME");
    end


    % Obis Laser
    if vr.currentWorld == 1
        vr.laser = ObisLaserController();
        if vr.laser.isReady()
            vr.has_usb_laser = true;
            vr.laser.serialOpen();
            vr.laser.setPowerMW(0);
            vr.laser.turnOn();
        else
            vr.has_usb_laser = false;
        end
    end
    vr.laser_process = false;   % Whether the laser is currently being processed
    vr.laser_powered = false;   % Whether the laser is powered
    vr.laser_tic = tic;         % Timer for the laser

    % Wait about 8 seconds for the laser to turn on
    pause(8);

    % Prompt for the experiment number and duration
    if vr.simulated
        %vr.debug = true;
        while true
            % Prompt for the mouse `.mov.csv` file for the raw mouse locomotion data to be fed into the simulation
            csvFile = input('Enter the full path to a `.mov.csv` file: ', 's');
            if isempty(csvFile)
                disp('User canceled file selection');
                vr.experimentEnded = true;
                return;
            end
            try
                if startsWith(csvFile, '"')
                    csvFile = extractAfter(csvFile, 1);
                end
                if endsWith(csvFile, '"')
                    csvFile = extractBefore(csvFile, strlength(csvFile));
                end

                % Read the CSV file
                csvData = readtable(csvFile);
                if any(any(ismissing(csvData)))
                    error('The CSV file contains missing data');
                end
                % Convert the table to a matrix
                vr.simData = table2array(csvData);
                vr.simDataSize = size(vr.simData);
                break; % Exit the loop if everything is fine
            catch ME
                disp(['Error: ', ME.message]);
                disp('Please try again.');
            end
        end
        answer = [promptNumber('Experiment', {'Mouse number'}, {''}), 0]; 
    else
        % Linear Track uses the laser. Request a valid laser power and duration from user.
        if vr.currentWorld == 1
            answer = promptNumber('Experiment', {'Mouse number', 'Experiment duration (sec)', 'Laser duration (sec)', 'Laser Power %'}, {'', '300', '5', '5'});
            while answer(4) < 0 || answer(4) > 110 || answer(3) < 0
                disp('Laser power must be between 0 and 110');
                disp('Laser duration must be greater than 0');
                answer = promptNumber('Experiment', {'Mouse number', 'Experiment duration (sec)', 'Laser duration (sec)', 'Laser Power %'}, {answer(1), answer(2), answer(3), answer(4)});
                if isempty(answer) || any(isnan(answer))
                    break;
                end
            end
        else
            answer = promptNumber('Experiment', {'Mouse number', 'Experiment duration (sec)'}, {'', '300'});
        end
    end

    if isempty(answer) || any(isnan(answer))
        vr.experimentEnded = true;
        return;
    end

    vr.mouseNo = answer(1);
    disp('Mouse No: ' + string(vr.mouseNo));

    vr.experimentDuration = answer(2);
    disp('Experiment duration: ' + string(vr.experimentDuration));

    if vr.currentWorld == 1
        if ~vr.simulated
            vr.laserDuration = answer(3);
            vr.laserPower = answer(4);
        else
            vr.laserDuration = 0;
            vr.laserPower = 0;
        end
        disp('Laser duration: ' + string(vr.laserDuration));
        disp('Laser power: ' + string(vr.laserPower));
    end

    vr.targetsReversed = eval(vr.exper.variables.swapped);

    rStr = "";
    if vr.targetsReversed
        rStr = "Swapped";
    end

    % Computer specific Movement zeroes and y-axis polarity
    
    if vr.myComputerName == "LRI-110045"
        vr.zero_offset = [2.59, 2.6, 2.62];
        vr.ypol = -1;
    elseif vr.myComputerName == "LRI-110117"
        vr.zero_offset = [2.49, 2.49, 2.49];
        vr.ypol = -1;
    else
        vr.zero_offset = [2.5, 2.5, 2.5];
        vr.ypol = 1;
    end


    if ~vr.debug
        % <Init DAQ>
        daqreset;   % reset DAQ in case it's still in use by a previous Matlab program

        % Add input channels
        vr.daq_ai_airball = daq("ni");    % create a new session
        vr.daq_ai_airball.Rate = 60;      % set the sample rate
        addinput(vr.daq_ai_airball,"Dev1","ai0","Voltage");
        addinput(vr.daq_ai_airball,"Dev1","ai1","Voltage");
        addinput(vr.daq_ai_airball,"Dev1","ai2","Voltage");

        % Add output channels
        vr.daq_ao_reward = daq("ni");
        vr.daq_do_cameras = daq("ni");
        vr.daq_do_laser = daq("ni");
        vr.daq_do_lasertrig = daq("ni");
        vr.daq_ao_reward.Rate = 60;
        vr.daq_do_cameras.Rate = 60;
        vr.daq_do_laser.Rate = 60;
        vr.daq_do_lasertrig.Rate = 60;
        addoutput(vr.daq_ao_reward,"Dev1","ao0","Voltage");
        addoutput(vr.daq_do_cameras,"Dev1","Port0/Line1","Digital");
        addoutput(vr.daq_do_laser,"Dev1","Port0/Line4","Digital");
        addoutput(vr.daq_do_lasertrig,"Dev1","Port0/Line3","Digital");


        start(vr.daq_ai_airball)
        start(vr.daq_ao_reward, "continuous");
        write(vr.daq_ao_reward, repmat(2.6, 40, 1));   % set the output channels to 2.6v
        write(vr.daq_do_cameras, false);               % keep cameras off for now
        write(vr.daq_do_lasertrig, false);             % keep laser off for now
        write(vr.daq_do_laser,   true);                % Indicate that the laser will be in trigger mode
        % </Init DAQ>

    end

    % Get the Datetime for the start of the experiment
    startDate = datetime('now', 'Format','y-MM-dd HH-mm-ss');
    % Extract individual components (year, month, day, hour, minute, second)
    yr = year(startDate);
    mo = month(startDate);
    da = day(startDate);
    ho = hour(startDate);
    mi = minute(startDate);
    se = floor(second(startDate));

    % Format the components into a string
    vr.startDate = sprintf('%04d-%02d-%02d %02d-%02d-%02d', yr, mo, da, ho, mi, se);

    %{
        vr.targetPositions
        shape: nx4
        [w, u, u, R] The first row is the world number and the world radius
        [t, x, y, r] The next rows are the target positions
        w -> w is the world number
        u -> u is currently unused
        R -> R is the world radius
        t -> t is the time the target spawned
        x -> x is the position in the x axis
        y -> y is the position in the y axis
        r -> r is the radius of the cylinder
    %}
    vr.targetAPosition = [(eval(vr.exper.variables.familiarX) * (~vr.targetsReversed)) + (-1 * eval(vr.exper.variables.familiarX) * vr.targetsReversed), eval(vr.exper.variables.familiarY)];
    vr.targetBPosition = [(eval(vr.exper.variables.novelX) * (~vr.targetsReversed)) + (-1 * eval(vr.exper.variables.novelX) * vr.targetsReversed), eval(vr.exper.variables.novelY)];

    % Use both targets in Worlds 1 and 2
    cylinderRadius = eval(vr.exper.variables.cylinderRadius);
    if vr.currentWorld == 1
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; "linearTrack" "virmen" 0 vr.worldRadius; "spawned" "x" "y" "radius"];
    elseif vr.currentWorld == 2
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; strcat("oneObject", rStr)            "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius];
    elseif vr.currentWorld == 3
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; "twoObjectSame"                      "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius; 0 vr.targetBPosition cylinderRadius];
    elseif vr.currentWorld == 4
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; strcat("twoObjectHorizontal", rStr)  "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius; 0 vr.targetBPosition cylinderRadius];
    elseif vr.currentWorld == 5
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; strcat("twoObjectDots", rStr)        "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius; 0 vr.targetBPosition cylinderRadius];
    elseif vr.currentWorld == 6
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; strcat("twoObjectSquares", rStr)     "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius; 0 vr.targetBPosition cylinderRadius];
    elseif vr.currentWorld == 7
        vr.targetPositions = ["world" "environment" "datetime" "radius" ; strcat("twoObjectTriangles", rStr)   "virmen"  vr.startDate  vr.worldRadius; "spawned" "x" "y" "radius"; 0 vr.targetAPosition cylinderRadius; 0 vr.targetBPosition cylinderRadius];
    end

    %{
        vr.saveMovement
        shape: nx4
        [e, r, l, f]
        e -> elapsed is the time since the first sample
        r -> orbital is the voltage from A0 with a value between 0 and 5.2
        l -> lateral is the voltage from A1 with a value between 0 and 5.2
        f -> forward is the voltage from A2 with a value between 0 and 5.2
    %} 
    vr.saveMovement = [];
    %{
        vr.savePositon
        shape: nx5
        [e, x, y, d, l]
        e -> elapsed is the time since the first sample
        x -> x is the position in the x axis
        y -> y is the position in the y axis
        d -> direction is the direction in radians (0 to 2pi)
        l -> state of the laser (0 or 1)
    %} 
    vr.savePositon = [];
    vr.yOffset = 0;

    % Preallocate saveMovement and savePositon
    vr.saveIndex = 1; % Index for writing into preallocated arrays
    local_numSamples = 0;
    
    if vr.simulated
        if isfield(vr, 'simDataSize') && ~isempty(vr.simDataSize) && vr.simDataSize(1) > 0
            local_numSamples = vr.simDataSize(1);
        else
            disp('Warning: simDataSize not available or zero for preallocation in simulated mode. Movement/Position data will not be preallocated.');
        end
    else % Non-simulated
        expectedRate = 60; % Default expected rate
        if ~vr.debug && isfield(vr, 'daq_ai_airball') && ~isempty(vr.daq_ai_airball) && isa(vr.daq_ai_airball, 'daq.ni.Session') && vr.daq_ai_airball.Rate > 0
            expectedRate = vr.daq_ai_airball.Rate;
        end
        if isfield(vr, 'experimentDuration') && vr.experimentDuration > 0
            local_numSamples = ceil(vr.experimentDuration * expectedRate) + 200; % Add a small buffer (e.g. ~3s at 60Hz)
        else
            disp('Warning: experimentDuration is not positive or not set. Movement/Position data will not be preallocated effectively.');
            % Fallback to a smaller, potentially dynamic array or a fixed small buffer if necessary
            local_numSamples = 1000; % Or a small default like 1000 if you expect some data regardless
        end
    end

    if local_numSamples > 0
        vr.saveMovement = zeros(local_numSamples, 4); % t, data1, data2, data3
        vr.savePositon = zeros(local_numSamples, 5);  % t, x, y, d, laser
        disp(['Preallocated space for ', num2str(local_numSamples), ' samples.']);
    else
        % If numSamples is 0, initialize as empty; performance will be impacted.
        vr.saveMovement = [];
        vr.savePositon = [];
        if vr.simulated || (isfield(vr, 'experimentDuration') && vr.experimentDuration > 0)
             disp('Warning: Preallocation failed or resulted in zero samples. saveMovement and savePositon initialized as empty.');
        end
    end

    % DAQ variables
    vr.daq_delay = tic;
    vr.daq_start = false;
    vr.daq_collect = false;
    vr.daq_startTime = NaN;
    vr.recentData = [0, 0, 0];
    vr.simData_i = 1;

    % Process reward variables
    vr.reward_process = false;
    vr.reward_processing = false;
    vr.reward_tic = tic;

    % Markers for what level the mouse is on
    % and what maximum level the mouse has reached
    vr.level = 1;
    vr.maxLevel = 1;

% --- RUNTIME code: executes on every iteration of the ViRMEn engine.
function vr = runtimeCodeFun(vr)
    
    % <Start DAQ>
    if ~vr.daq_start
        vr.daq_start = true;
        if vr.currentWorld == 1
            vr.position(1) = 0;
            vr.position(2) = -25;
            vr.position(3) = 0;
            vr.most_forward = -25;
            vr.unused = vr.dp(:);
            vr.level_end = false;
            vr.level_mid = false;
        else
            vr.position(1) = eval(vr.exper.variables.startX);
            vr.position(2) = eval(vr.exper.variables.startY);
            vr.position(3) = eval(vr.exper.variables.startZ);
            vr.unused = vr.dp(:);
        end
    end
    % </Start DAQ>

    
    % <Linear Track Logic>
    if vr.currentWorld == 1
        % Prevent the mouse from turning around (limit facing direction to -pi/3 to pi/3)
        if vr.position(4) > pi/3
            vr.position(4) = pi/3;
            vr.unused = vr.dp(:);
        elseif vr.position(4) < -pi/3
            vr.position(4) = -pi/3;
            vr.unused = vr.dp(:);
        end

        % Prevent mouse from going backwards
        if vr.position(2) < vr.most_forward
            vr.position(2) = vr.most_forward;
            vr.unused = vr.dp(:);
        end

        % Check if the mouse has reached the end of the loop
        if vr.position(2) > 50
            % The mouse reached the loop end
            vr.yOffset = vr.yOffset + 100;
            vr.position(2) = -50;
            vr.unused = vr.dp(:);
            vr.level_end = false;
            vr.level_mid = false;
        elseif ~vr.level_end && vr.position(2) > 43
            vr.level = vr.level + 1;
            vr.level_end = true;
        elseif ~vr.level_mid && vr.position(2) > -7
            % The mouse passed the center checkpoint
            % move the mouse just forward of the center
            vr.level = vr.level + 1;
            vr.level_mid = true;
        end
        % If the mouse has reached a new level
        if vr.level > vr.maxLevel
            vr.maxLevel = vr.level;
            % Enable the laser flag
            vr.laser_process = true;
            vr.laser_tic = tic;
        end

        % <Each Laser>
        if vr.laser_process
            % Check if the laser is still being processed (2 seconds)
            if toc(vr.laser_tic) < vr.laserDuration
                % If it just started processing, then turn on the laser
                if ~vr.laser_powered
                    vr.laser_powered = true;
                    if vr.has_usb_laser
                        vr.laser.setPowerMW(vr.laserPower);
                    end
                    write(vr.daq_do_lasertrig, true);
                end
            else
                % If the laser has been processed, then turn off the laser
                vr.laser_powered = false;
                vr.laser_process = false;
                if vr.has_usb_laser
                    vr.laser.setPowerMW(0);
                end
                write(vr.daq_do_lasertrig, false);
            end
        end
        % </Each Laser>
    end
    % </Linear Track Logic>

    % <Each DAQ>
    t = 0;

    % daq_start is a flag to start the DAQ. It is triggered below after the first cylinder is hit
    if vr.daq_start
        % daq_startTime is initialized as NaN above
        if isnan(vr.daq_startTime)
            vr.saveMovement = [];
            vr.savePositon = [];
            vr.daq_startTime = tic;                              % Initialize daq_startTime with a tic after the first cylinder is hit
            if ~vr.debug
                write(vr.daq_do_cameras, true);                  % Send a signal to the digital output to start the cameras
                write(vr.daq_ao_reward, repmat(3.142, 40, 1));   % set the output channels to 3.142v
            end
        end
        t = toc(vr.daq_startTime);
    end

     
    if ~vr.simulated && t > vr.experimentDuration
        vr.experimentEnded = true;
    else
        if vr.simulated
            % Read from the simulated data
            nextData = vr.simData(vr.simData_i, :);
            % Get last 3 values
            vr.recentData = nextData(vr.simDataSize(2) - 2:vr.simDataSize(2));
            vr.simData_i = vr.simData_i + 1;
            % if the index is at the end, then end the experiment
            if vr.simData_i > vr.simDataSize(1)
                vr.experimentEnded = true;
            end
        else
            % Read from the DAQ
            if ~vr.debug
                readData = read(vr.daq_ai_airball, 1, "OutputFormat", "Matrix");
                if readData
                    vr.recentData = readData;
                end
            end
        end
        % Populate the saveMovement matrix
        if vr.saveIndex <= size(vr.saveMovement, 1)
            vr.saveMovement(vr.saveIndex, :) = [t, vr.recentData];
        else
            % Fallback for unexpected extra data, though this indicates an issue with preallocation size
            vr.saveMovement = [vr.saveMovement; t, vr.recentData]; 
        end

        % Populate the savePositon matrix
        direction = rem(vr.position(4), 2 * pi);
        if direction < 0
            direction = direction + (2 * pi);
        end
        if vr.saveIndex <= size(vr.savePositon, 1)
            vr.savePositon(vr.saveIndex, :) = [t, vr.position(1), vr.position(2) + vr.yOffset, direction, vr.laser_powered];
        else
            % Fallback for unexpected extra data
            vr.savePositon = [vr.savePositon; t, vr.position(1), vr.position(2) + vr.yOffset, direction, vr.laser_powered];
        end
        vr.saveIndex = vr.saveIndex + 1;

        if vr.reward_process
            % Check if the reward is still being processed (2 seconds)
            if toc(vr.reward_tic) < 2
                % If it just started processing, then turn on the reward
                if ~vr.reward_processing
                    vr.reward_processing = true;
                    if ~vr.debug
                        write(vr.daq_ao_reward, 2.5);
                    end
                end
            else
                % If the reward has been processed, then turn off the reward
                vr.reward_processing = false;
                vr.reward_process = false;
                if ~vr.debug
                    write(vr.daq_ao_reward, 3.142);
                end
            end
        end
    end
    % </Each DAQ>

% --- TERMINATION code: executes after the ViRMEn engine stops.
function vr = terminationCodeFun(vr)
    if ~vr.debug
        % <Stop DAQ>
        if isfield(vr, "daq_do_cameras")
            write(vr.daq_ao_reward, repmat(0.998, 40, 1));
            write(vr.daq_do_cameras, false);
            write(vr.daq_do_laser, false);
            write(vr.daq_do_lasertrig, false);
            stop(vr.daq_ai_airball);
            stop(vr.daq_ao_reward);
        end
        % </Stop DAQ>
    end
    
    % <Write Data>
    if isfield(vr, "daq_startTime") && ~isnan(vr.daq_startTime)
        fileString = "Mouse " + vr.mouseNo + " " + string(vr.startDate);
        vr.saveMovement = ["elapsed" "orbital" "lateral" "forward"; vr.saveMovement];
        vr.savePositon = ["elapsed" "x" "y" "d" "laser"; vr.savePositon];
        writematrix(vr.saveMovement, fileString + ".mov.csv", "WriteMode", "overwrite");
        writematrix(vr.savePositon, fileString + ".pos.csv", "WriteMode", "overwrite");
        writematrix(vr.targetPositions, fileString + ".tgt.csv", "WriteMode", "overwrite");
    end
    % </Write Data>

    if isfield(vr, "window")
        vr.window.Dispose;
    end

    % <Stop Laser>
    if vr.currentWorld == 1
        if vr.has_usb_laser
            vr.laser.setPowerMW(0);
            vr.laser.turnOff();
            vr.laser.serialClose();
            delete(vr.laser);
        end
    end
    % </Stop Laser>
