# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 13:19:12 2023

@author: jhodges
"""

import pyfdstools as fds
import struct
import os
import numpy as np

def writeSLCFheader(f, quantity, shortName, units, size, endianness):
    sz = struct.pack('%s%0.0fi'%(endianness, len(size)), *size)
    qty = str.encode("{:<30}".format(quantity))
    sn = str.encode("{:<30}".format(shortName))
    un = str.encode("{:<30}".format(units))
    f.write(b'\x1e\x00\x00\x00')
    f.write(qty)
    f.write(b'\x1e\x00\x00\x00\x1e\x00\x00\x00')
    f.write(sn)
    f.write(b'\x1e\x00\x00\x00\x1e\x00\x00\x00')
    f.write(un)
    f.write(b'\x1e\x00\x00\x00\x18\x00\x00\x00')
    f.write(sz)
    f.write(b'\x18\x00\x00\x00')
    #f.write(b'\x04\x00\x00\x00')

def readSLCFheader(f, endianness, byteSize=False):
    data = f.read(142)
    header = data[:110]
    size = struct.unpack('%siiiiii'%(endianness), data[118:142])
    tmp = header.split(b'\x1e')
    quantity = tmp[1].decode('utf-8').replace('\x00','').strip(' ')
    shortName = tmp[3].decode('utf-8').replace('\x00','').strip(' ')
    units = tmp[5].decode('utf-8').replace('\x00','').strip(' ')
    
    if byteSize:
        return quantity, shortName, units, size
    else:
        iX, eX, iY, eY, iZ, eZ = size
        return quantity, shortName, units, iX, eX, iY, eY, iZ, eZ

def writeSLCFTime(f, time, data, endianness):
    f.write(b'\x04\x00\x00\x00')
    t = time.tobytes()
    f.write(t)
    f.write(b'\x04\x00\x00\x00')
    f.write(struct.pack('%si'%(endianness), data.shape[0]*4))
    d = data.tobytes()
    f.write(d)
    if data.shape[0]*4 <= 65535:
        f.write(struct.pack('%sHH'%(endianness), data.shape[0]*4,0))
    else:
        f.write(struct.pack('%sI'%(endianness), data.shape[0]*4))
    #f.write(struct.pack('%sHH'%(endianness), data.shape[0]*4,0))
    #f.write(b'\x04\x00\x00\x00')

if __name__ == "__main__":
    chid = "case003"
    result_dir = "E:\\projects\\customPythonModules\\pyfdstools\\pyfdstools\\examples\\%s\\"%(chid)
    
    slcf_name = chid+"_1_1.sf"
    slcfPath = os.path.join(result_dir, slcf_name)
    
    endianness = fds.getEndianness(result_dir, chid)
    datatype = fds.getDatatypeByEndianness(np.float32, endianness)
    
    # Read baseline slice
    timesSLCF = fds.readSLCFtimes(slcfPath, None, endianness)
    f = fds.zopen(slcfPath)
    qty, sName, uts, size = fds.readSLCFheader(f, endianness, byteSize=True)
    iX, eX, iY, eY, iZ, eZ = size
    (NX, NY, NZ) = (eX-iX, eY-iY, eZ-iZ)
    print("2-D slice:", slcfPath)
    shape = (NX+1, NY+1, NZ+1)
    NT = len(timesSLCF)
    datas2 = np.zeros((NX+1, NY+1, NZ+1, NT), dtype=np.float32)
    for i in range(0, NT):
        t, data = fds.readNextTime(f, NX, NY, NZ, datatype)
        data = np.reshape(data, shape, order='F')
        datas2[:, :, :, i] = np.array(data, dtype=np.float32)
    f.close()
    
    
    # Define quantities manually
    outQty = qty
    #sName = 'temp'
    #uts = 'C'
    #size = np.array([15, 15, 0, NY, 0, NZ], dtype=np.int32)
    times = np.array(timesSLCF, dtype=np.float32)
    
    # Write slice
    outFile = 'fake.sf'
    f = fds.zopen(outFile, 'wb')
    writeSLCFheader(f, outQty, sName, uts, size, endianness)
    shape2 = ((NX+1)*(NY+1)*(NZ+1),)
    for i in range(0, NT):
        data_tmp = datas2[:, :, :, i]
        data_out = np.reshape(data_tmp, shape2, order='F')
        writeSLCFTime(f, times[i], data_out, endianness)
    f.close()
    
    # Read baseline slice
    f = fds.zopen(slcfPath)
    b1 = f.read()
    f.close()
    
    
    # Read new slice
    f = fds.zopen(outFile)
    b2 = f.read()
    f.close()
    
    
    print(struct.unpack('%siiiiiiiiiiiii'%(endianness), b1[118:118+52]))
    print(struct.unpack('%siiiiiiiiiiiii'%(endianness), b2[118:118+52]))
    
    print(struct.unpack('%siiiii'%(endianness), b1[142:142+20]))
    print(struct.unpack('%siiiii'%(endianness), b2[142:142+20]))
    
    
    i1 = data_out.shape[0]*4+156 # 1256
    i2 = data_out.shape[0]*4+156+16 # 1268
    
    print(struct.unpack('%siHHii'%(endianness), b1[i1:i2]))
    print(struct.unpack('%siHHii'%(endianness), b2[i1:i2]))

    print(b1[i1:i2])
    print(b2[i1:i2])
    
    print(b1 == b2)