#Helper functions - https://diablohorn.com
import gdb

class ContinueI(gdb.Command):
    """
    https://stackoverflow.com/a/31249378
    Continue until instruction with given opcode.

        ci OPCODE

    Example:

        ci callq
        ci mov
    """
    def __init__(self):
        super().__init__('ci', gdb.COMMAND_BREAKPOINTS, gdb.COMPLETE_NONE, False)

    def invoke(self, arg, from_tty):
        if arg == '':
            gdb.write('Argument missing.\n')
        else:
            thread = gdb.inferiors()[0].threads()[0]
            while thread.is_valid():
                gdb.execute('si', to_string=True)
                frame = gdb.selected_frame()
                arch = frame.architecture()
                pc = gdb.selected_frame().pc()
                instruction = arch.disassemble(pc)[0]['asm']
                if instruction.startswith(arg + ' '):
                    gdb.write(instruction + '\n')
                    break
ContinueI()

class PrintExecuteInterrupt(gdb.Command):
    """
    Print the interrupt calls like int 13
    Current execution must reside at int opcode
    """

    interrupt_mapping = {"0x13":"low level disk services"}
    interrupt_13_functions = {"0x41":"Test Whether Extensions Are Available","0x42":"Extended Read Sectors From Drive"}

    def __init__(self):
        super().__init__('pex_interrupt', gdb.COMMAND_DATA, gdb.COMPLETE_NONE, False)

    def invoke(self, arg, from_tty):
        frame = gdb.selected_frame()
        arch = frame.architecture()
        pc = frame.pc()
        instruction = arch.disassemble(pc)[0]['asm']
        if instruction.startswith('int '):
            interrupt_num = instruction.split(' ')[-1]
            if interrupt_num == '0x13':
                gdb.write('called {} - {}\n'.format(interrupt_num,self.interrupt_mapping[interrupt_num]))
                function_num = hex(gdb.parse_and_eval("$ah"))
                if function_num == '0x41':
                    gdb.write('Function {} - {}\n'.format(function_num,self.interrupt_13_functions[function_num]))
                    gdb.write('Function params: \n')
                    gdb.write('\tDL (drive index) {}\n'.format(hex(gdb.parse_and_eval("$dl"))))
                    gdb.write('\tBX (signature) {}\n'.format(hex(gdb.parse_and_eval("$ebx"))))
                    gdb.execute('ni',to_string=True)
                    gdb.write('Return values\n')
                    gdb.write('\tCF (clear if present) {}\n'.format(int(gdb.parse_and_eval("$eflags")) & 0x1))
                    gdb.write('\tAH (error|version) {}\n'.format(hex(gdb.parse_and_eval("$ah"))))
                    gdb.write('\tBX (signature) {}\n'.format(hex(gdb.parse_and_eval("$ebx"))))
                    gdb.write('\tCX (supported iface) {0:b}\n'.format(int(gdb.parse_and_eval("$cx"))))
                elif function_num == '0x42':
                    gdb.write('Function {} - {}\n'.format(function_num,self.interrupt_13_functions[function_num]))
                    gdb.write('Function params: \n')
                    gdb.write('\tDL (drive index) {}\n'.format(hex(gdb.parse_and_eval("$dl"))))
                    gdb.write('\tDS:SI (DAP) {}:{}\n'.format(hex(gdb.parse_and_eval("$ds")),hex(gdb.parse_and_eval("$si"))))
                    gdb.write('Print DAP structure using: \n')
                    gdb.write('\tset $dapstruct = *(struct dap *) ($ds*0x10+$si)\n')
                    gdb.write('\tp/x $dapstruct\n')
                    gdb.write('Print dap buffer (after executing interrupt) using: \n')
                    gdb.write('\tx/10x $dapstruct.buffer_segment*0x10+$dapstruct.buffer_offset\n')
                else:
                    gdb.write('Function number {} not implemented yet\n'.format(function_num))
            else:
                gdb.write('Interrupt number {} not implemented yet\n'.format(interrupt_num))
        else:
            gdb.write('Not paused at interrupt\n')
PrintExecuteInterrupt()


