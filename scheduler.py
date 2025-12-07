import sys
import heapq
from enum import Enum
from collections import deque

# Enum for process states (5 state model)
class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    EXIT = "EXIT"

# Enum for event types
class EventType(Enum):
    ARRIVAL = "ARRIVAL"
    PREEMPTION = "PREEMPTION"
    IO_REQUEST = "IO_REQUEST"
    IO_DONE = "IO_DONE"
    TERMINATION = "TERMINATION"

# Process Control Block class
class Process:
    def __init__(self, pid, arrival_time, cpu_bursts, io_bursts):
        self.pid = pid
        self.arrival_time = arrival_time
        self.cpu_bursts = cpu_bursts
        self.io_bursts = io_bursts
        self.state = ProcessState.NEW
        
        # keep track of which CPU/IO burst we are on
        self.current_cpu_burst_idx = 0
        self.current_io_burst_idx = 0
        self.remaining_cpu_burst_time = 0

        # performance metrics
        self.finish_time = None
        self.total_ready_wait = 0
        self.total_io_wait = 0
        self.last_ready_enqueue_time = None
        self.last_io_enqueue_time = None

# Event class for discrete event simulation
class Event:
    def __init__(self, time, event_type, process_id):
        self.time = time
        self.type = event_type
        self.process_id = process_id

    def __lt__(self, other):
        return self.time < other.time


