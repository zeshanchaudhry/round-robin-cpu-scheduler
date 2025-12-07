Course: CIS 450 – Operating Systems
Assignment: Programming Assignment #1 – Job Scheduler
Simulation Language: Python 3 

1. DESCRIPTION:
    This project simulates a Round Robin (RR) CPU Scheduling algorithm using a single CPU and a single I/O device. It reads process data from an input file, performs event-based scheduling, and logs every state change. The simulator follows the 5-state model (NEW, READY, RUNNING, BLOCKED, EXIT) and handles events like arrivals, preemptions, I/O requests, and terminations. It also detects invalid input lines and skips them while printing an error message to the console. The final output shows CPU utilization, average turnaround time, average ready wait, and average I/O wait times.

2. HOW TO RUN 
    To run the scheduler, make sure you have Python 3 installed.
    You can run the simulation directly from the terminal or from Visual Studio Code.
    The program takes four command-line arguments in this order:
    Run the program from the command line using this format: 

        python scheduler.py <output_file> <input_file> <log_file> <quantum> 
    
    Example Commands to use:
        python scheduler.py cpu_intensive_output.txt cpu_intensive.txt cpu_intensive_log.txt 3
        python scheduler.py io_intensive_output.txt io_intensive.txt io_intensive_log.txt 2
        python scheduler.py mixed_output.txt mixed.txt mixed_log.txt 2
        python scheduler.py mixed_q5_output.txt mixed_q5.txt mixed_q5_log.txt 5
        python scheduler.py mixed_q10_output.txt mixed_q10.txt mixed_q10_log.txt 10
        python scheduler.py invalid_output.txt invalid_input.txt invalid_log.txt 2
        python scheduler.py cpu_short_output.txt cpu_short.txt cpu_short_log.txt 3
        python scheduler.py io_long_output.txt io_long.txt io_long_log.txt 2
        python scheduler.py staggered_arrival_output.txt staggered_arrival.txt staggered_arrival_log.txt 3
        python scheduler.py cpu_heavy_io_small_output.txt cpu_heavy_io_small.txt cpu_heavy_io_small_log.txt 4
        python scheduler.py stress_test_output.txt stress_test.txt stress_test_log.txt 5

 
    
3. FILE ORGANIZATION
    Source Code: 
        scheduler.py                -> main simulation program
    
    Documentation Files
        README_CONFIGURATION.txt    -> setup and file explanation
        Executed Test Plan.pdf      -> list and results of all test cases
        Results and Discussion.pdf  -> summary of all test data and hypothesis comparison

    CPU-Intensive Test Files: 
        cpu_intensive.txt           -> Input file with CPU-bound processes
        cpu_intensive_output.txt    -> Output summary for CPU-intensive test
        cpu_intensive_log.txt       -> Detailed log for CPU-intensive test

    I/O-Intensive Test Files: 
        io_intensive.txt            -> Input file with I/O-bound processes
        io_intensive_output.txt     -> Output summary for I/O-intensive test
        io_intensive_log.txt        -> Detailed log for I/O-intensive test
        
    Mixed Process Test Files: 
        mixed.txt                   -> Input file with a mix of CPU and I/O processes
        mixed_output.txt            -> Output summary for mixed test (quantum = 2)
        mixed_log.txt               -> Event log for mixed test (quantum = 2)
        mixed_q5.txt                -> Input file used for testing Round Robin with quantum = 5
        mixed_q5_output.txt         -> Output summary for mixed_q5 test
        mixed_q5_log.txt            -> Detailed log for mixed_q5 test
        mixed_q10.txt               -> Input file used for testing quantum = 10
        mixed_q10_output.txt        -> Output summary for mixed_q10 test
        mixed_q10_log.txt           -> Detailed log for mixed_q10 test
        
    Invalid Input Test Files: 
        invalid_input.txt           -> Input file with invalid data for error handling test
        invalid_out.txt             -> Output summary for invalid input test
        invalid_log.txt             -> Log showing skipped invalid lines
        
    Additional New Test Cases 
        cpu_short.txt 
        cpu_short_output.txt
        cpu_short_log.txt 

            → Short CPU bursts with quick finishes. Tests fairness with frequent context switching and short turnaround times.


        io_long.txt
        io_long_output.txt
        io_long_log.txt 

            → Processes with long I/O bursts and small CPU bursts. Tests how blocking affects CPU idle time.


        staggered_arrival.txt
        staggered_arrival_output.txt
        staggered_arrival_log.txt 

            → Processes arrive at different times. Checks if Round Robin keeps the CPU busy and fair with delayed arrivals.


        cpu_heavy_io_small.txt
        cpu_heavy_io_small_output.txt
        cpu_heavy_io_small_log.txt 

            → Mostly CPU-bound jobs with very short I/O bursts. Tests performance under near-constant CPU use.


        stress_test.txt
        stress_test_output.txt
        stress_test_log.txt 

            → Large mixed workload (8 processes). Tests stability and scheduler performance under heavy load.
        

