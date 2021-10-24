CC=gcc
CFLAGS=-std=gnu99 -pedantic -Wall -Wextra -g
LIBS=-lpthread
XLOGIN=xmacho12

all: proj2

proj2: proj2.o
	$(CC) $(CFLAGS) $^ -o $@ $(LIBS)

test: proj2
	./proj2 5 4 100 100
	cat proj2.out

zip:
	zip $(XLOGIN).zip *.c *.h Makefile

clean:
	rm -f *.o $(XLOGIN).zip
