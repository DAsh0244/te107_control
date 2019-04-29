
import socket as _socket
from enum import Enum as _Enum

BUF_CHUNK = 10

class TempUnits(_Enum):
    C = 'C'
    F = 'F'

class RampScale(_Enum):
    MINUTES = 'MINUTES'
    HOURE = 'HOURS'

class Device:
    """
    Generic socket connected device
    """

    @classmethod
    def from_other_dev(cls, dev):
        """Factory function for generating a new instance of the object as a more specific subclass"""
        assert issubclass(cls, dev)
        return cls(dev.host,dev.port,conn=dev._conn,id=dev._id)

    def __init__(self, host, port=5025,timeout=None,*args, **kwargs):
        self._host = host
        self._port = port
        self.timeout = timeout
        print('making conn {}:{}'.format(host,port))
        self._conn = kwargs.get('conn', _socket.create_connection((self._host,self._port),timeout=timeout))
        self._id = kwargs.get('id', None)
        self.encoding = kwargs.get('encoding', 'ascii')
        self.EOL = b'\n'
        if self._id is None:
            self.get_id()

    def _clear_buffer(self):
        self._conn.settimeout(self.timeout)
        try:
            res = self._conn.recv(BUF_CHUNK)
            print(res)
            # while res:
            # res = self._conn.recv(BUF_CHUNK)
        except _socket.timeout:
            pass

    def _readline(self):
        msg = b'FAILED'
        try:
            msg = bytearray(self._conn.recv(BUF_CHUNK))
            # print(msg)
            while msg[-1] != ord(self.EOL):
                # print('next chunk')
                msg.extend(self._conn.recv(BUF_CHUNK))
                # print(msg)
        except _socket.timeout:
            pass
        # print('return')
        return msg.decode(self.encoding).strip()

    def send_cmd(self,cmd:str):
        self._conn.send(cmd.encode(self.encoding)+self.EOL)

    def get_id(self):
        # print('clearing_buff')
        self._clear_buffer()
        # print('asking ID')
        self.send_cmd('*IDN?')
        # print('reading response')
        self._id = self._readline()
        # print('got id ',self._id)
        return self._id 

    def __del__(self):
        self._conn.close()

from time import sleep
class F4TController (Device):
    def __init__(self, set_point:float=22.0, units:TempUnits=TempUnits.C, profile:int=1,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_point = set_point
        self.temp_units = units
        self.current_profile = profile
        self.timeout = 1.5
        self.profiles = {}
    
    def get_profiles(self):
        # doesnt work if profile is running
        for i in range(1,40):
            self.select_profile(i)
            sleep(0.5)
            self.send_cmd(':PROGRAM:NAME?')
            sleep(0.5)
            name = self._readline().strip().replace('"','')
            # print(name)
            if name:
                self.profiles[i] = name
            else:
                break

    def get_units(self):
        self._clear_buffer()
        self.send_cmd(':UNIT:TEMPERATURE?')
        resp = self._readline()
        self.temp_units = TempUnits(resp)        

    def set_units(self, units:TempUnits=None):
        if units is None:
            units = self.temp_units
        self.send_cmd(':UNITS:TEMPERATURE {}'.format(units.value))

    def set_ramp_scale(self,ramp_scale,cloop=1):
        scale = RampScale(ramp_scale)
        self.send_cmd(':SOURCE:CLOOP{}:RSCALE {}'.format(cloop,scale))

    def set_ramp_rate(self,ramp_rate,cloop=1):
        self.send_cmd(':SOURCE:CLOOP{}:RRATE {}'.format(cloop,ramp_rate))

    def set_ramp_time(self,ramp_time,cloop=1):
        self.send_cmd(':SOURCE:CLOOP{}:RTIME {}'.format(cloop,ramp_time))

    def select_profile(self, profile:int):
        # assert profile =< 40 and profile >= 1
        self.send_cmd(':PROGRAM:NUMBER {}'.format(profile))
    
    def run_profile(self):
        self.send_cmd(':PROGRAM:SELECTED:STATE START')

    def stop_profile(self):
        self.send_cmd(':PROGRAM:SELECTED:STATE STOP')

    def get_temperature(self,cloop=1):
        self.send_cmd(':SOURCE:CLOOP{}:PVALUE?'.format(cloop))
        return self._readline()

    def set_temperature(self,temp,cloop=1):
        self.send_cmd('SOURCE:CLOOP{}:SPOINT {}'.format(cloop,temp))

    def is_done(self,ouput_num):
        self.send_cmd(':OUTPUT{}:STATE?'.format(ouput_num))
        sleep(0.2)
        resp = self._readline()
        status = None
        if resp == 'ON':
            status = True
        elif resp == 'OFF':
            status = False
        return status

    def set_output(self,output_num,state):
        self.send_cmd(':OUTPUT{}:STATE {}'.format(output_num,state))
 

if __name__ == "__main__":
    start = 5
    stop = 125
    step = 5
    ramp_time_min = 3.0
    soak_time_min = 7.0
    temps = range(start,stop+step,step)
    x = F4TController(host='169.254.250.143',timeout=1)
    # x.get_units()
    # print(x.get_temperature())
    # print(x.temp_units)
    x.get_profiles()
    print(x.profiles)
    # x.set_temperature(5)
    # x.send_cmd(':SOURCE:CLOOP1:SPOINT?') 
    # sleep(0.2)
    # print(x._readline())
    # x.set_output(1,'ON')
    # x.set_temperature(50)
    # 1 is 5 - 125
    # x.select_profile(1)
    sleep(0.5)
    x.send_cmd(':PROGRAM:NAME?')
    sleep(0.5)
    print(x._readline().strip())
    x.set_ramp_time(ramp_time_min)
    x.set_ramp_scale(RampScale.MINUTES)
    for temp in temps:
        x.set_temperature(temp)
        sleep(ramp_time_min*60)
        while abs(x.get_temperature() - temp) > 0.2:
            sleep(1.0)
        # begin soak
        print('beginning soak at temp {}'.format(x.get_temperature()))
        sleep(soak_time_min*60)
    # x.run_profile()
    # sleep(0.5)
    try:
        while True:
            print(x.get_temperature())
            sleep(1)
    except KeyboardInterrupt:
        pass 
    print('done')

    # x.set_temperature(22.0)