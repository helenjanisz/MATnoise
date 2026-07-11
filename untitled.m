function cleanLargeVars(thresholdBytes)
    vars = whos;
    
    for i = 1:length(vars)
        if vars(i).bytes > thresholdBytes
            eval(['clear ' vars(i).name])
        end
    end
end