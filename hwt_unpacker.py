import os
import shutil
import zipfile
import struct
from PIL import Image
from io import BytesIO

def unzippng(filename):
    pngfilename = filename.split(".bin")[0]
    pngbinsize = int((os.path.getsize(filename) - 8) / 4)
    pngbinfile = open(filename, "rb")
    tempdata = pngbinfile.read(8)
    header, width, height = struct.unpack("L2H", tempdata)

    pngdata = bytearray()

    offset = 0
    while offset < pngbinsize:
        tmpdata = pngbinfile.read(4)
        b, g, r, a = struct.unpack("4B", tmpdata)
        if b == 137 and g == 103 and r == 69 and a == 35:
            tmpdata = pngbinfile.read(4)
            b, g, r, a = struct.unpack("4B", tmpdata)
            tmpdata = pngbinfile.read(4)
            size = struct.unpack("L", tmpdata)
            for cnt in range(size[0]):
                pngdata.append(r)
                pngdata.append(g)
                pngdata.append(b)
                pngdata.append(a)
            offset = offset + 3
        else:
            pngdata.append(r)
            pngdata.append(g)
            pngdata.append(b)
            pngdata.append(a)
            offset = offset + 1

    pngfile = Image.frombytes("RGBA", (width, height), bytes(pngdata))
    pngfile.save(pngfilename)
    pngbinfile.close()

def unzipbin(dirname):
    indexfile = open(dirname + "/BitmapMapping.xml.bin", "rb")
    binfile = open(dirname + "/gui.bin", "rb")
    binfile.read(8)

    indexsize = int(os.path.getsize(dirname + "/BitmapMapping.xml.bin") / 8)
    for index in range(indexsize):
        indexdata = indexfile.read(8)
        offset, size = struct.unpack("LL", indexdata)
        if size == 0:
            pass
        else:
            pngbindata = binfile.read(size)
            pngbinfilename = dirname + "/A100_%03d.png.bin" % (index + 1)
            pngbinfile = open(pngbinfilename, "wb")
            pngbinfile.write(pngbindata)
            pngbinfile.close()
            unzippng(pngbinfilename)
            os.remove(pngbinfilename)

    indexfile.close()
    binfile.close()
    os.remove(dirname + "/BitmapMapping.xml.bin")
    os.remove(dirname + "/gui.bin")

def unzipwatchface(dirname):
    watchface = open(dirname + "/com.huawei.watchface", "rb")
    tempdata = watchface.read(16)
    header, xmllen, indexlen, binlen, blank = struct.unpack("2H3L", tempdata)
    xmloffset = 0
    indexoffset = xmllen
    binoffset = xmllen + indexlen

    xmldata = watchface.read(xmllen)
    # xmlfile = open(dirname + "/watchface/watch_face_config.xml.bin", "wb")
    # xmlfile.write(xmldata)
    # xmlfile.close()

    indexdata = watchface.read(indexlen)
    indexfile = open(dirname + "/watchface/res/BitmapMapping.xml.bin", "wb")
    indexfile.write(indexdata)
    indexfile.close()

    bindata = watchface.read(binlen)
    binfile = open(dirname + "/watchface/res/gui.bin", "wb")
    binfile.write(bindata)
    binfile.close()

    unzipbin(dirname + "/watchface/res")

    watchface.close()
    os.remove(dirname + "/com.huawei.watchface")

hwt_list = os.listdir(r'.')
for filename in hwt_list:
    if filename.endswith('.hwt'):
        dirname = filename.split(".hwt")[0]
        print(dirname)
        while os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)
        os.mkdir(dirname + "/watchface")
        os.mkdir(dirname + "/watchface/res")

        hwtfile = zipfile.ZipFile(filename, 'r')
        for file in hwtfile.namelist():
            hwtfile.extract(file, dirname)
        hwtfile.close()
        unzipwatchface(dirname)
        shutil.copy(dirname + "/description.xml", dirname + "/watchface/watch_face_info.xml")

        