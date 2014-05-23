from lib.garden import Garden

garden = Garden()

while True:
    print garden.read_mcp3008(channel_num=0)
