import argparse
from a7585d.a7585d import A7585D
from a7585d.a7585d import A7585D_REG
import time

def main(args):
    hv = A7585D()
    hv.open(args.port)

    print("Module serial number: " + str(hv.get_parameter(A7585D_REG.SERIAL_NUMBER)))
    print("firmware version: " + str(hv.get_parameter(A7585D_REG.FW_VERSION)))
    print("hardware version: " + str(hv.get_parameter(A7585D_REG.HW_VERSION)))

    if args.power_on is not None:
        hv.set_parameter(A7585D_REG.HV_ENABLE, args.power_on)

    if args.control_mode is not None:
        hv.set_parameter(A7585D_REG.CNTRL_MODE, args.control_mode)

    if args.voltage_target is not None:
        hv.set_parameter(A7585D_REG.V_TARGET, args.voltage_target)

    if args.max_current is not None:
        hv.set_parameter(A7585D_REG.MAX_I, args.max_current)

    if args.max_voltage is not None:
        hv.set_parameter(A7585D_REG.MAX_V, args.max_voltage)

    if args.temp_coef is not None:
        hv.set_parameter(A7585D_REG.T_COEF_SIPM, args.temp_coef)

    if args.ramp_speed is not None:
        hv.set_parameter(A7585D_REG.RAMP, args.ramp_speed)

    if args.current_range is not None:
        hv.set_parameter(A7585D_REG.CURRENT_RANGE, args.current_range)

    if args.enable_pi is not None:
        hv.set_parameter(A7585D_REG.ENABLE_PI, args.enable_pi)

    if args.monitor:
        if args.poll_mode == 'continuous':
            while True:
                print("V: " + str(hv.get_parameter(A7585D_REG.MON_VOUT)) + " I: " + str(hv.get_parameter(A7585D_REG.MON_IOUT)))
                time.sleep(0.1)
        else:
            print("V: " + str(hv.get_parameter(A7585D_REG.MON_VOUT)) + " I: " + str(hv.get_parameter(A7585D_REG.MON_IOUT)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A7585D HV Control Utility')
    parser.add_argument('--port', type=str, required=True, help='Serial port')
    parser.add_argument('--power-on', type=int, choices=[0, 1], help='Power on HV')
    parser.add_argument('--control-mode', type=int, choices=[0, 1, 2], help='Control mode')
    parser.add_argument('--voltage-target', type=float, help='Voltage target')
    parser.add_argument('--max-current', type=int, help='Max current')
    parser.add_argument('--max-voltage', type=int, help='Max voltage')
    parser.add_argument('--temp-coef', type=int, help='SiPM temperature coefficient')
    parser.add_argument('--ramp-speed', type=int, help='Ramp speed')
    parser.add_argument('--current-range', type=int, choices=[0, 1, 2], help='Current range')
    parser.add_argument('--enable-pi', type=int, choices=[0, 1], help='Enable PI controller')
    parser.add_argument('--poll-mode', type=str, default='one-shot', choices=['one-shot', 'continuous'], help='Reading mode: one-shot or continuous (default: one-shot)')
    parser.add_argument('--monitor', action='store_true', help='Enable monitoring of HV output')
    
    args = parser.parse_args()
    main(args)
