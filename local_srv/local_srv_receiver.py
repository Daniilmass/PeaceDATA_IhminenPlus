from paramiko import *
import os
from time import sleep

rpi_remote = '10.42.0.196'
rpi_port = 22

t = Transport((rpi_remote, rpi_port))
t.connect(None, 'pi', 'raspberry')

sftp = SFTPClient.from_transport(t)
workdir = 'neural_photos'
if not os.path.isdir(workdir):
    os.mkdir(workdir)
os.chdir(workdir)
sftp.chdir(workdir)
try:
    while 1:
        downloadquery = sftp.listdir('.')
        for fl in downloadquery:
            sftp.get(fl, fl)
            sftp.remove(fl)
        sleep(8)
except KeyboardInterrupt:
    t.close()
