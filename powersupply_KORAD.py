# Useful information about KORAD command set: https://sigrok.org/wiki/Korad_KAxxxxP_series

import serial
import time
import logging

# set up logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(name)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class KORAD:
    """
    Class for KORAD (RND) power supply
    """
    name = "Korad"
    KORAD_SPECS = {
        "KA3003P": (0.0, 31.0, 3.0, 90, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KA3005P": (0.0, 31.0, 5.1, 150, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),
        # confirmed (with the RND incarnation of the KA3005P)
        "KD3005P": (0.0, 31.0, 5.1, 150, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KA3010P": (0.0, 31.0, 10.0, 300, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KA6002P": (0.0, 60.0, 2.0, 120, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KA6003P": (0.0, 60.0, 3.0, 180, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KA6005P": (0.0, 31.0, 5.0, 300, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KD6005P": (0.0, 31.0, 5.0, 300, 0.01, 0.001, 0.01, 0.001, 0.0, 0.0, 2.0),  # not confirmed
        "KWR103": (0.0, 60.5, 15.0, 300, 0.001, 0.001, 0.001, 0.001, 0.0, 0.0, 2.0)
        # confirmed (with the RND incarnation of the KWR103
    }
    KORAD_TIMEOUT = 2.0

    def __init__(self, port, debug=False):
        super().__init__()

        self._debug = bool(debug)
        self.port = port
        baud = 19200

        try:
            self._Serial = serial.Serial(self.port, baudrate=baud, bytesize=8, parity='N', stopbits=1,
                                         timeout=KORAD.KORAD_TIMEOUT, exclusive=True)
        except serial.SerialException as e:
            raise e

        if self._debug:
            logger.info('KORAD <- %s' % self._Serial)

        time.sleep(0.2)

        self._Serial.flushInput()
        self._Serial.flushOutput()

        try:
            typestring = self._query('*IDN?', True).split(" ")

            if len(typestring) < 2:
                raise RuntimeError('No KORAD power supply connected to ' + port)
            if not (typestring[0].upper() in ['KORAD', 'RND', 'VELLEMAN', 'TENMA']):
                raise RuntimeError('No KORAD power supply connected to ' + port)
            if typestring[1].upper() in ['KA3003P', 'KA3005P', 'KD3005P', 'KD3010P',
                                         'KA6002P', 'KA6003P', 'KA6005P', 'KD6005P', 'KWR103']:
                self.MODEL = typestring[1]
                logger.info('KORAD - ' + self.MODEL + '  detected')
            else:
                logger.warning('Unknown KORAD model: ' + typestring[1])
                self.MODEL = '?????'

            v = KORAD.KORAD_SPECS[self.MODEL]
            self.VMIN = v[0]
            self.VMAX = v[1]
            self.IMAX = v[2]
            self.PMAX = v[3]
            self.VRESSET = v[4]
            self.VRESSETCNT = len(str(v[4]).split(".")[1])  # the number of digits after the dot(fractional digits)
            self.IRESSET = v[5]
            self.IRESSETCNT = len(str(v[5]).split(".")[1])
            self.VRESREAD = v[6]
            self.IRESREAD = v[7]
            self.VOFFSETMAX = v[8]
            self.IOFFSETMAX = v[9]
            self.MAXSETTLETIME = v[10]
            self.READIDLETIME = self.MAXSETTLETIME / 50
            self.polarity = True

            if debug:
                logger.info('\n' +
                            'VRESSETCNTMAX = ' + str(self.VRESSETCNT) + '\n' +
                            'VMIN = ' + str(self.VMIN) + '\n' +
                            'VMAX = ' + str(self.VMAX) + '\n' +
                            'IMAX = ' + str(self.IMAX) + '\n' +
                            'PMAX = ' + str(self.PMAX) + '\n')

        except serial.SerialTimeoutException:
            raise RuntimeError('No KORAD powersupply connected to ' + port)
        except KeyError:
            raise RuntimeError('Unknown KORAD model ' + self.MODEL)

        self._setmaxslope(99)

    def _setmaxslope(self, slope):
        if self._query("VSLOPE?") != str(slope):
            self._query("VSLOPE:" + str(slope))
        if self._query("ISLOPE?") != str(slope):
            self._query("ISLOPE:" + str(slope))

    def output(self, enable: bool):
        if self.MODEL == "KWR103":
            self._query('OUT:%d' % int(enable))
        else:
            self._query('OUT%d' % int(enable))

    def setvoltage(self, targetvoltage):
        targetvoltage = round(targetvoltage, self.VRESSETCNT)
        if self.VMIN <= targetvoltage <= self.VMAX:
            if self.MODEL == "KWR103":
                self._query('VSET:' + str(targetvoltage))
            else:
                self._query('VSET1:' + str(targetvoltage))
        else:
            logger.warning("voltage setting out of bounds "
                           + str(self.VMAX) + " max / " + str(self.VMIN) + " min ")
            return 1

        tmp_reading1 = self.physical_psu_readings()
        t0 = time.time()
        while tmp_reading1["voltage"] != targetvoltage:
            time.sleep(0.1)
            tmp_reading2 = self.physical_psu_readings()
            if tmp_reading1["mode"] == "CC":
                if tmp_reading1["voltage"] < tmp_reading2["voltage"]:
                    tmp_reading1 = tmp_reading2
                    t0 = time.time()
                    time.sleep(0.1)
                else:
                    print("CC\n")
                    break
            if time.time() - t0 > self.MAXSETTLETIME:
                # getting consistent readings is taking too long; give up
                logger.warning(': Could not set ' + str(targetvoltage) + ' volts after ' + str(
                    self.MAXSETTLETIME) + ' s ')
                break
            tmp_reading1 = tmp_reading2

    def setcurrent(self, current):
        current = round(current, self.IRESSETCNT)
        if 0 <= current <= self.IMAX:
            if self.MODEL == "KWR103":
                self._query('ISET:' + str(current))
            else:
                self._query('ISET1:' + str(current))
        else:
            logger.warning("current setting out of bounds "
                           + str(self.IMAX) + " max / ")
            return 1

    def _query(self, cmd, answer=False):
        self._Serial.reset_output_buffer()
        self._Serial.reset_input_buffer()
        time.sleep(0.03)

        if self._debug:
            logger.info('KORAD <- %s' % cmd)

        self._Serial.write((cmd + '\n').encode())

        if answer:
            ans = self._Serial.readline().decode('utf-8').rstrip("\n\r")
            return ans

    def _reading(self):
        if self.MODEL == "KWR103":
            vq = 'VOUT?'
            iq = 'IOUT?'
        else:
            vq = 'VOUT1?'
            iq = 'IOUT1?'

        v = float(self._query(vq, True))  # read voltage:
        i = float(self._query(iq, True))  # read current:
        s = self._query('STATUS?', True)  # read output limit status:
        if s.encode()[0] & 0b00000001:  # test bit-1 for CV or CC
            s = 'CV'
        else:
            s = 'CC'
        return v, i, s

    # get n consecutive readings within tolerance
    def physical_psu_readings(self, n=0):
        if n < 0:
            raise RuntimeError('Number of consistent readings in a row must be a positive or 0 for no check')
        t0 = time.time()
        match = 0

        v, i, mode = self._reading()

        while match < n:
            print("physical reading" + str(n))
            vv, ii, ll = self._reading()
            if (abs(vv - v) <= self.VRESREAD) and (abs(ii - i) <= self.IRESREAD) and (ll == mode):
                match += 1
            else:
                v = vv
                i = ii
                match = 0
                time.sleep(self.READIDLETIME)

            if time.time() - t0 > self.MAXSETTLETIME:
                mode = "ERR"
                logger.warning(': Could not get ' + str(n) + ' consistent readings in a row after ' + str(
                    self.MAXSETTLETIME) + ' s! DUT drifting? Noise?')
                break
        return {"voltage": float(v), "current": float(i), "mode": mode}

    def __del__(self):
        try:
            self._Serial.close()
        except AttributeError:
            pass
