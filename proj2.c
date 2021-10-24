#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdarg.h>
#include <time.h>
#include <sys/ipc.h>
#include <sys/types.h>
#include <sys/shm.h>
#include <sys/wait.h>
#include <semaphore.h>

// number must be less than
#define MAX_NE 1000
#define MAX_NR 20
// time must be less OR EQUAL
#define MAX_TE 1000
#define MAX_TR 1000

// how many elves are needed before santa helps them
#define ELF_GROUP 3
#define OUTPUT_FILENAME "proj2.out"

static FILE *outFile;

#define NUM_SEMS 10

typedef enum {
    SUCCESS = 0,
    ERR_ARGS,
    ERR_FORK,
    ERR_SHMGET,
    ERR_SHMAT,
    ERR_FOPEN,
    ERR_NEW_SEM,
    ERR_DEL_SEM,
} Error;

typedef enum {
    SEM_LOG = 0, // mutex for logging function
    SEM_SANTA, // used to wake up santa
    SEM_HITCH, // Reindeers wait for hitching by santa
    SEM_HELP_FN, // mutex for getHelp function
    SEM_SANTA_HELP, // elves wait for help from santa
    SEM_WORKSHOP, // signalizes whether the workshop is free
    SEM_CONFIRM_HELP, // reindeer of elf sets this to confirm help from santa
    SEM_RETURN, // mutex for returning reindeers
    SEM_FINISH, // semaphore for end of main process
    SEM_START,
} Semaphore;

typedef struct {
    // mutex for logging function
    int logCounter;
    // maximum is 2, the third will go wake up santa
    int elvesWaiting;
    // number of reindeers, that are already home
    int rdsReturned;
    // 1 by default, 0 after santa closes it
    bool workshopOpen;
    // 1 by default, 0 if fork fails
    bool initOK;
    sem_t sems[NUM_SEMS];
} SharedData;

static int shmid;
static SharedData *pShared = NULL;

typedef struct {
	int numElves;
	int numReindeers;
	// how long can an elf work without assistatnce
	int timeElf;
	// maximum length of reindeer's vacation
	int timeReindeer;
} Args;


void detachSharedMemory() {
    shmdt(pShared);
}

// side effect - sets atexit to automatically detach memory
Error initSharedMemory() {
    shmid = shmget(IPC_PRIVATE, sizeof(SharedData), IPC_CREAT | 0644);
    if (shmid == -1) {
        return ERR_SHMGET;
    }

    pShared = shmat(shmid, NULL, 0);
    if (pShared == (void *) -1) {
        return ERR_SHMAT;
    }
    // every process detaches the memory at exit
    atexit(detachSharedMemory);

    // initial values
    pShared->logCounter = 1;
    pShared->elvesWaiting = 0;
    pShared->workshopOpen = true;
    pShared->initOK = true;

    return SUCCESS;
}

// returns number of semaphores, that have been set up successfully
int initSemaphores(int *initialized) {
    int initialValues[] = {
        [SEM_LOG] = 1,
        [SEM_SANTA] = 0,
        [SEM_HITCH] = 0,
        [SEM_HELP_FN] = 1,
        [SEM_SANTA_HELP] = 0,
        [SEM_WORKSHOP] = ELF_GROUP,
        [SEM_CONFIRM_HELP] = 0,
        [SEM_RETURN] = 1,
        [SEM_FINISH] = 0,
        [SEM_START] = 0,
    };

    for (int i=0; i<NUM_SEMS; i++) {
        int status = sem_init(&pShared->sems[i], 1, initialValues[i]);
        if (status != 0) {
            *initialized = i;
            return ERR_NEW_SEM;
        }
    }

    return SUCCESS;
}

// destroy first n semaphores
Error destroySemaphores(int n) {
    // initialize log semaphore to value 1
    bool failed = false;
    for (int i=0; i<n; i++) {
        // returns 0 on success
        int status = sem_destroy(&pShared->sems[i]);
        failed = failed && status;
    }
    if (failed) {
        return ERR_DEL_SEM;
    }
    return SUCCESS;
}

void logformat(const char *format, ...) {
    // lock the semaphore
    sem_wait(&pShared->sems[SEM_LOG]);
    // print the number of the line
    fprintf(outFile, "%d: ", pShared->logCounter);
    pShared->logCounter++;

    va_list args;
    va_start(args, format);
    vfprintf(outFile, format, args);
    va_end(args);

    // flush buffer immediately
    fflush(outFile);
    // unlock the semaphore
    sem_post(&pShared->sems[SEM_LOG]);
}

void closeOutFile() {
	fclose(outFile);
}

// side effect - sets atexit to close the file
Error openOutFile() {
    outFile = fopen(OUTPUT_FILENAME, "w");
    if (outFile == NULL) {
        return ERR_FOPEN;
    }
    atexit(closeOutFile);
    return SUCCESS;
}

