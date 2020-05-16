"""CPU functionality."""

import sys

# op codes
LDI = 0b10000010 
HLT = 0b00000001
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

# flags
EF = 0b00000001
LF = 0b00000100
GF = 0b00000010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8 
        self.fl = 0 
        self.pointer = 7
        self.reg[self.pointer] = len(self.ram) - 1
        self.branchtable = {
            LDI: self.opcode_LDI,
            HLT: self.opcode_HLT,
            PRN: self.opcode_PRN,
            MUL: self.opcode_MUL,
            POP: self.opcode_POP,
            PUSH: self.opcode_PUSH,
            CALL: self.opcode_CALL,
            RET: self.opcode_RET,
            CMP: self.opcode_CMP,
            JMP: self.opcode_JMP,
            JNE: self.opcode_JNE,
            JEQ: self.opcode_JEQ
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        print(sys.argv)
        if len(sys.argv) != 2:
            print("Please enter proper file name")
            sys.exit(1)

        file = sys.argv[1]
        with open(file) as f:
            for line in f:
                comment_split = line.strip().split('#')
                num = comment_split[0].strip()
                if num == '':
                    continue
                instruction = int(num, 2)
                self.ram[address] = instruction
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == CMP:
            if self.reg[reg_a] < self.reg[reg_b]:
                # set the L flag to 1
                self.fl = LF
            elif self.reg[reg_a] < self.reg[reg_b]:
                # set the G flag to 1
                self.fl = GF
            else:
                # set the E flag to 1
                self.fl = EF
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address): # address == MAR: Memory Address Register
        value = self.ram[address]
        return value

    def ram_write(self, value, address): # value == MDR: Memory Data Register
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while True:
            ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)
            else:
                print(f"Instruction {ir} is unknown")
                sys.exit(1)
            
    def opcode_LDI(self, a, b):
        # set the value of a register to an int
        self.reg[a] = b
        self.pc += 3  

    def opcode_HLT(self, a, b):
        sys.exit(0)

    def opcode_PRN(self, a, b):
        # print to the console the decimal int value stored in given register
        num = self.reg[a]
        print(num)
        self.pc += 2
    
    def opcode_MUL(self, a, b):
        ir = self.ram[self.pc]
        x = self.branchtable[ir]
        self.alu(x, a, b)
        self.pc += 3

    def opcode_POP(self, a, b):
        # pop value of stack at pointer location
        value = self.ram[self.reg[self.pointer]]
        register = self.ram[self.pc + 1]
        # store value in given register
        self.reg[register] = value
        # increment the stack pointer
        self.reg[self.pointer] += 1
        self.pc += 2 

    def opcode_PUSH(self, a, b):
        register = self.ram[self.pc + 1]
        # decrement the stack pointer
        self.reg[self.pointer] -= 1
        # read the next value for register location
        reg_value = self.reg[register]
        # add the value from that register and add to stack
        self.ram[self.reg[self.pointer]] = reg_value
        self.pc += 2
    
    def opcode_CALL(self, a, b):
        # store the next line to execute on the stack
        # return this line after the subroutine 
        val = self.pc + 2
        register = self.ram[self.pc + 1]
        sub_address = self.reg[register]

        self.reg[self.pointer] -= 1
        self.ram[self.reg[self.pointer]] = val
        # self.ram_write(val, self.reg[self.pointer])
        # self.ram[self.reg[self.pointer]] = self.pc + 2
        # read which register stores the next line passed w/call 
        # register = self.ram[self.pc + 1]
        # set the PC to the value in that register
        self.pc = sub_address

    def opcode_RET(self, a, b):
        # pop the current value off stack
        return_address = self.reg[self.pointer]
        # set the pc to that value
        self.pc = self.ram[return_address]
        # increment the stack pointer up the stack
        self.reg[self.pointer] += 1

    def opcode_CMP(self, a, b):
        x = CMP
        self.alu(x, a, b)
        self.pc += 3

    def opcode_JMP(self, a, b):
        # set the pc to the address stored in the given register
        self.pc = self.reg[a]
        
    def opcode_JEQ(self, a, b):
        # if equal flag is set (true), jump to address in given register
        if self.fl == EF:
            self.pc = self.reg[a]
        else:
            self.pc += 2

    def opcode_JNE(self, a, b):
        # if equal flag is clear (false), jump to address stored in given register
        if not self.fl == EF:
            self.pc = self.reg[a]
        else:
            self.pc += 2