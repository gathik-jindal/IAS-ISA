import linecache
import sys
from time import sleep

NOTHING = '0'*8 + ' ' + '0'*12
HALT = '11111111'
NOP = '10000000'
LOAD = '00000001'
LOADNeg = '00000010'
LOADMod = '00000011'
LOADNegMod = '00000100'                 # LOAD -|M(X)|
ADD = '00000101'
SUB = '00000110'
ADDMod = '00000111'
SUBMod = '00001000'
LOADMQM = '00001001'                    # LOAD MQ,M(X)
LOADMQ = '00001010'
MUL = '00001011'
DIV = '00001100'
JUMPl = '00001101'                      # JUMP M(X,0:19)
JUMPr = '00001110'                      # JUMP M(X,20:39)
JUMPlIfG = '00001111'                   # JUMP+ M(X,0:19)
JUMPrIfG = '00010000'                   # JUMP+ M(X,20:39)
JUMPlIfGG = '00011000'                  # JUMP++ M(X,0:19)
JUMPrIfGG = '00011001'                  # JUMP++ M(X,20:39)
STORl = '00010010'                      # STOR M(X,8:19)
STORr = '00010011'                      # STOR M(X,28:39)
LSH = '00010100'
RSH = '00010101'
STOR = '00100001'


def checkType(*args) -> bool:
    """
    Checks the type. It can take any number of parameters (tuples).
    Parameters are given as:
    (obj, type), (obj, type) .....
    """
    for x in args:
        if (x[0] == None or not isinstance(x[0], x[1])):
            return False

    return True


def convertToBin(num1: int, b=12) -> str:
    """
    Converts any numerical representation to bin.
    Currently only supports binary.

    TODO: Need to add functionality for more numeral systems. Like 0x, o.
    """
    n = bin(abs(num1))[2:]

    number = '0'*(b-len(n)-1) + n
    if num1 < 0:
        number = '1' + number
    else:
        number = '0' + number

    return number


def convertToInt(word: str, mod=False) -> int:
    """
    Converts the given word to its integer reperesntation.
    """
    val = int(word[1:], 2)
    if word[0] == '1' and not mod:
        val *= -1

    return val


class MainMemory:
    def __init__(self, inputFileName: str):
        self.__inputFileName = inputFileName

    def getWord(self, lineNumber: int) -> str:
        """
        Gets the word from that Memory address. If the Memeory address is a string it is considered to be a binary number.
        """
        if checkType((lineNumber, str)):
            lineNumber = convertToInt(lineNumber)

        linecache.checkcache(self.__inputFileName)
        line = linecache.getline(self.__inputFileName,
                                 lineNumber).rstrip("\n")

        if line == '':
            line = '0'*40

        return line

    def replaceMemoryAddr(self, lineNumber: int, memAddr: str, leftOrRight: int) -> None:
        """
        Replaces memory address with the memAddr given. If it is in integer it is converted to binary.
        If leftOrRight = 1, then the left address is replaced, else the right one is replaced
        """

        if leftOrRight == 0:
            leftOrRight = -1
        else:
            leftOrRight = 1

        if checkType((memAddr, int)):
            memAddr = convertToBin(memAddr)

        with open(self.__inputFileName, 'r') as fh:
            lines = fh.readlines()

        lineNumber -= 1
        line = lines[lineNumber].strip(" \n").split()
        line[leftOrRight] = memAddr
        lines[lineNumber] = " ".join(line) + '\n'

        with open(self.__inputFileName, 'w+') as fh:
            fh.writelines(lines)

    def writeAtMem(self, lineNumber: int, word: str) -> None:
        """
        Replaces an entire word in memory with given word.
        """
        with open(self.__inputFileName, 'r') as fh:
            lines = fh.readlines()

        if len(lines) < lineNumber:
            for x in range(lineNumber - len(lines)):
                lines.append('\n')
        lines[lineNumber-1] = word + '\n'

        with open(self.__inputFileName, 'w+') as fh:
            fh.writelines(lines)