void initRandomSeed() {
    // every processs needs different random seed
    // so we use pid to get seeds that are definitely unique
    srand(time(NULL) ^ getpid() << 16);
}

// This function should be called only by elves
// returns true if elf gets help, false if santa closes workshop
// elfID parameter is only for print
bool getHelp() {
    // only one elf can have getHelpSem
    // this semaphore is modified exclusively in this function
    sem_wait(&pShared->sems[SEM_HELP_FN]);
    // if the last elf from the last trio has release getHelpSem
    // but the other two are still getting help
    sem_wait(&pShared->sems[SEM_WORKSHOP]); // wait until workshop is empty

    // if workshop is closed, end the function and return false
    if (!pShared->workshopOpen) {
        sem_post(&pShared->sems[SEM_HELP_FN]);
        return false;
    }
    pShared->elvesWaiting++;

    if (pShared->elvesWaiting == ELF_GROUP) {
        // you are the third elf, keep the mutex
        // and go get help from santa
        sem_post(&pShared->sems[SEM_SANTA]);
        sem_wait(&pShared->sems[SEM_SANTA_HELP]);
        // you still have this function's mutex
        // so you can set waiting elves to 0
        pShared->elvesWaiting = 0;
        // only after you get help, another elf can go wait in queue
        sem_post(&pShared->sems[SEM_HELP_FN]);
    } else {
        // release the mutex, so third elf can wake up santa
        // after he arrives
        sem_post(&pShared->sems[SEM_HELP_FN]);
        // wait for help from santa
        sem_wait(&pShared->sems[SEM_SANTA_HELP]);
    }
    // if santa closed the workshop in the meantime, you did not get help
    // if the shop is still open, santa waits for your help confirmation
    if (pShared->workshopOpen) {
        return true;
    }
    return false;
}


void doSanta(Args args) {
    // need to break in the middle
    while (true) {
        logformat("Santa: going to sleep\n");
        // wait until anyone wakes santa up
        sem_wait(&pShared->sems[SEM_SANTA]);
        // block reindeers from coming
        sem_wait(&pShared->sems[SEM_RETURN]);
        bool reindeersBack = (pShared->rdsReturned == args.numReindeers);
        if (reindeersBack) {
            break;
        }
        // if santa is still in the loop, elves need help
        logformat("Santa: helping elves\n");
        // reindeers can come after message has been printed
        sem_post(&pShared->sems[SEM_RETURN]);

        // help the three elves, that are waiting right now
        for (int i=0; i<ELF_GROUP; i++) {
            sem_post(&pShared->sems[SEM_SANTA_HELP]);
            sem_wait(&pShared->sems[SEM_CONFIRM_HELP]);
        }
        // let the next three elves wait
        for (int i=0; i<ELF_GROUP; i++) {
            sem_post(&pShared->sems[SEM_WORKSHOP]);
        }
    }

    logformat("Santa: closing workshop\n");
    pShared->workshopOpen = false;
    // now every elf can pass through workshop semaphore
    for (int i=0; i<args.numElves; i++) {
        sem_post(&pShared->sems[SEM_WORKSHOP]);
    }
    // if any elves are waiting for help, tell them to go     home
    for (int i=0; i<ELF_GROUP; i++) {
        sem_post(&pShared->sems[SEM_SANTA_HELP]);
    }

    // hitch all the reindeers
    for (int i=0; i<args.numReindeers; i++) {
        sem_post(&pShared->sems[SEM_HITCH]);
        sem_wait(&pShared->sems[SEM_CONFIRM_HELP]);
    }

    logformat("Santa: Christmas started\n");
}


void doElf(int elfID, Args args) {
    logformat("Elf %d: started\n", elfID);
    initRandomSeed();

    while (true) {
        int t = args.timeElf;
        // 1000 to convert ms to us
        int waitFor = rand() % (t*1000 + 1);
        usleep(waitFor); // working independently

        logformat("Elf %d: need help\n", elfID);
        if (!getHelp()) {
            // if the workshop is closed, break
            break;
        }
        // write out, that you got help
        logformat("Elf %d: get help\n", elfID);
        // confirm to santa
        sem_post(&pShared->sems[SEM_CONFIRM_HELP]);
    }

    logformat("Elf %d: taking holidays\n", elfID);
}


void doReindeer(int rdID, Args args) {
    logformat("RD %d: rstarted\n", rdID);
    initRandomSeed();

    int t = args.timeReindeer;
    // results in interval <TR/2, TR>
    int waitFor = rand() % (t*500 + 1) + t*500;
    usleep(waitFor); // vacation

    // critical section
    sem_wait(&pShared->sems[SEM_RETURN]);
    logformat("RD %d: return home\n", rdID);
    pShared->rdsReturned++;
    if (pShared->rdsReturned == args.numReindeers) {
        // Wake up Santa, if you are the last one
        sem_post(&pShared->sems[SEM_SANTA]);
    }
    sem_post(&pShared->sems[SEM_RETURN]);

    // wait to get hitched by santa
    sem_wait(&pShared->sems[SEM_HITCH]);
    logformat("RD %d: get hitched\n", rdID);
    // After logging, confirm help to santa
    sem_post(&pShared->sems[SEM_CONFIRM_HELP]);
}


