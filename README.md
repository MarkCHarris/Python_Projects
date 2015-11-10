##Python_Projects

###Wear_Time.py

####OVERVIEW

This program is meant for use with the .csv output of the Actigraph GT3X accelerometer, which quantitatively records physical activity counts every 10 seconds. The data in the .csv file is sorted by user, and for each user, the data are arranged chronologically.

Before this data can be converted into metabolic equivalents, non-wear time must be identified and filtered out at the scientist's discretion. This Python code allows the scientist to identify sequences of consecutive 0 counts in a chosen variable. For example, if the subject removed the Actigraph from 11am-1pm, there would be a string of 720 consecutive 0's (one every 10 seconds for 2 hours). If the scientist defines "non-wear" as one hour of 0 activity, they will choose a threshold of 360 consecutive 0's, and this program will identify all such sequences. The program allows the scientist to choose whether each day is treated as a separate monitoring period or all days for a given user are treated as one continuous monitoring period.

The output of this program is a .csv file with one variable named "Wear" that codes "0" for non-wear and "1" for wear. If the scientist defines "non-wear" as a duration of 0 activity that exceeds the amount of data available for a specific monitoring period, then the program will print a warning message to the user and output a value of "2" for that monitoring period. The scientist can then combine the output file with the original to filter the data as desired.

####BRIEF ALGORITHM DESCRIPTION

The algorithm this program uses to process the data is based on 3 goals:

1. Achieve perfectly accurate results.
2. Only look at each incoming value once.
3. Take a minimal number of actions to assign the proper values to the "Wear" variable.

As each value of the variable chosen by the user is read from the input file, the program checks whether it is "0" or non-"0". The program records a "Wear" value of "1" for every value, but it also remembers how many "0"s it has seen since the last non-"0" value. If this number exceeds the threshold, then the "Wear" value is changed to "0" for all values after the last non-"0" value. The program now remembers that it is in non-wear time, and will automatically set "Wear" to "0" for all new values until a non-"0" value is seen. Once a non-"0" value is seen, the program returns to its original behavior.

The above only describes the core algorithm used.  The rest of the code serves to interact with the user to obtain required parameters or handle special cases such as monitoring period being too short for the chosen threshold.
