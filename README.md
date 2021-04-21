# p2test
Testing script for project 2 from IOS course, VUT FIT

### Installation
You simply place the script into the same repository as your project.

### Running the script
```
./python3 p2test
```
You can also try running the test with `--full` option.
```
./python3 p2test --full
```
This adds a few test cases with more extreme arguments for your program.
This won't work on Merlin server, because you are limited to 50 processes.

If your executable hangs up or doesn't want to run, try running it yourself. 
The test shows you the arguments, that are currently tested.
```
./proj2 20 5 0 50
```

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

