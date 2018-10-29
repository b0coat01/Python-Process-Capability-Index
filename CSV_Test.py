import csv
import numpy as np
from scipy import stats
import sys

def selection_sort(x):
    for i in range(len(x)):
        swap = i + np.argmax(x[i:])
        (x[i], x[swap]) = (x[swap], x[i])
    return x

f_in = open('DWS_TEMP.csv', 'r')
f_out = open('DWS_TEMP_FILTERED.csv', 'w', newline='')
ln_cntr = 0
Bin_Cntr = 1
Bin_Index = 0
D_Prev = 0
D_Bin_List = []
timedelta = []
list_hist = []
list_elapse = []
time_cntr = 0
drop_cntr = 0
modal_cntr = 0
time_start = 0
time_stop = 0
time_elapse = 0
hist_cntr = 0
w, h = 8, 1;
D_Pnt = [[0 for x in range(w)] for y in range(h)] 

with f_in:
	reader = csv.reader(f_in)
	for row in reader:
		row_len = len(row)
		newrow=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		D_Pnt=np.vstack((D_Pnt,newrow))
		if ln_cntr > 0:
			for index in range(len(row)):
				if index == 0: #DATE
					TmpDate = row[index].split("@",2)
					TmpDate_Split = TmpDate[0].split("/",3)
					TmpTime_Split = TmpDate[1].split(":",2)
					TimeBase = (float(TmpDate_Split[2])-2000)*525949+float(TmpDate_Split[0])*43800+float(TmpDate_Split[1])*1440+float(TmpTime_Split[0])*60+float(TmpTime_Split[1])
					D_Pnt[ln_cntr][0]=TimeBase
					D_Pnt[ln_cntr][1]=TmpDate_Split[1]
					D_Pnt[ln_cntr][2]=float(TmpTime_Split[0])*60+float(TmpTime_Split[1])
				if index == 6: #LaneAB
					D_Pnt[ln_cntr][3]=row[index]
				if index == 11: #DimX
					D_Pnt[ln_cntr][4]=row[index]
				if index == 12: #DimY
					D_Pnt[ln_cntr][5]=row[index]
				if index == 13: #DimZ
					D_Pnt[ln_cntr][6]=row[index]
				if index == 19: #ErrCode
					if row[index] == "@@":
						D_Pnt[ln_cntr][7]=0
					else:
						D_Pnt[ln_cntr][7]=row[index]
		ln_cntr += 1

D_Pnt = np.array(D_Pnt)
for index in range(h):
	#print ("Dim Sort N: ",'% 6.0f' % index)
	if (D_Pnt[index,4]!='0' and D_Pnt[index,5]!='0' and D_Pnt[index,6]!='0'): 
		D_Pnt_Out = np.delete(D_Pnt, (index), axis=0)
	if (float(D_Pnt[index,4])!=0 and float(D_Pnt[index,5])!=0 and float(D_Pnt[index,6])!=0): 
		D_Pnt_Out = np.delete(D_Pnt, (index), axis=0)

D_Pnt_Out = D_Pnt_Out[D_Pnt_Out[:,0].argsort()]	

for index in range(ln_cntr):
	D_Dim = [float(D_Pnt_Out[index,4]), float(D_Pnt_Out[index,5]), float(D_Pnt_Out[index,6])]
	D_Dim_Sort = selection_sort(D_Dim)
	D_Pnt_Out[index,4] = D_Dim_Sort[0]
	D_Pnt_Out[index,5] = D_Dim_Sort[1]
	D_Pnt_Out[index,6] = D_Dim_Sort[2]
	
for index in range(ln_cntr):
	if D_Prev == D_Pnt_Out[index,0]:
		Bin_Cntr += 1
	else:
		if Bin_Index != 0:
			D_Bin_List.append(Bin_Cntr)
		Bin_Cntr = 1
		Bin_Index += 1
		D_Prev = D_Pnt_Out[index,0]
		
def runningMeanFast(x, N):
	return np.convolve(x, np.ones((N,))/N)[(N-1):]

TP_Rate_Peak = np.amax(D_Bin_List)*(60)
print("TP_Rate_Peak[ 1 ]: ",'% 6.0f' % TP_Rate_Peak)

for index in range(2, 10, 2):
	x = D_Bin_List
	N=index
	RunAvg_Out = runningMeanFast(x, N)
	TP_Rate_Peak = np.amax(RunAvg_Out)*(60/N)
	print("TP_Rate_Peak[", index, "]: ",'% 6.0f' % TP_Rate_Peak)
	
with f_out as csvfile:
	datawriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	h=D_Pnt_Out.shape[0]
	#print ("h:",h)
	for index in range(h):
		#print (drop_cntr)
		#print (D_Pnt_Out[index,3])
		if (D_Pnt_Out[index,4]!='0' and D_Pnt_Out[index,5]!='0' and D_Pnt_Out[index,6]!='0'): 
				if (float(D_Pnt_Out[index,4])!=0 and float(D_Pnt_Out[index,5])!=0 and float(D_Pnt_Out[index,6])!=0): 
					datawriter.writerow([D_Pnt_Out[index,0],D_Pnt_Out[index,1],D_Pnt_Out[index,2],D_Pnt_Out[index,3],D_Pnt_Out[index,4],D_Pnt_Out[index,5],D_Pnt_Out[index,6],D_Pnt_Out[index,7]])
				else:
					drop_cntr += 1

print ("Parcel Count: ",'% 6.0f' % ln_cntr)

scan_loss = drop_cntr/ln_cntr*100
print ("Scan Loss: ",'% 6.1f' % scan_loss,"%")

TP_Rate = np.mean(D_Bin_List)
TP_Rate_Std = np.std(D_Bin_List)
USL = 1800
LSL = 0
print("Throughput StdDev: ",'% 6.2f' % TP_Rate_Std)
Cpk_0 = (TP_Rate-LSL)/(3*TP_Rate_Std)
Cpk_1 = (USL-TP_Rate)/(3*TP_Rate_Std)
if Cpk_0 < Cpk_1:
	print("Cpk: ",'% 6.2f' % Cpk_0)
	if Cpk_0 < 1:
		print("Process is Not Capable (Cpk0)!")
else:
	print("Cpk: ",'% 6.2f' % Cpk_1)
	if Cpk_1 < 1:
		print("Process is Not Capable (Cpk1)!")