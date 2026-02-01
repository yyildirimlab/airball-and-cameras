function velocity = move2MiceMiguel(vr)
    % See saveMovement defined in the experiment code
    if isfield(vr, 'saveMovement') && ~isempty(vr.saveMovement)

        [last_row, ~] = size(vr.saveMovement);

        % Get the last row of the movement data
        mov_data = vr.saveMovement(last_row:last_row,2:4);
        
        % Offset the data to center it around 0 from the original (5.2/2)V resting position
        mov_data = (mov_data - vr.zero_offset);
        
        % Apply a threshold to each input
        thresh = 0.2;
        for i = 1:3
            if (norm(mov_data(i)) < thresh)
                mov_data(i) = 0;
            end
        end

        % Apply ypol
        mov_data = mov_data * vr.ypol;

        % Input scaling
        mov_data = mov_data * 10;

        % velocity is (d/dt)[x y z theta]
        x = mov_data(3) * sin(-vr.position(4)) + mov_data(2) * cos(-vr.position(4));
        y = mov_data(3) * cos(-vr.position(4)) - mov_data(2) * sin(-vr.position(4));
        z = 0;
        theta = mov_data(1)/(-4 * pi);
        velocity = [x y z theta];

    else
        velocity = [0 0 0 0];
    end