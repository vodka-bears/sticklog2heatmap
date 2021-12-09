import hid
import datetime
import csv
import signal
from time import sleep
from sys import exit, argv

filename = ''

def to_signed(inp):
	if inp & 0x80:
		return inp - 256
	return inp

def main():
	signal.signal(signal.SIGINT, sigint)
	
	devs = [d for d in hid.enumerate() if d['usage_page'] == 5 or d['usage'] in (4,5,8)]
	if not devs:
		print('No game devices seem to be connected')
		exit()
	elif len(devs) == 1:
		j_vid = devs[0]['vendor_id']
		j_pid = devs[0]['product_id']
	else:
		for index, jdev in enumerate(devs):
			print(f"{index+1}) 0x{jdev['vendor_id']:04x}:0x{jdev['product_id']:04x} {jdev['product_string']}")
		num = int(input(f'Which device to use (1-{len(devs)}): ')) - 1
		j_vid = devs[num]['vendor_id']
		j_pid = devs[num]['product_id']
	filename = argv[0] + '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S') + '.csv'
	print('Writing OpenTX style stick log to ' + filename)
	print('Press Crtl+C to stop')
	with hid.Device(j_vid, j_pid) as jstick, open(filename, 'w', newline='') as csvfile:
		csvwriter = csv.DictWriter(csvfile, fieldnames = ['Date', 'Time', 'Rud', 'Ele', 'Thr', 'Ail'])
		csvwriter.writeheader()
		oldstyle = len(jstick.read(20)) < 16
		while True:
			if oldstyle:
				rawdata = jstick.read(10)
				ail = to_signed(rawdata[1]) * 8
				ele = to_signed(rawdata[2]) * 8
				thr = to_signed(rawdata[3]) * 8
				rud = to_signed(rawdata[4]) * 8
			else:
				rawdata = jstick.read(20)
				ail = rawdata[3] + rawdata[4] * 256 - 1024
				ele = rawdata[5] + rawdata[6] * 256 - 1024
				thr = rawdata[7] + rawdata[8] * 256 - 1024
				rud = rawdata[9] + rawdata[10] * 256 - 1024
			cur_datetime = datetime.datetime.now()
			date_str = cur_datetime.strftime('%Y-%m-%d')
			time_str = cur_datetime.strftime('%H:%M:%S.%f')[:-3]
			csvwriter.writerow({'Date' : date_str, 'Time' : time_str, 'Ail' : ail, 'Ele' : ele, 'Thr' : thr, 'Rud' : rud})
			sleep(0.1)


def sigint(sig, frame):
	print("Written log: " + frame.f_locals['filename'])
	exit()

if __name__ == "__main__":
	main()