# Scheduler Class
class Scheduler:
    # Now includes output_file as separate file from log_file
    def __init__(self, input_file, output_file, log_file, quantum):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file
        self.time_quantum = int(quantum)
        
        # simulation control
        self.sim_time = 0
        self.cpu_idle = True
        self.io_device_idle = True
        self.cpu_busy_time = 0
        
        # tracking current processes
        self.running_process = None
        self.io_process = None

        # main data structures
        self.processes = []
        self.event_queue = []
        self.ready_queue = deque()
        self.io_queue = deque()

    # Read input file and initialize ARRIVAL events (with validation + logging invalid inputs)
    def _initialize_events(self):
        with open(self.input_file, 'r') as f, open(self.log_file, 'a') as log:
            pid_counter = 0  # process ID tracker

            for line in f:
                # skip blank lines
                if not line.strip():
                    continue

                parts = [int(p) for p in line.strip().split()]
                arrival = parts[0]
                num_bursts = parts[1]

                # calculate expected number of values in this line
                expected_values = 2 + (num_bursts * 2 - 1)

                # ---- VALIDATION CHECKS ----

                # invalid start time
                if arrival <= 0:
                    msg = f"Invalid Input: {line.strip()} < invalid start time; start time must be > 0; start time input = {arrival}\n"
                    print(msg.strip())
                    log.write(msg)
                    continue  # skip invalid process

                # invalid number of CPU bursts
                if num_bursts <= 0:
                    msg = f"Invalid Input: {line.strip()} < invalid number of CPU bursts; must be > 0; number of CPU bursts = {num_bursts}\n"
                    print(msg.strip())
                    log.write(msg)
                    continue

                # mismatch between declared and actual number of bursts
                if len(parts) != expected_values:
                    actual_bursts = (len(parts) - 2) // 2
                    msg = f"Invalid Input: {line.strip()} < number of CPU bursts = {num_bursts}; number of CPU bursts input = {actual_bursts}\n"
                    print(msg.strip())
                    log.write(msg)
                    continue

                # invalid burst duration (0 or negative)
                if any(x <= 0 for x in parts[2:]):
                    msg = f"Invalid Input: {line.strip()} < CPU burst and/or I/O burst value must be > 0; one of the burst values = 0\n"
                    print(msg.strip())
                    log.write(msg)
                    continue

                # ---- VALID INPUT ----
                # split into CPU and I/O bursts
                cpu_bursts = parts[2::2]
                io_bursts = parts[3::2]

                # create new process
                proc = Process(pid_counter, arrival, cpu_bursts, io_bursts)
                self.processes.append(proc)

                # schedule first ARRIVAL event
                heapq.heappush(self.event_queue, Event(proc.arrival_time, EventType.ARRIVAL, proc.pid))

                pid_counter += 1  # move to next process ID


    # Main Simulation Loop
    def run(self):
        self._initialize_events()

        with open(self.log_file, 'w') as log:
            while self.event_queue:
                current_event = heapq.heappop(self.event_queue)

                # advance time until next event
                while self.sim_time < current_event.time:
                    log.write(f"{self.sim_time}: no event\n")
                    self.sim_time += 1
                    if self.sim_time % 5 == 0:
                        self._print_queue_states(log, "before events")

                self.sim_time = current_event.time

                # handle all events happening at this same time
                events_at_this_time = [current_event]
                while self.event_queue and self.event_queue[0].time == self.sim_time:
                    events_at_this_time.append(heapq.heappop(self.event_queue))

                # event priority order
                priority = {
                    EventType.ARRIVAL: 0,
                    EventType.IO_DONE: 1,
                    EventType.PREEMPTION: 2,
                    EventType.IO_REQUEST: 3,
                    EventType.TERMINATION: 4
                }

                events_at_this_time.sort(key=lambda e: priority[e.type])

                for event in events_at_this_time:
                    self._handle_event(event, log)

                self._dispatch(log)

            log.write(f"{self.sim_time}: simulation finished.\n")

        # Write results to separate output file
        self._print_summary()

    # Handle different event types
    def _handle_event(self, event, log):
        p = self.processes[event.process_id]
        log.write(f"{self.sim_time}: P{p.pid}")

        if event.type == EventType.ARRIVAL:
            log.write(f" arrives, changes state from {p.state.value} to READY\n")
            p.state = ProcessState.READY
            p.last_ready_enqueue_time = self.sim_time
            self.ready_queue.append(p.pid)

        elif event.type == EventType.PREEMPTION:
            log.write(f" preempted, changes state from RUNNING to READY\n")
            self.running_process = None
            self.cpu_idle = True
            p.state = ProcessState.READY
            p.last_ready_enqueue_time = self.sim_time
            self.ready_queue.append(p.pid)

        elif event.type == EventType.IO_REQUEST:
            log.write(f" requests I/O, changes state from RUNNING to BLOCKED\n")
            self.running_process = None
            self.cpu_idle = True
            p.state = ProcessState.BLOCKED
            p.last_io_enqueue_time = self.sim_time
            self.io_queue.append(p.pid)

        elif event.type == EventType.IO_DONE:
            log.write(f" finishes I/O, changes state from BLOCKED to READY\n")
            self.io_process = None
            self.io_device_idle = True
            p.state = ProcessState.READY
            p.last_ready_enqueue_time = self.sim_time
            self.ready_queue.append(p.pid)

        elif event.type == EventType.TERMINATION:
            log.write(f" terminates, changes state from RUNNING to EXIT\n")
            self.running_process = None
            self.cpu_idle = True
            p.state = ProcessState.EXIT
            p.finish_time = self.sim_time

    # CPU and IO dispatching
    def _dispatch(self, log):
        # CPU scheduling
        if self.cpu_idle and self.ready_queue:
            pid_to_run = self.ready_queue.popleft()
            p = self.processes[pid_to_run]

            if p.last_ready_enqueue_time is not None:
                p.total_ready_wait += self.sim_time - p.last_ready_enqueue_time

            self.running_process = p
            self.cpu_idle = False
            p.state = ProcessState.RUNNING
            log.write(f"{self.sim_time}: P{p.pid} changes state from READY to RUNNING\n")

            if p.remaining_cpu_burst_time <= 0:
                p.remaining_cpu_burst_time = p.cpu_bursts[p.current_cpu_burst_idx]

            burst_duration = p.remaining_cpu_burst_time
            self.cpu_busy_time += min(burst_duration, self.time_quantum)

            if burst_duration > self.time_quantum:
                p.remaining_cpu_burst_time -= self.time_quantum
                heapq.heappush(self.event_queue, Event(self.sim_time + self.time_quantum, EventType.PREEMPTION, p.pid))
            else:
                p.remaining_cpu_burst_time = 0
                p.current_cpu_burst_idx += 1

                if p.current_cpu_burst_idx < len(p.cpu_bursts):
                    heapq.heappush(self.event_queue, Event(self.sim_time + burst_duration, EventType.IO_REQUEST, p.pid))
                else:
                    heapq.heappush(self.event_queue, Event(self.sim_time + burst_duration, EventType.TERMINATION, p.pid))

        # I/O scheduling
        if self.io_device_idle and self.io_queue:
            pid_to_io = self.io_queue.popleft()
            p = self.processes[pid_to_io]

            if p.last_io_enqueue_time is not None:
                p.total_io_wait += self.sim_time - p.last_io_enqueue_time

            self.io_process = p
            self.io_device_idle = False
            log.write(f"{self.sim_time}: P{p.pid} starts I/O\n")

            io_duration = p.io_bursts[p.current_io_burst_idx]
            p.current_io_burst_idx += 1
            heapq.heappush(self.event_queue, Event(self.sim_time + io_duration, EventType.IO_DONE, p.pid))

    # Print queues for debugging
    def _print_queue_states(self, log, context):
        log.write(f"{self.sim_time}: ----- Queue States ({context}) -----\n")
        ready_q_str = " ".join([f"P{pid}" for pid in self.ready_queue]) if self.ready_queue else "empty"
        io_q_str = " ".join([f"P{pid}" for pid in self.io_queue]) if self.io_queue else "empty"
        log.write(f"{'Ready Queue:':<15}{ready_q_str}\n")
        log.write(f"{'I/O Queue:':<15}{io_q_str}\n")
        log.write("----------------------------------\n")

    # Final summary printed in a separate output file
    def _print_summary(self):
        total_turnaround = 0
        total_ready_wait = 0
        total_io_wait = 0
        num_finished = 0

        if not self.processes:
            with open(self.output_file, 'w') as out:
                out.write("<Output File - Simulation Results>\n")
                out.write(f"> Results for quantum = {self.time_quantum} CPU utilization = 0%\n")
                out.write("No valid processes to simulate.\n")
            return

        for p in self.processes:
            if p.finish_time:
                tat = p.finish_time - p.arrival_time
                total_turnaround += tat
                total_ready_wait += p.total_ready_wait
                total_io_wait += p.total_io_wait
                num_finished += 1

        cpu_util = round((self.cpu_busy_time / self.sim_time) * 100) if self.sim_time > 0 else 0

        with open(self.output_file, 'w') as out:
            out.write("<Output File - Simulation Results>\n")
            out.write(f"> Results for quantum = {self.time_quantum} CPU utilization = {cpu_util}%\n")
            for p in self.processes:
                if p.finish_time:
                    tat = p.finish_time - p.arrival_time
                    out.write(f"P{p.pid} (Turn Around Time = {tat}, ReadyWait = {p.total_ready_wait}, I/O-wait={p.total_io_wait})\n")

            if num_finished > 0:
                out.write(f"\nCPU Utilization = {cpu_util}%\n")
                out.write(f"Average Turnaround = {total_turnaround/num_finished:.2f}\n")
                out.write(f"Average Ready Wait = {total_ready_wait/num_finished:.2f}\n")
                out.write(f"Average I/O Wait = {total_io_wait/num_finished:.2f}\n")


# Main Entry Point
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python scheduler.py <output_file> <input_file> <log_file> <quantum>")
        sys.exit(1)

    output_file = sys.argv[1]
    input_file = sys.argv[2]
    log_file = sys.argv[3]
    quantum = sys.argv[4]

    print("Starting simulation with:")
    print(f"Input File: {input_file}")
    print(f"Output File: {output_file}")
    print(f"Log File: {log_file}")
    print(f"Time Quantum: {quantum}")

    scheduler = Scheduler(input_file, output_file, log_file, quantum)
    scheduler.run()

    print(f"Simulation complete.\n- Output summary: {output_file}\n- Detailed log: {log_file}")
