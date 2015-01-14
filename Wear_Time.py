from collections import deque

#Function to determine whether all vm values in a window are '0'
def all_zeros(window, threshold):
    numzeros = window.count('0')
    if numzeros == threshold:
        zeros = True
    else:
        zeros = False
    return zeros;

#Function to read in the first window of a day.
def first_window(window, rowlist, infile, outfile, threshold, vm, subject_start, date_start, separate):

    window.clear()
    window.append(rowlist[vm])

    for i in range(0,threshold-1):
        prev_line = infile.tell()
        row = infile.readline()
        if row == '':
            print "Threshold exceeds number of data points on day", date_start, "for subject ID", subject_start
            infile.seek(prev_line)
            break
        else:
            rowlist = row.split(',')
            if separate and rowlist[date] != date_start:
                print "Threshold exceeds number of data points on day", date_start, "for subject ID", subject_start
                infile.seek(prev_line)
                break
            elif rowlist[subject] != subject_start:
                print "Threshold exceeds number of data points on day", date_start, "for subject ID", subject_start
                infile.seek(prev_line)
                break
            else:
                window.append(rowlist[vm])
    
    return window;

#Function to slide the window over one spot.
def slide_window(window, rowlist):

    window.append(rowlist[vm])
    window.popleft()
    
    return window;

outfile=open('Output.csv','w')
print>>outfile, 'Wear'

#Prompts the user for the file name.
filename = raw_input('Enter file name, including extension.\n')
infile=open(filename, 'r')

#As an alternative to the above prompt, the file name can be entered here.
#infile=open('endline1029.csv', 'r')

#Prompts the user for the window width.
threshold = input('Enter number of consecutive zeros to scan for.\n')

#As an alternative to the above prompt, the threshold can be entered here.
#threshold = 360

#Prompts the user to decide whether to treat each day as separate.
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

#Read the first row of the file and use it to find the ID, date, and vm columns.
row = infile.readline()
rowlist = row.split(',')
i=0
for x in rowlist:
    if x == 'vm' or x == 'vm\n':
        vm = i
    if x == 'ID' or x == 'ID\n':
        subject = i
    if x == 'Date' or x == 'Date\n':
        date = i
    i=i+1

#Initializing variables.
window=deque()#Contains a number of vm values equal to threshold.
zeros = False#Indicates whether the current window is all zeros.
slide_counter = 0#Remembers how many times the window has slid on a given day.
subject_start = '0'#Remembers the current subject.
date_start = '0'#Remembers the current date.
outlist=['1']*threshold#Stores Wear values as they are determined.
end_subject = True#Indicates whether a new subject has been reached.
end_date = True#Indicates whether a new day has been reached.
end_file = False#Indicates whether the end of the file has been reached.

#Read the first row of data and determine the initial date and subject values.
row = infile.readline()
if row == '':
    end_file = True
rowlist = row.split(',')

#Loop over the entire file.
while not end_file:

    #If we are starting a new subject or a new day.
    if end_subject or end_date:

        #Reinitialize the below variables for a new day.
        slide_counter = 0
        end_subject = False
        end_date = False
        subject_start = rowlist[subject]
        date_start = rowlist[date]

        if separate:
            print subject_start, date_start
        else:
            print subject_start
        
        #Read in the first window.
        window = first_window(window, rowlist, infile, outfile, threshold, vm, subject_start, date_start, separate);

        #If the number of data points was smaller than threshold, we will output 2's.
        if len(window) < threshold:
            outlist=['2']*len(window)
            end_date = True
        else:
            #Determine whether the window is all zeros.
            zeros = all_zeros(window, threshold);
            #If the window is all zeros, set the output list to all '0'.
            if zeros:
                outlist=['0']*threshold

    #If we are continuing the current subject and current day.
    else:
        #Slide the window.
        slide_counter = slide_counter+1
        window = slide_window(window, rowlist);
        outlist.append('1')
        
        #Determine whether the window is all zeros.
        zeros = all_zeros(window, threshold);

        #If the window is all zeros, set the corresponding values of the output list to '0'.        
        if zeros:
            for i in range(slide_counter,threshold+slide_counter):
                outlist[i] = '0'

    if end_date:
        for i in outlist:
            print>>outfile, i
        outlist=['1']*threshold
        row = infile.readline()
        if row == '':
            end_file = True
        else:
            rowlist = row.split(',')

    else:
        #Read the next line and check wether it is a new subject, new day, or end of file.
        row = infile.readline()
        if row == '':
            end_file = True
        else:
            rowlist = row.split(',')
            if rowlist[subject] != subject_start:
                end_subject = True
            if separate and rowlist[date] != date_start:
                end_date = True

        #If we have finished the current day, send the data in outlist to the output file.      
        if end_file or end_subject or end_date:
            for i in outlist:
                print>>outfile, i
            outlist=['1']*threshold

#Close the input and output files.
outfile.close()
infile.close()
