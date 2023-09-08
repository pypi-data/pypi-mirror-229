import random

def main():
	pracs = ['aerobic', 'sprints', 'technique', 'gym', 'mostly talk']
	prac = random.choice(pracs)
	print("Today's practice will be %s." % prac)
	if prac in ['aerobic', 'mostly talk']:
		print('Sorry...')
	else:
		print('Yes!')

if __name__ == '__main__':
	main()
