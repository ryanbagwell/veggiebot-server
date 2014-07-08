



def get_volts(reading, input_volts=3.3):
    """ Convert a digital reading to volts """

    return (reading * input_volts) / 1024


def get_kpa(kohms, celsius):
    """ Conversion equations taken from
        http://www.kimberly.uidaho.edu/water/swm/calibration_watermark2.pdf """

    if kohms < 1:
        kpa = -20 * (kohms * (1 + 0.018 * (celsius - 24)) - 0.55)

    elif 1 < kohms < 8:
        kpa = (-3.213 * kohms - 4.093) / (1 - 0.009733 * kohms - 0.01205 * celsius)
    else:
        kpa = -2.246 - 5.239 * kohms * (1 + 0.018 * (celsius - 24)) - (0.06756**2) * (1 + 0.018 * (celsius - 24))**2

    return kpa



