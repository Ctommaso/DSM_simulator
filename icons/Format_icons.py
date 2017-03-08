from PIL import Image

def main():
	
	name=["battery_capacity", "battery_power"]
	for fn in name:
		houses_im = Image.open(fn+'.png')
		houses_im = houses_im.resize((50,40),Image.ANTIALIAS)
		houses_im.save(fn+'50x40.png')
				
if __name__ == '__main__':
	main()
