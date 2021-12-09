import numpy as np
import cv2 as cv
from sys import argv
import csv
import matplotlib
import matplotlib.pyplot as plt

def get_simple_cross(size, colored = True):
	if colored:
		ret_arr = np.full([size, size, 3], 255, dtype = np.uint8)
	else:
		ret_arr = np.full([size, size], 255, dtype = np.uint8)
	
	for rownum, row in enumerate(ret_arr):
		for colnum, pixel in enumerate(row):
			if abs(colnum - size/2) < size * 0.01 or abs(rownum - size/2) < size * 0.01:
				ret_arr[rownum][colnum] = [0, 0, 0] if colored else 0
				
	return ret_arr


def read_sticks(filename):
	ail = []
	ele = []
	thr = []
	rud = []
	with open(filename) as csv_with_logs:
		csvreader = csv.DictReader(csv_with_logs)
		for entry in csvreader:
			ail.append(int(entry['Ail']))
			ele.append(int(entry['Ele']))
			thr.append(int(entry['Thr']))
			rud.append(int(entry['Rud']))
	return {'Ail' : np.array(ail), 'Ele' : np.array(ele), 'Thr' : np.array(thr), 'Rud' : np.array(rud)}
	
def to_freqlist(arrayof, minval, maxval):
	pos, freq = np.unique(arrayof, return_counts=True)
	full_pos, full_freq = [], []
	for i in range(minval, maxval + 1):
		full_pos.append(i)
		if i in pos.tolist():
			full_freq.append(freq[pos.tolist().index(i)])
		else:
			full_freq.append(0)
	return full_pos, full_freq
	
def to_2d_freqlist(abscissa, ordinate, minval, maxval):
	ao_pairs = zip(abscissa.tolist(), ordinate.tolist())
	freq_array = np.zeros((maxval - minval + 1, maxval - minval + 1), dtype = np.uint64)
	for i,j in ao_pairs:
		freq_array[i - minval][j - minval] += 1
	return freq_array
				
def lower_dimension_of_sticklog(vals, min_big, max_big, min_small, max_small):
	newvals = []
	for i in vals:
		newvals.append(round(i * (max_small - min_small) / (max_big - min_big)))
	return np.array(newvals)
	
def get_heatmap_raw(frlist_array, min_val, max_val):
	fig, ax = plt.subplots(figsize=(1,1), dpi = 300)
	im = ax.imshow(frlist_array, origin = 'lower', cmap=plt.get_cmap('Reds'), aspect = 'equal')
	ax.set_xticks([])
	ax.set_yticks([])
	
	plt.gca().set_axis_off()

	fig.tight_layout(pad = 0)
	fig = plt.gcf()
	fig.canvas.draw()
	
	my_img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
	my_img = my_img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
	my_img = cv.cvtColor(my_img, cv.COLOR_RGB2BGR)
	
	return my_img

def main():
	min_stick, max_stick = -1024, 1024
	min_plot, max_plot = -25, 25
	figsize = 300
	sep_pixel = 0
	sep_width = 10
	stick_log = read_sticks(argv[1])
	ailerons = lower_dimension_of_sticklog(stick_log['Ail'], min_stick, max_stick, min_plot, max_plot)
	elevators = lower_dimension_of_sticklog(stick_log['Ele'], min_stick, max_stick, min_plot, max_plot)
	throttles = lower_dimension_of_sticklog(stick_log['Thr'], min_stick, max_stick, min_plot, max_plot)
	rudders = lower_dimension_of_sticklog(stick_log['Rud'], min_stick, max_stick, min_plot, max_plot)
	freqlist_left = to_2d_freqlist(throttles, rudders, min_plot, max_plot)
	freqlist_right = to_2d_freqlist(elevators, ailerons, min_plot, max_plot)
	

	hm_left = get_heatmap_raw(freqlist_left, min_plot, max_plot)
	hm_right = get_heatmap_raw(freqlist_right, min_plot, max_plot)
	s_cross = get_simple_cross(figsize, colored = True)
	alpha = 0.95
	beta = 1 - alpha
	hm_left_with_cross = cv.addWeighted(hm_left, alpha, s_cross, beta, 0.0)
	hm_right_with_cross = cv.addWeighted(hm_right, alpha, s_cross, beta, 0.0)
	
	assert hm_left_with_cross.shape == hm_right_with_cross.shape
	sep = np.empty((figsize, sep_width, 3), dtype = np.uint8)
	sep.fill(0)
	
	clean_final = np.concatenate((hm_left_with_cross, sep, hm_right_with_cross), axis = 1)
	
	cv.imwrite(argv[1] + '.png', clean_final)
		
	
if __name__ == "__main__":
    main() 