class ALU:
    def __init__(self):
        self.__ACval = convertToBin(0, 40)
        self.__MQval = convertToBin(0, 40)

    def putAC(self, word) -> None:
        """
        Puts the value in AC.
        """
        self.__ACval = word

    def putMQ(self, word) -> None:
        """
        Puts the value in MQ.
        """
        self.__MQval = word

    def getAC(self) -> str:
        """
        Returns value of AC.
        """
        return self.__ACval

    def getMQ(self) -> str:
        """
        Returns value of MQ.
        """
        return self.__MQval

    def mq(self) -> None:
        """
        Does the LOAD MQ operation.
        """
        self.__ACval = self.__MQval

    def lsh(self) -> None:
        """
        Does the LSH operation.
        """
        self.__ACval = convertToBin(int(self.__ACval, 2) * 2)

    def rsh(self) -> None:
        """
        Does the RSH operation.
        """
        self.__ACval = convertToBin(int(self.__ACval, 2) / 2)

    def add(self, word: str, mod=False) -> None:
        """
        Does the ADD operation. mod is set to false by default.
        """

        ac = convertToInt(word, mod)
        val = convertToInt(self.__ACval)
        val += ac
        self.__ACval = convertToBin(val, 40)

    def sub(self, word: str, mod=False) -> None:
        """
        Does the SUB operation. mod is set to false by default.
        """

        word = convertToInt(word, mod)
        ac = convertToInt(self.__ACval)
        ac -= word
        self.__ACval = convertToBin(ac, 40)

    def mul(self, word: str) -> None:
        """
        Does the MUL operation.
        """

        word = convertToInt(word)
        val = convertToInt(self.__ACval)
        val *= word
        val = convertToBin(val, 80)
        self.__MQval = val[-40:]
        self.__ACval = val[:-40]

    def div(self, word: str) -> None:
        """
        Does the DIV operation.
        """

        word = convertToInt(word)
        ac = convertToInt(self.__ACval)
        quo = int(ac/word)
        rem = ac % word
        self.__MQval = convertToBin(quo, 40)
        self.__ACval = convertToBin(rem, 40)


class MBR:
    def __init__(self):
        self.__value = NOTHING + ' ' + NOTHING

    def put(self, value: str) -> None:
        """
        Stores the value in MBR.
        """
        self.__value = value

    def get(self) -> str:
        """
        Gets the value in MBR.
        """
        return self.__value

    def getri(self) -> str:
        """
        Returns the right instruction.
        """
        ret = self.__value.split()
        ret = " ".join(ret[2:])
        return ret

    def getli(self) -> str:
        """
        Returns the left instruction.
        """
        ret = self.__value.split()
        ret = " ".join(ret[:2])
        return ret


class IBR:
    def __init__(self):
        self.__value = NOTHING

    def put(self, word: str) -> None:
        """
        Puts an instruciton in the IBR.
        """
        self.__value = word

    def get(self) -> str:
        """
        Gets the entire word stored in IBR.
        """
        return self.__value

    def getOpCode(self) -> str:
        """
        Gets the Opcode stored in IBR.
        """
        return self.__value.split(" ")[0]

    def getMemAddr(self) -> str:
        """
        Gets the memeory address stored in IBR.
        """
        return self.__value.split(" ")[1]

    def isEmpty(self) -> bool:
        """
        Checks if the IBR empty.
        """
        if self.__value == NOTHING:
            return True
        return False

    def clear(self) -> None:
        """
        Clears the IBR.
        """
        self.__value = NOTHING


