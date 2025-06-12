import multiprocessing as mp
import os
import time
import random
import numpy as np
from ctypes import c_bool, c_int, c_double

# Pinning helper
def pin_to_core(core_id):
    """Pin the current process to a specific CPU core"""
    pid = os.getpid()
    os.sched_setaffinity(pid, {core_id})

# Shared memory
FAULT_FLAG = mp.Value(c_bool, False)
ERROR_CODE = mp.Value(c_int, 0)
CORRECTION_COUNT = mp.Value(c_int, 0)
SYSTEM_HEALTH = mp.Value(c_double, 100.0)

class SimulatedFault(Exception):
    pass

# Core 1
def primary_worker(health):
    pin_to_core(0)
    print("Core 1: Primary worker started")
    try:
        iteration = 0
        while True:
            task_result = complex_calculation(iteration)
            if random.random() < 0.15:
                raise SimulatedFault(f"Core1 fault at iteration {iteration}")
            time.sleep(0.5)
            iteration += 1
            health.value = max(60, health.value - 0.01)
    except SimulatedFault as e:
        ERROR_CODE.value = random.randint(100, 999)
        FAULT_FLAG.value = True
        print(f"⚠️ Core 1: FAULT DETECTED - {str(e)}")

# Core 2
def fault_detector(fault_flag, error_code, health):
    pin_to_core(1)
    print("Core 2: Fault detector activated")
    while True:
        if memory_corruption_check():
            error_code.value = 800
            fault_flag.value = True
        if computation_validation():
            error_code.value = 900
            fault_flag.value = True
        if timing_violation_check():
            error_code.value = 700
            fault_flag.value = True
        time.sleep(0.1)

# Core 3
def error_corrector(fault_flag, correction_count, health):
    pin_to_core(2)
    print("Core 3: Error corrector standing by")
    while True:
        if fault_flag.value:
            print(f"🛠️ Core 3: Correcting error {ERROR_CODE.value}")
            if 100 <= ERROR_CODE.value < 200:
                apply_rollback_recovery()
            elif 700 <= ERROR_CODE.value < 800:
                adjust_timing_constraints()
            else:
                apply_redundant_computation()
            correction_count.value += 1
            fault_flag.value = False
            health.value = min(100, health.value + 2.5)
        time.sleep(0.1)

# Core 4
def health_reporter(correction_count, health):
    pin_to_core(3)
    print("Core 4: Health reporter initialized")
    report_interval = 5
    last_report = time.time()
    while True:
        if time.time() - last_report > report_interval:
            print("\n" + "="*50)
            print(f"📊 SYSTEM HEALTH REPORT [{time.strftime('%H:%M:%S')}]")
            print(f"Current Health: {health.value:.1f}/100")
            print(f"Total Corrections: {correction_count.value}")
            if health.value < 75:
                print("🚨 ACTION REQUIRED: Increase watchdog timer frequency")
            if correction_count.value > 10:
                print("🚨 ACTION REQUIRED: Investigate persistent error source")
            if health.value > 95:
                print("✅ OPTIMIZATION: Reduce redundancy for efficiency")
            print("="*50 + "\n")
            last_report = time.time()
        time.sleep(0.5)

# Simulated check functions
def complex_calculation(iteration):
    if random.random() < 0.05:
        return 1 / (iteration % 10)  # risky division
    return np.sqrt(iteration) * np.sin(iteration)

def memory_corruption_check():
    return random.random() < 0.02

def computation_validation():
    return random.random() < 0.03

def timing_violation_check():
    return random.random() < 0.01

def apply_rollback_recovery():
    time.sleep(0.2)

def adjust_timing_constraints():
    time.sleep(0.1)

def apply_redundant_computation():
    time.sleep(0.3)

# Main
if __name__ == "__main__":
    print("🚀 Starting Quad-Core Self-Healing System with Core Pinning")
    processes = [
        mp.Process(target=primary_worker, args=(SYSTEM_HEALTH,)),
        mp.Process(target=fault_detector, args=(FAULT_FLAG, ERROR_CODE, SYSTEM_HEALTH)),
        mp.Process(target=error_corrector, args=(FAULT_FLAG, CORRECTION_COUNT, SYSTEM_HEALTH)),
        mp.Process(target=health_reporter, args=(CORRECTION_COUNT, SYSTEM_HEALTH)),
    ]
    for p in processes:
        p.start()
    time.sleep(60)  # Run system for 60 seconds
    for p in processes:
        p.terminate()

    print("🛑 System shutdown complete.")
