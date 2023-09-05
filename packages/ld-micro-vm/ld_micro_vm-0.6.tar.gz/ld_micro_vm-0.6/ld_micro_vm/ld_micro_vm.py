import Jetson.GPIO as GPIO
import time
import threading
import sys
from threading import Event
PLC_ISA = bytearray([0,3])
header = bytearray()
header.extend(map(ord, "PLC"))
#Masks
PLC_BIT_LOCAL_OUT_MASK = 0xF
PLC_BIT_LOCAL_IN_MASK = 0xF00
PLC_BIT_MQTT_IN_MASK = 0xF000
PLC_BIT_MQTT_OUT_MASK = 0x00F0
PLC_BIT_LOOPS_MASK = 0xFFFF
PLC_BIT_RADIO_OUT_MASK = 0xFFFF
PLC_BIT_PIEZO_MASK = 0xFFFF
#Error Codes 
PLC_FILE_OK = 0 
PLC_FILE_NOT_FOUND = 1
PLC_FILE_ERROR = 2
PLC_UNKNOWN_INSTRUCTION = 3
PLC_PROGRAM_OVERRUN = 4
PLC_PROGRAM_END = 5

#File format constants 
ICS_MAX_PROGRAM_SIZE = 1024
FILE_HEADER_LENGTH = 4
FILE_FILE_NAME_LENGTH = 20
VERSION_COMMENT_LENGTH = 20
TOTAL_INTEGERS_ISA1 = 64
TOTAL_INTEGERS = 64		# Ready for Increased number of integers for 1 < ISA 
# We can only increase the number of integers if we modify the instruction set to allocate more bits to the integer addressing
TOTAL_BITS = 256
BIT_VAR_SIZE = 16
IO_USAGE_BITMAP_SIZE = 80		# + Piezo channels See "LAST_FREE_BIT" in 760685
IO_USAGE_BITMAP_SIZE_1 = 64		# Original io_usage_bitmap size	

IO_USAGE_VAR_BITS = 16
ICS_MAX_NAMES_SIZE = 255		# buffer is allocated with extra trailing character for null termination		
PLC_NAMES_DELIMITER = ','		# Comma separated	

# Predefined bits
# Word # 0
IO_BIT_DETECTION  = 0   # INPUT There are vehicle details from the Q in the relevant integers
IO_BIT_BUTTON = 1		# INPUT The button has been pressed
IO_BIT_ENERGY_SAVING = 2		# INPUT ENergy Saving Mode in operation
IO_BIT_TIMEOUT = 3		# INPUT - Remote Input has timed-out
IO_BIT_FAULT = 4		# OUTPUT Fault Status
IO_BIT_SEND	= 5		# OUTPUT Trigger to SEND MQTT status message
IO_BIT_SPARE1 = 6
IO_BIT_SPARE2 = 7	 
#
IO_BIT_IN0 = 8
IO_BIT_IN1 = 9
IO_BIT_IN2 = 10
IO_BIT_IN3 = 11
IO_BIT_MQTT_IN0 = 12
IO_BIT_MQTT_IN1 = 13
IO_BIT_MQTT_IN2 = 14
IO_BIT_MQTT_IN3 = 15
#
# Word  # 1
IO_BIT_LOOP1 = 16
IO_BIT_LOOP2 = 17
IO_BIT_LOOP3 = 18
IO_BIT_LOOP4 = 19
IO_BIT_LOOP5 = 20
IO_BIT_LOOP6 = 21
IO_BIT_LOOP7 = 22
IO_BIT_LOOP8 = 23
IO_BIT_LOOP9 = 24
IO_BIT_LOOP10 = 25
IO_BIT_LOOP11 = 26
IO_BIT_LOOP12 = 27
IO_BIT_LOOP13 = 28
IO_BIT_LOOP14 = 29
IO_BIT_LOOP15 = 30
IO_BIT_LOOP16 = 31
#
# Word # 2
IO_BIT_OUT0 = 32
IO_BIT_OUT1 = 33
IO_BIT_OUT2 = 34
IO_BIT_OUT3 = 35
IO_BIT_MQTT_OUT0 = 36
IO_BIT_MQTT_OUT1 = 37
IO_BIT_MQTT_OUT2 = 38
IO_BIT_MQTT_OUT3 = 39
#
IO_BIT_STATUS1 = 40			# Keep in sync with NUM_PLC_STATUS_BITS
IO_BIT_STATUS2 = 41
IO_BIT_STATUS3 = 42
IO_BIT_STATUS4 = 43
IO_BIT_STATUS5 = 44
IO_BIT_STATUS6 = 45
IO_BIT_STATUS7 = 46
IO_BIT_STATUS8 = 47
#
# Word # 3
IO_BIT_RADIO1_OUT0 = 48
IO_BIT_RADIO2_OUT0 = 56
#
# Word # 4
IO_BIT_PIEZO = 64

