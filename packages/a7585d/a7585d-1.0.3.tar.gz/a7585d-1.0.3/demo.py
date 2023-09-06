from a7585d.a7585d import A7585D 
from a7585d.a7585d import A7585D_REG
import time


hv = A7585D()


# open serial port
hv.open("COM4") # Windows
# hv.open("/dev/ttyUSB0") # Linux USB
# hv.open("/dev/ttyS0") # Linux UART

# configure parameters HV

# set control output control loop mode
# 0 Digital mode (output voltage is vtarget)
# 1 Analog mode (output voltage is proportional to vref)
# 2 Thermal compensation (output voltage is vtarget - Tcoef * (T - 25)
hv.set_parameter(A7585D_REG.CNTRL_MODE, 0)  

# set voltage target to 40V
hv.set_parameter(A7585D_REG.V_TARGET, 42.5)

# set max voltage 1mA
hv.set_parameter(A7585D_REG.MAX_I, 4)

# set max voltage (compliance) to 50V
hv.set_parameter(A7585D_REG.MAX_V, 50)

# configure SiPM temperature compensation coefficient
hv.set_parameter(A7585D_REG.T_COEF_SIPM, -35)

# configure ramp speed to 5V/s
hv.set_parameter(A7585D_REG.RAMP, 5)

# set current monitor range
# 0 low range
# 1 high range
# 2 auto select
hv.set_parameter(A7585D_REG.CURRENT_RANGE, 2)


# control pi controller (1 enable)
hv.set_parameter(A7585D_REG.ENABLE_PI, 0)

# enable hv
hv.set_parameter(A7585D_REG.HV_ENABLE, 0)

while True:
    print("HV V_OUT: " + str(hv.get_parameter(A7585D_REG.MON_VOUT)))
    print("HV I_OUT: " + str(hv.get_parameter(A7585D_REG.MON_IOUT)))
    time.sleep(0.1)
