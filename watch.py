from lib.garden import Garden

garden = Garden()


while True:
	moisture = garden.read_mcp3008(channel_num=0)

	if moisture < garden.moisture_threshold:
		garden.notify("Stopped watering the garden.")
		os.system('insteonic irrigation off')
	else:
		garden.notify("Started watering the garden.")
		os.system('insteonic irrigation on')