# IO BIT constants
PLC_BIT_LOCAL_OUT = 2		# word address
PLC_BIT_LOCAL_IN = 0		# word address
PLC_BIT_LOCAL_IN_SHIFT = 8
NUM_GPO_BITS = 4
NUM_GPI_BITS = 4
PLC_BIT_MQTT_IN = 0		# word address
PLC_BIT_MQTT_IN_SHIFT = 12
PLC_BIT_MQTT_OUT = 2		# word address
PLC_BIT_MQTT_OUT_SHIFT = 4
PLC_BIT_LOOPS = 1		# word address
PLC_BIT_RADIO_OUT = 3	# word address
PLC_BIT_PIEZO = 4
	
#Predefined integers
IO_INT_LANE = 0
IO_INT_DIRECTION = 1
IO_INT_SPEED = 2
IO_INT_LENGTH = 3
IO_INT_CLASS = 4
IO_INT_GAP = 5
IO_INT_GPM_PRM1 = 6
IO_INT_GPM_PRM2 = 7
IO_INT_GPM_PRM3 = 8
IO_INT_GPM_PRM4 = 9
IO_INT_GPM_PRM5 = 10
IO_INT_GPM_PRM6 = 11
IO_INT_GPM_PRM7= 12
IO_INT_GPM_PRM8 = 13,
IO_INT_TEMP_CC = 14,			
IO_INT_BATT_MV = 15,			
IO_INT_EXT_MV = 16,			
IO_INT_MINUTE = 17,			
IO_INT_STATUS1 = 18,			
IO_INT_STATUS2 = 19,
IO_INT_STATUS3 = 20,
IO_INT_STATUS4 = 21,
IO_INT_STATUS5 = 22,
IO_INT_STATUS6 = 23,
IO_INT_STATUS7 = 24,
IO_INT_STATUS8 = 25

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

