### OVERVIEW ###

# This program is meant for use with the .csv output of the Actigraph GT3X
# accelerometer, which quantitatively records physical activity counts every
# 10 seconds. The data in the .csv file is sorted by user, and for each user,
# the data are arranged chronologically.

# Before this data can be converted into metabolic equivalents, non-wear time
# must be identified and filtered out at the scientist's discretion. This
# Python code allows the scientist to identify sequences of consecutive 0
# counts in a chosen variable. For example, if the subject removed the
# Actigraph from 11am-1pm, there would be a string of 720 consecutive 0's
# (one every 10 seconds for 2 hours). If the scientist defines "non-wear"
# as one hour of 0 activity, they will choose a threshold of 360 consecutive
# 0's, and this program will identify all such sequences. The program allows
# the scientist to choose whether each day is treated as a separate monitoring
# period or all days for a given user are treated as one continuous monitoring period.

# The output of this program is a .csv file with one variable named "Wear" that
# codes "0" for non-wear and "1" for wear. If the scientist defines "non-wear"
# as a duration of 0 activity that exceeds the amount of data available for a
# specific monitoring period, then the program will print a warning message
# to the user and output a value of "2" for that monitoring period. The
# scientist can then combine the output file with the original to filter the
# data as desired.

### BRIEF ALGORITHM DESCRIPTION ###

# The algorithm this program uses to process the data is based on 3 goals:

# 1. Achieve perfectly accurate results.
# 2. Only look at each incoming value once.
# 3. Take a minimal number of actions to assign the proper values to the "Wear" variable.

# As each value of the variable chosen by the user is read from the input file,
# the program checks whether it is "0" or non-"0". The program records a
# "Wear" value of "1" for every value, but it also remembers how many "0"s
# it has seen since the last non-"0" value. If this number exceeds the
# threshold, then the "Wear" value is changed to "0" for all values after the
# last non-"0" value. The program now remembers that it is in non-wear time,
# and will automatically set "Wear" to "0" for all new values until a non-"0"
# value is seen. Once a non-"0" value is seen, the program returns to its
# original behavior.

# The above only describes the core algorithm used.  The rest of the code
# serves to interact with the user to obtain required parameters or handle
# special cases such as monitoring period being too short for the chosen
# threshold.

import string
import time

# Prompts the user for the file name.
def get_filename():
	
	while True:
		try:
			filename = raw_input('Enter file name, including extension.\n')
			infile=open(filename, 'r')
			break
		except IOError:
			print "Invalid file name."
			
	return infile;

# Prompts the user for the window width.
def get_threshold():

	while True:
		try:
			while True:
				y = int(raw_input("Enter number of consecutive zeros to scan for.\n"))
				if y > 0:
					threshold = y
					break
				else:
					print "Please enter an integer greater than zero."
			break
		except ValueError:
			print "Please enter an integer greater than zero."
			
	return threshold;

# Prompts the user to decide whether to treat each day as separate.
def get_is_separate():
	
	answer = False
	is_separate = True
	
	while not answer:
		
		merge_string = raw_input('Do you want to treat each day as separate? (Y/N)\n')
		
		if merge_string == 'y' or merge_string == 'Y':
			is_separate = True
			answer = True
		elif merge_string == 'n' or merge_string == 'N':
			is_separate = False
			answer = True
		else:
			print "I'm sorry, I don't understand.\n"
			
	return is_separate;

# Read the first row of the file to get the column names.
def get_colnames(infile):

	row = infile.readline()
	rowlist = row.split(',')
	colnames = [string.strip(x) for x in rowlist]
	
	return colnames;

# Print the column names.
def print_colnames(colnames):
	
	for i in range(len(colnames)):
		j = str(i+1)
		print j+'.', colnames[i]

# Query the user to identify a specific column.
def find_col(colnames, prompt):
	
	while True:
		try:
			while True:
				x = int(raw_input(prompt))
				y = x-1
				if y in range(len(colnames)):
					column = y
					break
				else:
					print "Please enter one of the above numbers."
			break
		except ValueError:
			print "Please enter one of the above numbers."

	return column;

# Warns the user if there are fewer data points in a time period than the selected threshold.
def data_less_than_threshold_warning(date_start, subject_start):
	
	message_part_1 = 'Threshold exceeds number of data points on day '
	message_part_2 = ' for subject ID '
	message = message_part_1 + date_start + message_part_2 + subject_start
	print message

