from paramiko import *

rpi_remote = '10.42.0.196'
rpi_port = 22

t = Transport((rpi_remote, rpi_port))
t.connect(None, 'pi', 'raspberry')

sftp = SFTPClient.from_transport(t)
print(sftp.listdir('.'))
t.close()
