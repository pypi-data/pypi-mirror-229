from ld_micro_vm_h import *
import Jetson.GPIO as GPIO
import time
import threading
from threading import Event
PLC_ISA = bytearray([0,3])
header = bytearray()
header.extend(map(ord, "PLC"))

GPIO_OUT = [29,31,32,33]
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
    def __init__ (self, plc_address):
        file_check, self.plc_object, self.cycle_time = self.load_program(plc_address)
        GPIO.setmode(GPIO.BOARD) 
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
                GPIO.output(GPIO_OUT[i], GPIO.HIGH)
                #print(GPIO_OUT[i] ,"high")
            else:
                GPIO.output(GPIO_OUT[i], GPIO.LOW)
                #print(GPIO_OUT[i], "low")
    
    def gpio_setup(self):
        GPIO.setup(GPIO_OUT, GPIO.OUT)
    
    def clear_inputs(self):
        for i in INPUT_BITS:
            self.plc_object.bits[i] = False

    def kill(self):
        self.event.set()
        self.thread.join()        
        GPIO.cleanup()
