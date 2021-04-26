# p2test
Testing script for project 2 from IOS course, VUT FIT

### Installation
You simply place the script into the same repository as your project.


### Running the script
```
python3 p2test
```
You can also try running the test with `--full` option.
```
python3 p2test --full
```
This adds a few test cases with more extreme arguments for your program.
This won't work on Merlin server, because you are limited to 50 processes.

If your executable hangs up or doesn't want to run, try running it yourself. 
The test shows you the arguments, that are currently tested.
```
./proj2 20 5 0 50
```

If you want to do more extensive testing, you can use ```-t``` or ```--time``` in seconds.
Please, do this only on your own computer, this might be quite demanding.
```
python3 p2test -t 120
```

If you want strictly no call of Santa helping elves after all reindeers are home then you can use ```-s``` or ```--strict```
```
python3 p2test -s
```

If you want to test if your program have any deadlocks then specify timeout time in seconds ```-to``` or ```--timeout```
In default tester will wait for program exit without any timeout.
```
python3 p2test -to 10
```

More info about parameter of tester with flag ```-h``` or ```--help```

### My tests fail
Here are some of the most common mistakes, that people often make:
- The project outputs to stdout. The tester can read only from file proj2.out, ignores everything else.

- The main process exits before all of its children have finished. This bug can manifest in weird ways, highly dependent on setup. For example, the test can finish analyzing file before the last elf goes on vacation.


### Limitations
What you have to test yourself:
```
limits of arguments
memory deallocation
random time generators
```

The test uses finite state machines to test each entity.
Most of the useful features are implemented.
Test runs for 30 seconds by default and does not yet have a simple way to change this behavior.

If you find any error, that is not detected, please contact me.

