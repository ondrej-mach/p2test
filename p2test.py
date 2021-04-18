#!/bin/python3

# Tests for project 2 from IOS course
# Author: Ondrej Mach
# Date: 17.04.2021

import os
import sys
from enum import Enum
from time import perf_counter

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

class Elf:
    class State(Enum):
        NOT_STARTED = 0
        WORKING_ALONE = 1
        AWAITING_HELP = 2
        ON_VACATION = 3

    def __init__(self, ID=0):
        self.state = self.State.NOT_STARTED
        self.ID = ID

class Reindeer:
    class State(Enum):
        NOT_STARTED = 0
        ON_VACATION = 1
        BACK_HOME = 2
        HITCHED = 3

    def __init__(self, ID=0):
        self.state = self.State.NOT_STARTED
        self.ID = ID

class LineCounter:
    def __init__(self):
        self.expectedNumber = 1
        pass

    def read(self, num):
        if int(num) != self.expectedNumber:
            print(f'Expected line number {self.expectedNumber}')
            raise

        self.expectedNumber += 1


class Environment:
    def __init__(self, args):
        self.lineCounter = LineCounter()
        self.santa = Santa()
        self.elves = [Elf(ID=i+1) for i in range(args.NE)]
        self.rds = [Reindeer(ID=i+1) for i in range(args.NR)]

        # shared variables for checking
        self.args = args
        self.numElvesToHelp = 0
        self.reindeersHome = 0
        self.workshopOpen = True

    def end(self):
        # After all lines are read
        try:
            self.santaEnd(self.santa)
        except:
            raise

        for ID, elf in enumerate(self.elves):
            try:
                self.elfEnd(elf)
            except:
                print(f'Elf {ID} ended in wrong state')
                raise

        for ID, rd in enumerate(self.rds):
            try:
                self.rdEnd(rd)
            except:
                print(f'Reindeer {ID} ended in wrong state')
                raise

    def readLine(self, line):
        lineList = line.split(':')
        lineNum, actor, action = [item.strip() for item in lineList]

        self.lineCounter.read(lineNum)

        if actor == 'Santa':
            self.santaRead(self.santa, action)

        elif actor.startswith('Elf'):
            ID = int(actor.split()[1])
            self.elfRead(self.elves[ID-1], action)

        elif actor.startswith('RD'):
            ID = int(actor.split()[1])
            self.rdRead(self.rds[ID-1], action)

        else:
            print(f'Wrong actor identifier: {actor}')
            raise

    def santaEnd(self, santa):
        if santa.state != Santa.State.GONE:
            print(f'Santa ended in state {santa.state}')
            raise

    def santaRead(self, santa, text):
        if santa.state == Santa.State.NOT_STARTED:
            if text == 'going to sleep':
                if self.numElvesToHelp != 0:
                    print(f'There are still {self.numElvesToHelp} elves in workshop, that didn\'t get help')
                    raise
                santa.state = Santa.State.SLEEPING
            else:
                print(f'Santa in state {santa.state} cannot do {text}')
                raise

        elif santa.state == Santa.State.SLEEPING:
            if text == 'helping elves':
                if self.numElvesToHelp != 0:
                    print('Santa did not yet help all the elves in previous helping cycle (or helped more than 3)')
                    raise
                if self.reindeersHome == self.args.NR:
                    print('Santa cannot help elves, when all reindeers are home')
                    raise
                self.numElvesToHelp = 3
                santa.state = Santa.State.HELPING_ELVES
            elif text == 'closing workshop':
                if self.reindeersHome != self.args.NR:
                    print('Santa is closing workshop before all reindeers are home')
                    raise
                self.workshopOpen = False
                santa.state = Santa.State.HITCHING_RDS
            else:
                print(f'Santa in state {santa.state} cannot do {text}')
                raise

        elif santa.state == Santa.State.HELPING_ELVES:
            if text == 'going to sleep':
                if self.numElvesToHelp != 0:
                    print(f'Santa went to sleep, he still has {self.numElvesToHelp} elves in his workshop')
                    raise
                santa.state = Santa.State.SLEEPING
            else:
                print(f'Santa in state {santa.state} cannot do {text}')
                raise

        elif santa.state == Santa.State.HITCHING_RDS:
            if text == 'Christmas started':
                santa.state = Santa.State.GONE
            else:
                print(f'Santa in state {santa.state} cannot do {text}')
                raise

        elif santa.state == Santa.State.GONE:
            print(f'Santa in state {santa.state} cannot do {text}')
            raise


    def elfEnd(self, elf):
        if elf.state != Elf.State.ON_VACATION:
            print(f'Elf {elf.ID} ended in state {elf.state}')
            raise

    def elfRead(self, elf, text):
        if elf.state == Elf.State.NOT_STARTED:
            if text == 'started':
                elf.state = Elf.State.WORKING_ALONE
            else:
                print(f'Elf in state {elf.state} cannot do {text}')
                raise

        elif elf.state == Elf.State.WORKING_ALONE:
            if text == 'need help':
                elf.state = Elf.State.AWAITING_HELP
            else:
                print(f'Elf in state {elf.state} cannot do {text}')
                raise

        elif elf.state == Elf.State.AWAITING_HELP:
            if text == 'get help':
                if not self.workshopOpen:
                    print('Elf cannot get help after the workshop is closed')
                    raise

                self.numElvesToHelp -= 1
                elf.state = Elf.State.WORKING_ALONE
            elif text == 'taking holidays':
                if self.workshopOpen:
                    print('Elf cannot go on vacation before the workshop closes')
                    raise
                elf.state = Elf.State.ON_VACATION
            else:
                print(f'Elf in state {elf.state} cannot do {text}')
                raise

        elif elf.state == Elf.State.ON_VACATION:
            print(f'Elf in state {elf.state} cannot do {text}')
            raise



    def rdEnd(self, rd):
        if rd.state != Reindeer.State.HITCHED:
            print(f'Reindeer {rd.ID} ended in state {rd.state}')
            raise

    def rdRead(self, rd, text):
        if rd.state == Reindeer.State.NOT_STARTED:
            if text == 'rstarted':
                rd.state = Reindeer.State.ON_VACATION
            else:
                print(f'Reindeer in state {rd.state} cannot do {text}')
                raise

        elif rd.state == Reindeer.State.ON_VACATION:
            if text == 'return home':
                self.reindeersHome += 1
                rd.state = Reindeer.State.BACK_HOME
            else:
                print(f'Reindeer in state {rd.state} cannot do {text}')
                raise

        elif rd.state == Reindeer.State.BACK_HOME:
            if text == 'get hitched':
                if self.workshopOpen:
                    print('Workshop must be closed, when a reindeer gets hitched')
                    raise
                rd.state = Reindeer.State.HITCHED
            else:
                print(f'Reindeer in state {rd.state} cannot do {text}')
                raise

        elif rd.state == Reindeer.State.HITCHED:
            print(f'Reindeer in state {rd.state} cannot do {text}')
            raise


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
    # initialize the test environment with all the creattures
    env = Environment(args)

    for lineNumber, line in enumerate(file.readlines()):
        try:
            env.readLine(line)
        except:
            print(f'Illegal operation on line {lineNumber}:')
            print(line)
            raise


class Controller:
    def __init__(self, timeToRun=30, interval=5):
        self.printInterval = interval
        self.timeToRun = timeToRun
        self.startTime = perf_counter()
        self.lastStatusTime = self.startTime

    def programRunning(self):
        return perf_counter() < self.startTime + self.timeToRun


    def printStatus(self, numTest):
        if perf_counter() > self.lastStatusTime + self.printInterval:
            print(f'Current status: {numTest} tests have been run')
            self.lastStatusTime = perf_counter()


def main():
    cont = Controller()
    # change these in order to test with different settings
    args = Arguments(20, 5, 0, 50)
    # comment this line if you want to see the python exception
    sys.stderr = open('/dev/null', 'w')

    try:
        testNumber = 0 # only for logging
        while cont.programRunning():
            runSubject(args)

            with open('proj2.out', 'r') as file:
                analyzeFile(file, args)

            cont.printStatus(testNumber)
            testNumber += 1

    except:
        print(fmt.RED + fmt.CROSS + ' Tests failed' + fmt.NOCOLOR)
        return 1

    print(fmt.GREEN + fmt.TICK + ' Tests passed' + fmt.NOCOLOR)
    return 0

if __name__ == '__main__':
    sys.exit(main())
