import time


def trace(*args):   # args = psuVdsTestParameters, [psuVgsTestParameters]
    Vds = args[0]["Start V"]
    args[0]["psuobject"].setvoltage(0)
    args[0]["psuobject"].setcurrent(args[0]["Max I"])
    args[0]["psuobject"].turnon()
    if len(args) > 1:
        Vgs = args[1]["Start V"]
        args[1]["psuobject"].setvoltage(0)
        args[1]["psuobject"].setcurrent(args[1]["Max I"])
        args[1]["psuobject"].turnon()

    while Vds <= args[0]["End V"]:
        args[0]["psuobject"].setvoltage(Vds)
        readVds = args[0]["psuobject"].read(3)
        if len(args) > 1:
            while Vgs <= args[1]["End V"]:
                args[1]["psuobject"].setvoltage(Vgs)
                readVds = args[1]["psuobject"].read(3)
                print(args[0].POLARITY * Vds, args[1].POLARITY * readVds["voltage"], args[1].POLARITY * readVds["current"], readVds["mode"])
                Vgs += step
                time.sleep(IDLESECS)
            Vgs = VgsStart
        else:
            print(args[0].POLARITY * readVds["voltage"], args[0].POLARITY * readVds["current"], readVds["mode"])
            Vds += step

