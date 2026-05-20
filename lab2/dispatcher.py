import heapq
import random

# If you are a Mac user, uncomment the two following lines:
# import matplotlib as mpl
# mpl.use('tkagg')
import matplotlib.pyplot as plt

import numpy as np
from queue import Queue
import time
import sys

signalList = []


def send(signalType, evTime, destination, info):
    heapq.heappush(signalList, [evTime, signalType, destination, info])


GENERATE = 1
ARRIVAL = 2
DEPARTURE = 3
MEASUREMENT = 4


simTime = 0.0
stopTime = 100000


class larger:
    def __gt__(self, other):
        return False


class generator(larger):
    def __init__(self, lamda, sendTo):
        self.sendTo = sendTo
        self.lamda = lamda

    def arrivalTime(self):
        return simTime + random.expovariate(self.lamda)

    def treatSignal(self, x, info):
        if x == GENERATE:
            send(ARRIVAL, simTime, self.sendTo, [simTime])
            send(GENERATE, self.arrivalTime(), self, [])


class dispatcher(larger):
    def __init__(self, queues):
        self.queues = queues
        self.rr = 0

    def randomDispatch(self):
        # randomly select one queue from the list of queues
        return random.choice(self.queues)

    def roundRobin(self):
        self.rr = (self.rr + 1) % len(self.queues)
        return self.queues[self.rr]

    def fewestCustomers(self):
        smallest = 0
        smallestNumber = sys.maxsize
        for i in range(len(self.queues)):
            if smallestNumber > self.queues[i].numberInQueue:
                smallest = i
                smallestNumber = self.queues[i].numberInQueue
        return self.queues[smallest]

    def treatSignal(self, x, info):
        if x == ARRIVAL:
            send(ARRIVAL, simTime, self.fewestCustomers(), [simTime])


class queue(larger):
    def __init__(self, mu, sendTo):
        self.numberInQueue = 0
        self.sumMeasurements = 0
        self.numberOfMeasurements = 0
        self.measuredValues = []
        self.buffer = Queue(maxsize=0)
        self.sendTo = sendTo
        self.mu = mu

    def serviceTime(self):
        return simTime + random.expovariate(self.mu)

    # return 1/self.mu
    def treatSignal(self, x, info):
        if x == ARRIVAL:
            if self.numberInQueue == 0:
                send(DEPARTURE, self.serviceTime(), self, [])
            self.numberInQueue = self.numberInQueue + 1
            self.buffer.put(info)
        elif x == DEPARTURE:
            self.numberInQueue = self.numberInQueue - 1
            if self.numberInQueue > 0:
                send(DEPARTURE, self.serviceTime(), self, [])
            send(ARRIVAL, simTime, self.sendTo, self.buffer.get())
        elif x == MEASUREMENT:
            self.measuredValues.append(self.numberInQueue)
            self.sumMeasurements = self.sumMeasurements + self.numberInQueue
            self.numberOfMeasurements = self.numberOfMeasurements + 1
            send(MEASUREMENT, simTime + 1.0, self, [])


class sink(larger):
    def __init__(self):
        self.numberArrived = 0
        self.totalTime = 0

    def treatSignal(self, x, info):
        self.numberArrived = self.numberArrived + 1
        self.totalTime = self.totalTime + simTime - info[0]


startTime = time.time()
s = sink()
# Updated service rates: mu0=1, mu1=0.5, mu2=1.5, mu3=1, mu4=1
queues = [queue(MU, s) for MU in [1, 0.5, 1.5, 1, 1]]
disp = dispatcher(queues)
gen = generator(4, disp)

send(GENERATE, 0, gen, [])
for i in queues:
    send(MEASUREMENT, 1, i, [])


while simTime < stopTime:
    [simTime, signalType, dest, info] = heapq.heappop(signalList)
    dest.treatSignal(signalType, info)


Lq = len(queues)
for i in range(Lq):
    print(
        "In queueing system ",
        i,
        ": ",
        queues[i].sumMeasurements / queues[i].numberOfMeasurements,
    )


print("Mean time in queue: ", s.totalTime / s.numberArrived)


totalTid = time.time() - startTime
print("Elapsed time: ", totalTid)


x = 20
a = list(range(0, x))
hist = [
    np.histogram(queues[i].measuredValues, bins=a, density=True)[0] for i in range(Lq)
]


X = np.arange(x - 1)
fig = plt.figure()
a = 0.00
w = 0.15

for i in range(len(queues)):
    plt.bar(X + a, hist[i], width=w)
    a += w

# --- Calculate Total Metrics ---

# Sum the average number of customers from every queue in the dispatcher
total_E_N = sum(q.sumMeasurements / q.numberOfMeasurements for q in queues)

# The sink already has the total time and total count for E(T)
mean_E_T = s.totalTime / s.numberArrived

print(f"\nTotal mean number of customers E(N): {total_E_N:.4f}")
print(f"Mean time in system E(T): {mean_E_T:.4f}")

# Optional: Verify with Little's Law (E(N) = lambda * E(T))
# lambda is 4 in your current setup
print(f"Verification (Lambda * E(T)): {4 * mean_E_T:.4f}")

plt.show()
