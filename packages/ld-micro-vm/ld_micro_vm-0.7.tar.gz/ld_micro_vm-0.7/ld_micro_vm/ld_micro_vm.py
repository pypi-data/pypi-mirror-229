import Jetson.GPIO as GPIO
import time
import threading
import sys
from threading import Event
PLC_ISA = bytearray([0,3])
header = bytearray()
header.extend(map(ord, "PLC"))

#Error Codes 
PLC_FILE_OK = 0 
PLC_FILE_NOT_FOUND = 1
PLC_FILE_ERROR = 2
PLC_UNKNOWN_INSTRUCTION = 3
PLC_PROGRAM_OVERRUN = 4
PLC_PROGRAM_END = 5

PC_MASK  = 0x3FF
ICS_MAX_PROGRAM_SIZE = 1024

#PLC class
class plc_t:
    header = []
    filename = []
    version = []
    isa = 0
    cycle_time = 0
    program_length = 0
    program = []
    integers = []
    bits = [False for i in range(256)]

#ICS Instructions 
class ICS:
	NOP = 0x00
	JUMP = 0x01
	JUMP_EQ = 0x02
	JUMP_NEQ = 0x03
	JUMP_GT = 0x04
	JUMP_LEQ = 0x05
	JUMP_LT = 0x06
	JUMP_GEQ = 0x07
	ADD = 0x08
	SUB = 0x09
	MUL = 0x0A
	DIV = 0x0B
	MOD  = 0x0C
	ADD_1  = 0x0D
	SUB_1 = 0x0E
	NEG = 0x0F
	SHL = 0x10
	ROL = 0x11
	SHR = 0x12
	ROR = 0x13
	SR0 = 0x14
	AND = 0x18
	OR = 0x19
	XOR = 0x1A
	NOT = 0x1B
	LOAD_LITERAL = 0x1C
	COPY_VARIABLE = 0x1D
	COPY_BIT = 0x1E
	JUMP_IF_BIT_CLEAR = 0x20
	JUMP_IF_BIT_SET = 0x21
	CLEAR_BIT = 0x22
	SET_BIT = 0x23
	END_OF_PROGRAM = 0xFF
INPUT_BITS = [8,9,10,11]
           
class instruction_frame:                                   
    def __init__(self, instruction):
        self.OP_CODE = (instruction >> 24) & 0xFF
        self.JUMP_ADDR = ((instruction >> 12) & 0x03FF) +1
        self.INT_A = instruction & 0x3F
        self.INT_B = (instruction>>6) & 0x3F
        self.INT_C = (instruction>>16) & 0x3F
        self.BIT_A = instruction & 0xFF
        self.BIT_B = (instruction>>8) & 0xFF
        self.LITERAL = instruction & 0xFFFF
    