def main():
	
	outfile=open('Output.csv','w')
	print>>outfile, 'Wear'
	
	# The code below gets needed input from the user.
	infile = get_filename()
	threshold = get_threshold()
	is_separate = get_is_separate()
	colnames = get_colnames(infile)
	print_colnames(colnames)
	
	variable_prompt = 'Which of the above variables do you wish to scan for consecutive zeros?  Please enter a number:\n'
	variable_col = find_col(colnames, variable_prompt)
	
	subject_prompt = 'Which of the above variables indicates the subject ID?  Please enter a number:\n'
	subject_col = find_col(colnames, subject_prompt)
	
	date_prompt = 'Which of the above variables indicates the date?  Please enter a number:\n'
	date_col = find_col(colnames, date_prompt)
	
	# Store current time immediately after all input is received from the user.
	start = time.time()
		
	# Initializing variables.
	subject_start = '0' # Remembers the current subject.
	date_start = '0' # Remembers the current date.
	end_subject = True # Indicates whether a new subject has been reached.
	end_date = True # Indicates whether a new day has been reached, if treating each day as separate.
	end_file = False # Indicates whether the end of the file has been reached.
	outlist = [] # Stores Wear values as they are determined.
	current_index = 0 # Remembers how far the program has progressed through
	                  # the current subject or date.
	is_nonwear = False # Indicates whether we are known to be in a period of non wear time.
	last_nonzero = -1 # Indicates where the last nonzero value of the tracked variable was.
	row_count = 0 # Tracks how many rows of data have been processed.
	
	# Read the first row of data.
	row = infile.readline()
	if row == '':
		end_file = True
	rowlist = row.split(',')

	# Loop over the entire file.
	while not end_file:
		
		row_count = row_count+1
		
		# If we are starting a new subject or a new day.
		if end_subject or end_date:
		
			# Reinitialize the below variables for a new day.
			current_index = 0
			end_subject = False
			end_date = False
			subject_start = rowlist[subject_col]
			date_start = rowlist[date_col]
			is_nonwear = False
						
			if is_separate:
				print subject_start, date_start
			else:
				print subject_start
			
			if rowlist[variable_col] == '0':
				last_nonzero = -1
			else:
				last_nonzero = 0
			
			if threshold == 1 and rowlist[variable_col] == '0':
				outlist.append('0')
			else:
				outlist.append('1')
			
		# If we are continuing the current subject and current day.
		else:
			
			current_index = current_index+1
			
			if rowlist[variable_col] == '0':
				if is_nonwear:
					outlist.append('0')
				else:
					if current_index - last_nonzero >= threshold:
						for i in range(last_nonzero+1, current_index):
							outlist[i] = '0'
						outlist.append('0')
						is_nonwear = True
					else:
						outlist.append('1')
			else:
				outlist.append('1')
				is_nonwear = False
				last_nonzero = current_index

		# Read the next line and check whether it is a new subject, new day, or end of file.
		# If it is, and there were fewer data points for the previous day or subject
		# than the threshold, warn the user and output '2' for that range
		# (instead of '0' or '1'.
		row = infile.readline()
		if row == '':
			end_file = True
			if current_index < threshold-1:
				data_less_than_threshold_warning(date_start, subject_start)
				outlist = ['2']*(current_index+1)
		else:
			rowlist = row.split(',')
			if rowlist[subject_col] != subject_start:
				end_subject = True
				if current_index < threshold-1:
					data_less_than_threshold_warning(date_start, subject_start)
					outlist = ['2']*(current_index+1)
			if is_separate and rowlist[date_col] != date_start:
				end_date = True
				if current_index < threshold-1:
					data_less_than_threshold_warning(date_start, subject_start)
					outlist = ['2']*(current_index+1)
					
		# If we have finished the day, subject, or file, send the data in outlist
		# to the output file and set outlist to empty.
		if end_file or end_subject or end_date:
			for i in outlist:
				print>>outfile, i
			outlist=[]

	# Close the input and output files.
	outfile.close()
	infile.close()
	
	# Tell the user how long it took to process the data.
	print "Number of Wear Time data points calculated:", row_count
	print "Seconds elapsed:", time.time() - start

if __name__ == '__main__':
	main()