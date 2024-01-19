import re
import linecache
import sys


class Assembler:
    def __init__(self, inputFileName, outputFileName):
        self.__inputFileName = inputFileName
        self.__outputFileName = outputFileName

    def __getOpCode(self, op: str, address="") -> str:
        """
        Returns the opcode.

        arguemnts:
            op: the instruction itself
            address: default is \"\".
            The address should be of form M(XXXX)
        """
        if (op == 'ADD' and address[0] == 'M'):
            return '00000101'

        elif (op == 'STOR' and (',' not in address)):
            return '00100001'

        elif (op == 'LOAD' and address[0:2] == 'M('):
            return '00000001'

        elif (op == 'LOAD' and address[0:2] == '-M'):
            return '00000010'

        elif (op == 'LOAD' and address[0] == '|'):
            return '00000011'

        elif (op == 'LOAD' and address[0:2] == '-|'):
            return '00000100'

        elif (op == 'LOAD' and address[:5] == 'MQ,M('):
            return '00001001'

        elif (op == 'LOAD' and address == 'MQ'):
            return '00001010'

        elif (op == 'ADD' and address[0] == '|'):
            return '00000111'

        elif (op == 'SUB' and address[0] == 'M'):
            return '00000110'

        elif (op == 'SUB' and address[0] == '|'):
            return '00001000'

        elif (op == 'DIV'):
            return '00001100'

        elif (op == 'LSH'):
            return '00010100'

        elif (op == 'RSH'):
            return '00010101'

        elif (op == 'JUMP+' and address[-6:-1] == ',0:19'):
            return '00001111'

        elif (op == 'JUMP+' and address[-7:-1] == ',20:39'):
            return '00010000'

        elif (op == 'JUMP' and address[-6:-1] == ',0:19'):
            return '00001101'

        elif (op == 'JUMP' and address[-7:-1] == ',20:39'):
            return '00001110'

        elif (op == 'MUL'):
            return '00001011'

        elif (op == 'STOR' and address[-6:-1] == ',8:19'):
            return '00010010'

        elif (op == 'STOR' and address[-7:-1] == ',28:39'):
            return '00010011'

        elif (op == 'HALT'):
            return '11111111'

        else:
            self.__printErrorAndExit(
                f"Error: Invalid Instruction at line {self.__lineNum} in the instruction \"{op}\".")

    def __printErrorAndExit(self, message: str) -> None:
        print(message)
        sys.exit(1)

    def __convertToBin(self, num: int) -> str:
        """
        Converts any numerical representation to bin.
        Currently only supports binary.

        TODO: Need to add functionality for more numeral systems. Like 0x, o.
        """
        n = bin(num)[2:]
        addr = '0'*(12-len(n)) + n
        return addr

    def __convertInstructionToBin(self, instr: str) -> str:
        """
        Converts the instruction to its binary equivalent.
        """
        pattern = "[0-9]+"

        instr = instr.split(" ")

        if len(instr) == 2:
            opcode = self.__getOpCode(instr[0], instr[1])
            num = re.findall(pattern, instr[1])
        else:
            opcode = self.__getOpCode(instr[0])
            num = 0

        if (not num):
            address = '000000000000'

        else:
            address = self.__convertToBin(int(num[0]))

        instruction = opcode + " " + address

        return instruction

    def __write(self, instr: str) -> None:
        """
        Writes the instruction into the object file.
        """
        self.__oFh.write(instr)

    def run(self):
        """
        Runs the actual assembler.
        """

        self.__lineNum = 1

        self.__oFh = open(self.__outputFileName, "w+")

        while True:
            line = linecache.getline(self.__inputFileName, self.__lineNum).rstrip("\n")
            if not line:
                break

            line = line.split('//')[0]
            line = line.split(';')

            if (len(line) == 2):
                instruction = self.__convertInstructionToBin(line[0].strip(" \n")) + " " + self.__convertInstructionToBin(line[1].strip(" \n"))

                self.__write(instruction + "\n")

            if (len(line) == 1):
                instruction = self.__convertInstructionToBin(line[0].strip(" \n"))

                self.__write(instruction + "\n")

            self.__lineNum += 1

        self.__oFh.close()


asm = Assembler("helloWorld.asm", "helloWorld.obj")
asm.run()