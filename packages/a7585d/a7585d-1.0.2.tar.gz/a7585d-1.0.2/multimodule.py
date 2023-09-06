from a7585d.a7585d import A7585D 
from a7585d.a7585d import A7585D_REG
import time

#recognize module by serial number so windows assigned port is not relevant

#Serial Number 1 = 28885
#Serial Number 2 = 12297
SNS = [ 28885, 12297 ]

MAP = [0 for i in range(len(SNS))]

hvs = [A7585D() for i in range(len(SNS))]

for i in range(len(SNS)):
    hvs[i].open("COM" + str(i+3))

for i in range(len(SNS)):
    current_sn = hvs[i].get_parameter(A7585D_REG.SERIAL_NUMBER)

    # If the read serial number is in the list, map it
    if current_sn in SNS:
        MAP[SNS.index(current_sn)] = i


print(MAP)


print(hvs[MAP[0]].get_parameter(A7585D_REG.SERIAL_NUMBER))
print(hvs[MAP[1]].get_parameter(A7585D_REG.SERIAL_NUMBER))