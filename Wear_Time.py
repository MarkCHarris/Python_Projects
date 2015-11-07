import string
from collections import deque

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
def get_separate():
	
	answer = False
	separate = True
	
	while not answer:
		
		merge_string = raw_input('Do you want to treat each day as separate? (Y/N)\n')
		
		if merge_string == 'y' or merge_string == 'Y':
			separate = True
			answer = True
		elif merge_string == 'n' or merge_string == 'N':
			separate = False
			answer = True
		else:
			print "I'm sorry, I don't understand.\n"
			
	return separate;

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

# Function to read in the first window of a day.
def first_window(window, rowlist, infile, threshold, variable_col, subject_start, date_start, separate, date_col, subject_col):

	message_part_1 = 'Threshold exceeds number of data points on day '
	message_part_2 = ' for subject ID '
	message = message_part_1 + date_start + message_part_2 + subject_start

	window.clear()
	rowlist[variable_col] = string.strip(rowlist[variable_col])
	window.append(rowlist[variable_col])

	for i in range(0, threshold-1):
		prev_line = infile.tell()
		row = infile.readline()
		if row == '':
			print message
			infile.seek(prev_line)
			break
		else:
			rowlist = row.split(',')
			if separate and rowlist[date_col] != date_start:
				print message
				infile.seek(prev_line)
				break
			elif rowlist[subject_col] != subject_start:
				print message
				infile.seek(prev_line)
				break
			else:
				rowlist[variable_col] = string.strip(rowlist[variable_col])
				window.append(rowlist[variable_col])
				
	return window;

# Function to slide the window over one spot.
def slide_window(window, rowlist, variable_col):
	
	rowlist[variable_col] = string.strip(rowlist[variable_col])
	window.append(rowlist[variable_col])
	window.popleft()
	
	return window;

# Function to determine whether all variable values in a window are '0'
def all_zeros(window, threshold):
	
	numzeros = window.count('0')

	if numzeros == threshold:
		zeros = True
	else:
		zeros = False

	return zeros;

def main():
	
	outfile=open('Output.csv','w')
	print>>outfile, 'Wear'
	
	infile = get_filename()
	threshold = get_threshold()
	separate = get_separate()
	colnames = get_colnames(infile)
	print_colnames(colnames)
	
	variable_prompt = 'Which of the above variables do you wish to scan for consecutive zeros?  Please enter a number:\n'
	variable_col = find_col(colnames, variable_prompt)
	
	subject_prompt = 'Which of the above variables indicates the subject ID?  Please enter a number:\n'
	subject_col = find_col(colnames, subject_prompt)
	
	date_prompt = 'Which of the above variables indicates the date?  Please enter a number:\n'
	date_col = find_col(colnames, date_prompt)
	
	# Initializing variables.
	window = deque() # Contains a number of variable values equal to threshold.
	zeros = False # Indicates whether the current window is all zeros.
	slide_counter = 0 # Remembers how many times the window has slid on a given day.
	subject_start = '0' # Remembers the current subject.
	date_start = '0' # Remembers the current date.
	outlist = ['1']*threshold # Stores Wear values as they are determined.
	end_subject = True # Indicates whether a new subject has been reached.
	end_date = True # Indicates whether a new day has been reached.
	end_file = False # Indicates whether the end of the file has been reached.
	
	# Read the first row of data and determine the initial date and subject values.
	row = infile.readline()
	if row == '':
		end_file = True
	rowlist = row.split(',')

	# Loop over the entire file.
	while not end_file:
	
		# If we are starting a new subject or a new day.
		if end_subject or end_date:
		
			# Reinitialize the below variables for a new day.
			slide_counter = 0
			end_subject = False
			end_date = False
			subject_start = rowlist[subject_col]
			date_start = rowlist[date_col]
			
			if separate:
				print subject_start, date_start
			else:
				print subject_start
				
			# Read in the first window.
			window = first_window(window, rowlist, infile, threshold, variable_col, subject_start, date_start, separate, date_col, subject_col);
			
			# If the number of data points was smaller than threshold, we will output 2's.
			if len(window) < threshold:
				outlist=['2']*len(window)
				end_date = True
			else:
				# Determine whether the window is all zeros.
				zeros = all_zeros(window, threshold);
				# If the window is all zeros, set the output list to all '0'.
				if zeros:
					outlist=['0']*threshold
					
		# If we are continuing the current subject and current day.
		else:
			# Slide the window.
			slide_counter = slide_counter+1
			window = slide_window(window, rowlist, variable_col);
			outlist.append('1')
			
			# Determine whether the window is all zeros.
			zeros = all_zeros(window, threshold);
			
			# If the window is all zeros, set the corresponding values of the output list to '0'.
			if zeros:
				for i in range(slide_counter,threshold+slide_counter):
					outlist[i] = '0'

		# Read the next line and check whether it is a new subject, new day, or end of file.
		row = infile.readline()
		if row == '':
			end_file = True
		else:
			rowlist = row.split(',')
			if rowlist[subject_col] != subject_start:
				end_subject = True
			if separate and rowlist[date_col] != date_start:
				end_date = True
					
		# If we have finished the current day, send the data in outlist to the output file.
		if end_file or end_subject or end_date:
			for i in outlist:
				print>>outfile, i
			outlist=['1']*threshold

	# Close the input and output files.
	outfile.close()
	infile.close()

if __name__ == '__main__':
	main()