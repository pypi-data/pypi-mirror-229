import pyuff

from vbeam.data_importers import parse_pyuff_scan

uff = pyuff.Uff("/home/magnusk/vbeam/sonar_ping.uff")
channel_data: pyuff.ChannelData = uff.read("channel_data")
scan = parse_pyuff_scan(uff.read("b_data_raw/scan"))
# setup = import_pyuff(channel_data, scan)