Error readArguments(int argc, char **argv, Args *a) {
	// name of executable + 4 positional arguments
	if (argc != 5) {
		fprintf(stderr, "Bad arguments.\nUsage: %s NE NR TE TR\n", argv[0]);
		return ERR_ARGS;
	}

	char *numberEnd;

	a->numElves = strtol(argv[1], &numberEnd, 10);
	// if there is something after the number in the argument
	// or if the number is out of permitted range
	if ((*numberEnd != '\0') || (a->numElves <= 0) || (a->numElves >= MAX_NE)) {
        return ERR_ARGS;
	}

	a->numReindeers = strtol(argv[2], &numberEnd, 10);
	if ((*numberEnd != '\0') || (a->numReindeers <= 0) || (a->numReindeers >= MAX_NR)) {
        return ERR_ARGS;
	}

	a->timeElf = strtol(argv[3], &numberEnd, 10);
	if ((*numberEnd != '\0') || (a->timeElf < 0) || (a->timeElf > MAX_TE)) {
        return ERR_ARGS;
	}

	a->timeReindeer = strtol(argv[4], &numberEnd, 10);
	if ((*numberEnd != '\0') || (a->timeReindeer < 0) || (a->timeReindeer > MAX_TR)) {
        return ERR_ARGS;
	}

	return SUCCESS;
}

Error spawnSubproc(Args args, int *childrenCreated) {
    int numChildren = 1 + args.numElves + args.numReindeers;

    int i;
	for (i=0; i<numChildren; i++) {
		pid_t pid = fork();

		if (pid < 0) {
            *childrenCreated = i;
            pShared->initOK = false;
			return ERR_FORK;
		}

		if (pid == 0) {
            // code for all the children
            sem_wait(&pShared->sems[SEM_START]);
            if (pShared->initOK) {
                // decide the type of child and start its function
                if (i == 0) {
                    doSanta(args);
                }
                else if (i <= args.numElves) {
        		    doElf(i, args);
                }
                else {
                    i -= args.numElves;
                    doReindeer(i, args);
                }
            }
            sem_post(&pShared->sems[SEM_FINISH]);
        	exit(0);
		}
	}
    *childrenCreated = numChildren;
    return SUCCESS;
}

void printError(Error err) {
    char *msgs[] = {
        [ERR_ARGS] = "Bad arguments.\nUsage: %s NE NR TE TR\n",
        [ERR_FORK] = "Fork calling was unsuccessful\n",
        [ERR_SHMGET] = "Unsuccessful shared memory allocation\n",
        [ERR_SHMAT] = "Could not attach shared memory\n",
        [ERR_FOPEN] = "Could not open output file\n",
        [ERR_NEW_SEM] = "Could not initialize a semaphore\n",
        [ERR_DEL_SEM] = "Could not delete a semaphore\n",
    };

    if (err < 0 || err > sizeof(msgs) / sizeof(char *)) {
        fputs("Unknown error\n", stderr);
    }

    fputs(msgs[err], stderr);
}

int main(int argc, char **argv) {
    Error err = SUCCESS;
    int semsInitialized = 0;

	Args args;
    err = readArguments(argc, argv, &args);
    if (err != SUCCESS) {
        goto NO_CLEANUP_EXIT;
    }

    err = openOutFile();
    if (err != SUCCESS) {
        goto NO_CLEANUP_EXIT;
    }

    err = initSharedMemory();
    if (err != SUCCESS) {
        if (err == ERR_SHMGET) {
            goto NO_CLEANUP_EXIT;
        }
        goto MEM_EXIT;
    }

    err = initSemaphores(&semsInitialized);
    if (err != SUCCESS) {
        goto SEMAPHORE_EXIT;
    }

    // will return number of successfully forked children
    // if error occurs, children will know it from error in shared memory
    int numChildren;
	err = spawnSubproc(args, &numChildren);

    // let all the children run
    for (int i=0; i<numChildren; i++) {
        sem_post(&pShared->sems[SEM_START]);
    }
    // wait until all children finish
    for (int i=0; i<numChildren; i++) {
        sem_wait(&pShared->sems[SEM_FINISH]);
    }

    SEMAPHORE_EXIT:
    destroySemaphores(semsInitialized);

    MEM_EXIT:
    shmctl(shmid, IPC_RMID, 0);

    NO_CLEANUP_EXIT:
    if (err != SUCCESS) {
        printError(err);
        return 1;
    }
	return 0;
}
