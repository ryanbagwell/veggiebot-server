from lib.garden import Garden
import time

garden = Garden()

while True:
    moisture1= garden.sample_mcp3008(channel_num=0)
    time.sleep(1)
    moisture2= garden.sample_mcp3008(channel_num=1)
    print "%s %s" % (moisture1, moisture2)
    time.sleep(1)
