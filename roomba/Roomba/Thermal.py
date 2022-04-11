import adafruit_mlx90640
import board
import busio
import numpy
from Roomba import Settings
from matplotlib import pyplot
from Roomba import RegionInterest


class Thermal:
    def __init__(self):
        print('Creating thermal camera')
        self.ic2 = busio.I2C(board.SCL, board.SDA, frequency=400000)
        self.mlx = adafruit_mlx90640.MLX90640(self.ic2)
        self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
        self.msg = ("MLX addr detected on I2C", [hex(i) for i in self.mlx.serial_number])
        self.frame = [0] * 768

        self.centers = Settings.thermal_roi
        self.fov = Settings.thermal_fov
        self.regions = RegionInterest.Regions(width=32, height=24, fov=self.fov, centers=self.centers)

    def get_data(self, plot=False):
        self.mlx.getFrame(self.frame)
        self.frame = list(map(int, self.frame))
        data = numpy.array(self.frame)
        data = data.reshape((24, 32))
        data = numpy.fliplr(data)
        if plot:
            pyplot.imshow(data)
            pyplot.colorbar()
            pyplot.show()
        return data

    def look(self, plot=False, as_frame=False):
        snapshot = self.get_data()
        result = self.regions.get_stats(snapshot)
        if plot:
            pyplot.plot(result, 'o-k')
            pyplot.xlabel('Region Number')
            pyplot.ylabel('Intensity')
            pyplot.show()
        return result

# t = Thermal()
# s = t.get_snapshot()
# pyplot.imshow(s)
# pyplot.show()
#
# x = t.look()