4. INPUT FILE FORMAT
    Each line in the input file represents a process in the following format: 

        <arrival_time> <num_cpu_bursts> <cpu1> <io1> <cpu2> <io2> ... <cpuN> 

    Example: 
        3 3 2 5 8 7 4 

    Meaning: 
    - Process arrives at time 3 
    - Has 3 CPU bursts: 2, 8, 4 
    - Has 2 I/O bursts: 5, 7 

5. OUTPUT FILES
    LOG FILE: 
    Contains detailed time-based events, for example: 
    5: P1 arrives, changes state from NEW to READY 
    5: P1 changes state from READY to RUNNING 
    8: P1 requests I/O, changes state from RUNNING to BLOCKED 
    58: simulation finished. 
    
    OUTPUT FILE: 
    Contains summary statistics formatted as required: 
        <Output File - Simulation Results> 
        > Results for quantum = 2 CPU utilization = 77% 
        P0 (Turn Around Time = 60, ReadyWait = 18, I/O-wait=16) 
        P1 (Turn Around Time = 7, ReadyWait = 3, I/O-wait=0) 
        P2 (Turn Around Time = 47, ReadyWait = 7, I/O-wait=20) 
        ... 
        CPU Utilization = 77% 
        Average Turnaround = 49.00 
        Average Ready Wait = 10.33 
        Average I/O Wait = 13.67 

6. INVALID INPUT HANDLING
    If a process line is invalid, it is skipped and reported as an error message. 
    Examples of invalid lines: 
        0 2 5 2 2     < invalid start time; must be > 0 
        2 0 2 1 4     < invalid number of CPU bursts; must be > 0 
        4 2 3 4       < incorrect number of parameters 
        6 3 0 6 1     < CPU/IO burst value must be > 0 
        
    The program continues running and produces: 
        <Output File - Simulation Results> 
        > Results for quantum = 2 CPU utilization = 0% 
        
    This confirms that the program handled invalid input correctly and skipped bad processes. 

7. NOTES
    - There is only one CPU and one I/O device. 
    - The simulation starts at time 0 and progresses one time unit at a time. 
    - Scheduling is handled using Round Robin with the specified quantum. 
    - Every 5 time units, the current Ready Queue and I/O Queue states are printed to the log file. 
    - If multiple events happen at the same time, the program handles them in this priority order: 
        - Arrival 
        - I/O Completion 
        - Preemption 
        - I/O Request 
        - Termination 

    - Invalid input lines like zero arrival time, wrong number of CPU bursts, or zero burst values are ignored with an error message printed to the console. 
    - CPU utilization = (Total CPU busy time / Total simulation time) × 100%. 
    - The output file summarizes results for each process with turnaround, ready wait, and I/O wait times. 
    - The log file records every single event in sequence like arrival, running, blocked, terminated, etc.