PC_MASK  = 0x3FF

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
            #print("cycle number{:d} ".format(i))
            print("Loop", file=sys.stdout)
            self.lock.acquire()
            self.ld_run_program(self.plc_object)
            #print(self.plc_object.bits)
            #print(self.plc_object.integers)
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
                #print("NOP")
                pass
            elif instruction.OP_CODE == ICS.JUMP:
                program_counter = instruction.JUMP_ADDR
                #print("Jump")
                
            elif instruction.OP_CODE == ICS.JUMP_EQ:
                if(plc_program.integers[instruction.INT_A] == plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump Eq")
                
            elif instruction.OP_CODE == ICS.JUMP_NEQ:
                if(plc_program.integers[instruction.INT_A] != plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump NEq")
                
            elif instruction.OP_CODE == ICS.JUMP_GT:
                if(plc_program.integers[instruction.INT_A] > plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump GT")
                
            elif instruction.OP_CODE == ICS.JUMP_LEQ:
                if(plc_program.integers[instruction.INT_A] <= plc_program.integers[instruction.INT_B]):
                    program_counter =instruction.JUMP_ADDR                                                                                                                                                                                                                                                                                                 
                #print("Jump LEq")
                
            elif instruction.OP_CODE == ICS.JUMP_LT:
                if(plc_program.integers[instruction.INT_A] < plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump LT")
                
            elif instruction.OP_CODE == ICS.JUMP_GEQ:
                if(plc_program.integers[instruction.INT_A] >= plc_program.integers[instruction.INT_B]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jumpe GEq")
                
            elif instruction.OP_CODE == ICS.ADD:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] + plc_program.integers[instruction.INT_B]
                #print("Add")
                
            elif instruction.OP_CODE == ICS.SUB:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] - plc_program.integers[instruction.INT_B]
                #print("Sub")
                
            elif instruction.OP_CODE == ICS.MUL:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] * plc_program.integers[instruction.INT_B]
                #print("Mul")
                
            elif instruction.OP_CODE == ICS.DIV:
                if(plc_program.integers[instruction.INT_B] != 0):
                    plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] / plc_program.integers[instruction.INT_B]
                #print("Div")
                
            elif instruction.OP_CODE == ICS.MOD:
                if(plc_program.integers[instruction.INT_B] != 0):
                    plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] % plc_program.integers[instruction.INT_B]
                #print("Mod")
                
            elif instruction.OP_CODE == ICS.ADD_1:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] + 1
                #print("Add 1")
                
            elif instruction.OP_CODE == ICS.SUB_1:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] - 1
                #print("Sub 1")
                
            elif instruction.OP_CODE == ICS.NEG:
                plc_program.integers[instruction.INT_C] = 0 - plc_program.integers[instruction.INT_B]
                #print("Neg")
                
            elif instruction.OP_CODE == ICS.AND:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] & plc_program.integers[instruction.INT_B]
                #print("And")
                
            elif instruction.OP_CODE == ICS.OR:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] | plc_program.integers[instruction.INT_B]
                #print("Or")
                
            elif instruction.OP_CODE == ICS.XOR:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A] ^ plc_program.integers[instruction.INT_B]
                #print("Xor")
                
            elif instruction.OP_CODE == ICS.NOT:
                plc_program.integers[instruction.INT_C] = ~plc_program.integers[instruction.INT_A]
                #print("Not")
                
            elif instruction.OP_CODE == ICS.LOAD_LITERAL:
                plc_program.integers[instruction.INT_C] = instruction.LITERAL
                #print("Load Literal")
                
            elif instruction.OP_CODE == ICS.COPY_VARIABLE:
                plc_program.integers[instruction.INT_C] = plc_program.integers[instruction.INT_A]
                #print("Coppy Variable")
                
            elif instruction.OP_CODE == ICS.COPY_BIT:
                if (plc_program.bits[instruction.BIT_A]):
                    plc_program.bits[instruction.BIT_B] = True
                else:
                    plc_program.bits[instruction.BIT_B] = False
                #print("Copy bit")
                #print(instruction.BIT_A)
                #print(instruction.BIT_B)
                                   
            elif instruction.OP_CODE == ICS.JUMP_IF_BIT_CLEAR:
                if(not plc_program.bits[instruction.BIT_A]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump if bit clear")
                #print(instruction.BIT_A)
                
            elif instruction.OP_CODE == ICS.JUMP_IF_BIT_SET:
                if(plc_program.bits[instruction.BIT_A]):
                    program_counter = instruction.JUMP_ADDR
                #print("Jump if bit set")
                
            elif instruction.OP_CODE == ICS.CLEAR_BIT:
                plc_program.bits[instruction.BIT_B] = False
                #print("Clear bit")
                #print(instruction.BIT_B)
                
            elif instruction.OP_CODE == ICS.SET_BIT:
                plc_program.bits[instruction.BIT_B] = True
                                                
                #print("Set bit")
                #print(instruction.BIT_B)
                
            elif instruction.OP_CODE == ICS.END_OF_PROGRAM:
                #print("End")
                self.clear_inputs()
                return PLC_PROGRAM_END
            else:
                #print("Unknown")
                return PLC_UNKNOWN_INSTRUCTION
            self.gpio_functions(plc_program.bits)
        return PLC_PROGRAM_OVERRUN
    
    def gpio_functions(self, bits):
        for i in range(4):
            if(bits[IO_BIT_OUT0+i]):
                GPIO.output(self.GPIO_OUT[i], GPIO.HIGH)
                #print(self.GPIO_OUT[i] ,"high")
            else:
                GPIO.output(self.GPIO_OUT[i], GPIO.LOW)
                #print(self.GPIO_OUT[i], "low")
    
    def gpio_setup(self):
        GPIO.setup(self.GPIO_OUT, GPIO.OUT)
    
    def clear_inputs(self):
        for i in INPUT_BITS:
            self.plc_object.bits[i] = False

    def kill(self):
        self.event.set()
        self.thread.join()        
        GPIO.cleanup()
