#!/bin/python3

# Tests for project 2 from IOS course
# Author: Ondrej Mach
# Date: 17.04.2021

import os
import sys
from enum import Enum

class Arguments:
    def __init__(self, NE=5, NR=5, TE=100, TR=100):
        self.NE = NE
        self.NR = NR
        self.TE = TE
        self.TR = TR


class Santa:
    class State(Enum):
        NOT_STARTED = 0
        SLEEPING = 1
        HELPING_ELVES = 2
        HITCHING_RDS = 3
        GONE = 4

    def __init__(self):
        self.state = self.State.NOT_STARTED

    def end(self):
        if self.state != self.State.GONE:
            print(f'Santa ended in state {self.state}')
            raise

    def read(self, text):
        if self.state == self.State.NOT_STARTED:
            if text == 'going to sleep':
                self.state = self.State.SLEEPING
            else:
                print(f'Santa in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.SLEEPING:
            if text == 'helping elves':
                self.state = self.State.HELPING_ELVES
            elif text == 'closing workshop':
                self.state = self.State.HITCHING_RDS
            else:
                print(f'Santa in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.HELPING_ELVES:
            if text == 'going to sleep':
                self.state = self.State.SLEEPING
            else:
                print(f'Santa in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.HITCHING_RDS:
            if text == 'Christmas started':
                self.state = self.State.GONE
            else:
                print(f'Santa in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.GONE:
            print(f'Santa in state {self.state} cannot do {text}')
            raise


class Elf:
    class State(Enum):
        NOT_STARTED = 0
        WORKING_ALONE = 1
        AWAITING_HELP = 2
        ON_VACATION = 3

    def __init__(self, ID=0):
        self.state = self.State.NOT_STARTED
        self.ID = ID

    def end(self):
        if self.state != self.State.ON_VACATION:
            print(f'Elf {self.ID} ended in state {self.state}')
            raise

    def read(self, text):
        if self.state == self.State.NOT_STARTED:
            if text == 'started':
                self.state = self.State.WORKING_ALONE
            else:
                print(f'Elf in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.WORKING_ALONE:
            if text == 'need help':
                self.state = self.State.AWAITING_HELP
            elif text == 'taking holidays':
                self.state = self.State.ON_VACATION
            else:
                print(f'Elf in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.AWAITING_HELP:
            if text == 'get help':
                self.state = self.State.WORKING_ALONE
            elif text == 'taking holidays':
                self.state = self.State.ON_VACATION
            else:
                print(f'Elf in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.ON_VACATION:
            print(f'Elf in state {self.state} cannot do {text}')
            raise


class Reindeer:
    class State(Enum):
        NOT_STARTED = 0
        ON_VACATION = 1
        BACK_HOME = 2
        HITCHED = 3

    def __init__(self, ID=0):
        self.state = self.State.NOT_STARTED
        self.ID = ID

    def end(self):
        if self.state != self.State.HITCHED:
            print(f'Reindeer {self.ID} ended in state {self.state}')
            raise

    def read(self, text):
        if self.state == self.State.NOT_STARTED:
            if text == 'rstarted':
                self.state = self.State.ON_VACATION
            else:
                print(f'Reindeer in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.ON_VACATION:
            if text == 'return home':
                self.state = self.State.BACK_HOME
            else:
                print(f'Reindeer in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.BACK_HOME:
            if text == 'get hitched':
                self.state = self.State.HITCHED
            else:
                print(f'Reindeer in state {self.state} cannot do {text}')
                raise

        elif self.state == self.State.HITCHED:
            print(f'Reindeer in state {self.state} cannot do {text}')
            raise


class LineCounter:
    def __init__(self):
        self.expectedNumber = 1
        pass

    def read(self, num):
        if int(num) != self.expectedNumber:
            print(f'Expected line number {self.expectedNumber}')
            raise

        self.expectedNumber += 1

# things used for formatting
class fmt:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    DIM = '\e[2m'
    NOCOLOR = '\033[0m'
    TICK = '\u2713'
    CROSS = '\u2717'


def runSubject(args):
    cmd = f'./proj2 {args.NE} {args.NR} {args.TE} {args.TR}'
    ret = os.system(cmd)

    if ret != 0:
        print('Subject exited with error')
        raise


def analyzeFile(file, args):
    lc = LineCounter()
    santa = Santa()
    elves = [Elf(ID=i+1) for i in range(args.NE)]
    rds = [Reindeer(ID=i+1) for i in range(args.NR)]

    for line in file.readlines():
        lineList = line.split(':')
        lineNum, actor, action = [item.strip() for item in lineList]

        try:
            lc.read(lineNum)

            if actor == 'Santa':
                santa.read(action)

            elif actor.startswith('Elf'):
                elfID = int(actor.split()[1])
                elves[elfID - 1].read(action)

            elif actor.startswith('RD'):
                rdID = int(actor.split()[1])
                rds[rdID - 1].read(action)

            else:
                print(f'Wrong actor identifier: {actor}')
                raise

        except:
            print(f'Illegal operation on line {lineNum}:')
            print(line)
            raise

    # After all lines are read
    try:
        del santa
    except:
        raise

    for elf, ID in enumerate(elves):
        try:
            del elf
        except:
            print(f'Elf {ID} ended in wrong state')
            raise

    for rd, ID in enumerate(rds):
        try:
            del rd
        except:
            print(f'Reindeer {ID} ended in wrong state')
            raise



def main():
    args = Arguments(50, 5, 0, 500)

    try:
        while True:
            runSubject(args)

            with open('proj2.out', 'r') as file:
                analyzeFile(file, args)

    except Exception:
        print(fmt.RED + fmt.CROSS + ' Tests failed' + fmt.NOCOLOR)
        with open('exception.log', 'w') as outFile:
            outFile.write(Exception)
        return 1

    print(fmt.GREEN + fmt.TICK + ' Tests passed' + fmt.NOCOLOR)
    return 0

if __name__ == '__main__':
    sys.exit(main())