class ProgramControlUnit:
    def __init__(self, mm: MainMemory, alu: ALU, PC=1):
        self.__IR = convertToBin(0, 8)
        self.__MAR = convertToBin(0, 12)
        self.__PC = convertToBin(PC, 12)
        self.__IBR = IBR()
        self.__MBR = MBR()
        self.__MainMemory = mm
        self.__ALU = alu
        self.flag = True  # only for jumps, False when we need to right jump

    def __decodeAndExecute(self) -> None:
        """
        Decodes and executes the processor.
        """

        if self.__IR == HALT:
            sys.exit(1)

        if self.__IR == NOP:
            return

        if self.__IR == LOAD:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.putAC(self.__MBR.get())
            return

        if self.__IR == LOADNeg:
            self.__MBR.put(
                convertToBin(-convertToInt(self.__MainMemory.getWord(convertToInt(self.__MAR)))))
            self.__ALU.putAC(self.__MBR.get())
            return

        if self.__IR == LOADMod:
            self.__MBR.put(convertToBin(
                abs(convertToInt(self.__MainMemory.getWord(convertToInt(self.__MAR))))))
            self.__ALU.putAC(self.__MBR.get())
            return

        if self.__IR == LOADNegMod:
            self.__MBR.put(
                convertToBin(-abs(convertToInt(self.__MainMemory.getWord(convertToInt(self.__MAR))))))
            self.__ALU.putAC(self.__MBR.get())
            return

        if self.__IR == ADD:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.add(self.__MBR.get())
            return

        if self.__IR == SUB:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.sub(self.__MBR.get())
            return

        if self.__IR == ADDMod:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.add(self.__MBR.get(), mod=True)
            return

        if self.__IR == SUBMod:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.sub(self.__MBR.get(), mod=True)
            return

        if self.__IR == LOADMQM:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.putMQ(word)
            return

        if self.__IR == LOADMQ:
            self.__ALU.mq()
            return

        if self.__IR == MUL:
            self.__MBR.put(self.__MainMemory.getWord(convertToInt(self.__MAR)))
            self.__ALU.mul(self.__MBR.get())
            return

        if self.__IR == DIV:
            word = self.__MainMemory.getWord(convertToInt(self.__MAR))
            self.__ALU.div(word)
            return

        if self.__IR == JUMPl:
            self.__IBR.clear()
            self.__PC = self.__MAR

        if self.__IR == JUMPr:
            self.__IBR.clear()
            self.__PC = self.__MAR
            self.flag = False

        if self.__IR == JUMPlIfG:
            if convertToInt(self.__ALU.getAC()) >= 0:
                self.__IBR.clear()
                self.__PC = self.__MAR

        if self.__IR == JUMPrIfG:
            if convertToInt(self.__ALU.getAC()) >= 0:
                self.__IBR.clear()
                self.__PC = self.__MAR
                self.flag = False

        if self.__IR == JUMPlIfGG:
            if convertToInt(self.__ALU.getAC()) > 0:
                self.__IBR.clear()
                self.__PC = self.__MAR

        if self.__IR == JUMPrIfGG:
            if convertToInt(self.__ALU.getAC()) > 0:
                self.__IBR.clear()
                self.__PC = self.__MAR
                self.flag = False

        if self.__IR == STOR:
            self.__MBR.put(self.__ALU.getAC())
            self.__MainMemory.writeAtMem(
                convertToInt(self.__MAR), self.__MBR.get())

        if self.__IR == STORr:
            self.__MBR.put(self.__ALU.getAC()[-12:])
            self.__MainMemory.replaceMemoryAddr(
                convertToInt(self.__MAR), self.__MBR.get(), 0)
            return

        if self.__IR == STORl:
            self.__MBR.put(self.__ALU.getAC()[-12:])
            self.__MainMemory.replaceMemoryAddr(
                convertToInt(self.__MAR), self.__MBR.get(), 1)
            return

        if self.__IR == LSH:
            self.__ALU.lsh()
            return

        if self.__IR == RSH:
            self.__ALU.rsh()
            return
    
    def __ForBubbleSort(self) -> None:
        for x in range(37, convertToInt(self.__MainMemory.getWord(35))):
                print(f"{convertToInt(self.__MainMemory.getWord(x))} ")
        print(f"Swap: {convertToInt(self.__MainMemory.getWord(31))}")
        print(f"Location of starting of array: {
              convertToInt(self.__MainMemory.getWord(32))}")
        print(f"Value of i: {convertToInt(self.__MainMemory.getWord(33))}")
        print(
            f"Value of i+1: {convertToInt(self.__MainMemory.getWord(34))}")
        print(f"Value of N: {convertToInt(self.__MainMemory.getWord(35))}")
        print(
            f"Value of N-2: {convertToInt(self.__MainMemory.getWord(36))}")
        print(f"PC: {convertToInt(self.__PC)}")
    
    def __print(self) -> None:
        print()
        print(f'\033[1;31;50m IR -> \033[0;0m', end="")
        print(f'\033[4;31;50m {self.__IR} ({convertToInt(self.__IR)}) \033[0;0m')
        print(f'\033[1;32;50m MAR -> \033[0;0m', end="")
        print(f'\033[4;32;50m {self.__MAR} ({convertToInt(self.__MAR)}) \033[0;0m')
        print(f'\033[1;33;50m MBR -> \033[0;0m', end="")
        print(f'\033[4;33;50m {self.__MBR.get()} \033[0;0m')
        print(f'\033[1;34;50m IBR -> \033[0;0m', end="")
        print(f'\033[4;34;50m {self.__IBR.get()} \033[0;0m')
        print(f'\033[1;35;50m AC ->  \033[0;0m', end="")
        print(f'\033[4;35;50m {self.__ALU.getAC()} ({convertToInt(self.__ALU.getAC())}) \033[0;0m')
        print(f'\033[1;36;50m MQ -> \033[0;0m', end="")
        print(f'\033[4;36;50m {self.__ALU.getMQ()} ({convertToInt(self.__ALU.getMQ())}) \033[0;0m')
        print(f'\033[1;37;50m PC -> \033[0;0m', end="")
        print(f'\033[4;37;50m {self.__PC} ({convertToInt(self.__PC)}) \033[0;0m')
        print()

    def run(self) -> None:
        """
        Runs the processor.
        """
        counter = 0
        while True:

            if (convertToInt(self.__PC) == 19):
                print("hi")

            if self.__IBR.isEmpty() and self.flag:

                self.__MAR = self.__PC

                self.__MBR.put(self.__MainMemory.getWord(self.__MAR))

                if self.__MBR.getli().split()[0] != NOP:

                    self.__IBR.put(self.__MBR.getri())
                    self.__IR, self.__MAR = self.__MBR.getli().split()

                    self.__decodeAndExecute()

                else:

                    self.__IBR.put(self.__MBR.getri())
                    self.__IR = self.__IBR.getOpCode()
                    self.__MAR = self.__IBR.getMemAddr()
                    self.__PC = convertToBin(convertToInt(self.__PC) + 1)

                    self.__decodeAndExecute()

                    self.__IBR.clear()

            elif self.flag:

                self.__IR, self.__MAR = self.__IBR.getOpCode(), self.__IBR.getMemAddr()

                self.__PC = convertToBin(convertToInt(self.__PC) + 1)

                self.__decodeAndExecute()

                self.__IBR.clear()

            else:  # when the instruciton is executed due to a jump right

                self.__MAR = self.__PC
                self.__MBR.put(self.__MainMemory.getWord(
                    convertToInt(self.__MAR)))

                self.__IBR.put(self.__MBR.getri())
                self.__IR = self.__IBR.getOpCode()
                self.__MAR = self.__IBR.getMemAddr()
                self.__IBR.clear()

                self.__decodeAndExecute()

                self.__PC = convertToBin(convertToInt(self.__PC) + 1)

                self.flag = True

            # sleep(0.5)
            self.__print()
            # self.__ForBubbleSort()


nameOfFile = "MatMul"
CPU = ProgramControlUnit(MainMemory(
    "object files/" + nameOfFile + ".obj"), ALU(), 1)
CPU.run()