class ld_micro_vm:
    def __init__ (self, plc_address, GPIO_OUT = [29,31,32,33]):
        file_check, self.plc_object, self.cycle_time = self.load_program(plc_address)
        GPIO.setmode(GPIO.BOARD) 
        self.GPIO_OUT = GPIO_OUT
        self.gpio_setup()
        self.event = Event()
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()    
    def run(self):
        while True:
            now = time.time()
            #print("Loop", file=sys.stdout)
            self.lock.acquire()
            self.ld_run_program(self.plc_object)
            self.lock.release()
            if self.event.is_set():
                break
            elapsed = time.time() - now
            time.sleep(self.cycle_time - elapsed)
    def load_program(self,address):
        fp = open(address, 'rb')
        ba = bytearray(fp.read())
        fp.close()
        plc_program = plc_t()
        plc_program.header = ba[0:3]
        if plc_program.header != header:
            return PLC_FILE_ERROR, plc_program, 0
        plc_program.filename = ba[4:24]
        plc_program.version = ba[24:44]
        plc_program.isa = ba[44:46]
        if plc_program.isa != PLC_ISA:
            return PLC_FILE_ERROR, plc_program, 0
        plc_program.cycle_time = ba[46:48]
        cycle_time = (16*ba[46] + ba[47])*0.001
        plc_program.program_length = (ba[48]<<8)+ba[49]
        if(plc_program.program_length > ICS_MAX_PROGRAM_SIZE):
            print ( PLC_FILE_ERROR )
        plc_program_temp = ba[50:50+plc_program.program_length*4]
        k = 0
        c = 0
        for i in plc_program_temp:
            c += 1
            k <<= 8
            k += i
            if c >= 4:
                c = 0
                plc_program.program.append(k)
                k = 0
        plc_int_temp = ba[50+plc_program.program_length*4:50+plc_program.program_length*4 + 128]
        k = 0
        c = 0
        for i in plc_int_temp:
            c += 1
            k <<= 8
            k += i
            if c >= 2:
                c = 0
                plc_program.integers.append(k)
                k = 0
        return 0, plc_program, cycle_time
    def ld_run_program(self, plc_program):
        program_counter = 0
        cycle_watchdog = plc_program.program_length
        while cycle_watchdog > 0:
            cycle_watchdog -= 1
            instruction = instruction_frame(plc_program.program[program_counter & PC_MASK])
            program_counter +=1
            if instruction.OP_CODE ==  ICS.NOP:
                pass
            elif instruction.OP_CODE == ICS.JUMP:
                program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_EQ:
                if(plc_program.integers[instruction.INT_A] == plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_NEQ:
                if(plc_program.integers[instruction.INT_A] != plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_GT:
                if(plc_program.integers[instruction.INT_A] > plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_LEQ:
                if(plc_program.integers[instruction.INT_A] <= plc_program.integers[instruction.INT_B]):
                    program_counter =instruction.JUMP_ADDR                                                                                                                                                                                                                                                                                                 
                
            elif instruction.OP_CODE == ICS.JUMP_LT:
                if(plc_program.integers[instruction.INT_A] < plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_GEQ:
                if(plc_program.integers[instruction.INT_A] >= plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.ADD:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] + plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.SUB:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] - plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.MUL:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] * plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.DIV:
                if(plc_program.integers[instruction.INT_B] != 0):
                    plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] / plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.MOD:
                if(plc_program.integers[instruction.INT_B] != 0):
                    plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] % plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.ADD_1:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] + 1
                
            elif instruction.OP_CODE == ICS.SUB_1:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] - 1
                
            elif instruction.OP_CODE == ICS.NEG:
                plc_program.integers[instruction.INT_C] = 0 - plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.AND:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] & plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.OR:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] | plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.XOR:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] ^ plc_program.integers[instruction.INT_B]
                
            elif instruction.OP_CODE == ICS.NOT:
                plc_program.integers[instruction.INT_C] = ~plc_program.integers[instruction.INT_A]
                
            elif instruction.OP_CODE == ICS.LOAD_LITERAL:
                plc_program.integers[instruction.INT_C] = instruction.LITERAL
                
            elif instruction.OP_CODE == ICS.COPY_VARIABLE:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A]
                
            elif instruction.OP_CODE == ICS.COPY_BIT:
                if (plc_program.bits[instruction.BIT_A]):
                    plc_program.bits[instruction.BIT_B] = True
                else:
                    plc_program.bits[instruction.BIT_B] = False
                                   
            elif instruction.OP_CODE == ICS.JUMP_IF_BIT_CLEAR:
                if(not plc_program.bits[instruction.BIT_A]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.JUMP_IF_BIT_SET:
                if(plc_program.bits[instruction.BIT_A]):
                    program_counter = instruction.JUMP_ADDR
                
            elif instruction.OP_CODE == ICS.CLEAR_BIT:
                plc_program.bits[instruction.BIT_B] = False
                
            elif instruction.OP_CODE == ICS.SET_BIT:
                plc_program.bits[instruction.BIT_B] = True
                
            elif instruction.OP_CODE == ICS.END_OF_PROGRAM:
                self.clear_inputs()
                return PLC_PROGRAM_END
            else:
                return PLC_UNKNOWN_INSTRUCTION
            self.gpio_functions(plc_program.bits)
        return PLC_PROGRAM_OVERRUN
    
    def gpio_functions(self, bits):
        for i in range(4):
            if(bits[32+i]): #IO_BIT_OUT0 = 32
                GPIO.output(self.GPIO_OUT[i], GPIO.HIGH)
            else:
                GPIO.output(self.GPIO_OUT[i], GPIO.LOW)
    
    def gpio_setup(self):
        GPIO.setup(self.GPIO_OUT, GPIO.OUT)
    
    def clear_inputs(self):
        for i in INPUT_BITS:
            self.plc_object.bits[i] = False

    def kill(self):
        self.event.set()
        self.thread.join()        
        GPIO.cleanup()
