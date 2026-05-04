import heapq
import random
import matplotlib.pyplot as plt
import numpy as np
from queue import Queue

# import matplotlib as mpl
# mpl.use('tkagg')
# import matplotlib.pyplot as plt

signalList = []


def send(signalType, evTime, destination, info):
    heapq.heappush(signalList, (evTime, signalType, destination, info))


GENERATE = 1
ARRIVAL = 2
MEASUREMENT = 3
DEPARTURE = 4

simTime = 0.0
stopTime = 10000.0


class larger:
    def __gt__(self, other):
        return False


class generator(larger):
    def __init__(self, sendTo, lmbda):
        self.sendTo = sendTo
        self.lmbda = lmbda
        self.arrivalTimes = []

    def arrivalTime(self):
        return simTime + random.expovariate(self.lmbda)

    def treatSignal(self, x, info):
        if x == GENERATE:
            send(ARRIVAL, simTime, self.sendTo, simTime)  # Send new cusomer to queue
            send(GENERATE, self.arrivalTime(), self, [])  # Schedule next arrival
            self.arrivalTimes.append(simTime)


class queue(larger):
    def __init__(self, mu, sendTo):
        self.numberInQueue = 0
        self.sumMeasurements = 0
        self.numberOfMeasurements = 0
        self.measuredValues = []
        self.buffer = Queue(maxsize=0)
        self.mu = mu
        self.sendTo = sendTo

    def serviceTime(self):
        return simTime + random.expovariate(self.mu)

    def treatSignal(self, x, info):
        if x == ARRIVAL:
            if self.numberInQueue == 0:
                send(
                    DEPARTURE, self.serviceTime(), self, []
                )  # Schedule  a departure for the arrival customer if queue is empty
            self.numberInQueue = self.numberInQueue + 1
            self.buffer.put(info)
        elif x == DEPARTURE:
            self.numberInQueue = self.numberInQueue - 1
            if self.numberInQueue > 0:
                send(
                    DEPARTURE, self.serviceTime(), self, []
                )  # Schedule  a departure for next customer in queue
            send(ARRIVAL, simTime, self.sendTo, self.buffer.get())
        elif x == MEASUREMENT:
            self.measuredValues.append(self.numberInQueue)
            self.sumMeasurements = self.sumMeasurements + self.numberInQueue
            self.numberOfMeasurements = self.numberOfMeasurements + 1
            send(MEASUREMENT, simTime + random.expovariate(1), self, [])


class sink(larger):
    def __init__(self):
        self.numberArrived = 0
        self.departureTimes = []
        self.totalTime = 0
        self.T = []

    def treatSignal(self, x, info):
        self.numberArrived = self.numberArrived + 1
        self.departureTimes.append(info)
        self.totalTime = self.totalTime + simTime - info
        self.T.append(simTime - info)


###################################################
#
# Add code to create a queuing system  here
#
###################################################

# Uppdatera stopTime till 1000 sekunder enligt labbinstruktionerna
stopTime = 3000.0

lmbda = 7.0
mu = 10.0

# Skapa instanser av systemets delar (vi kopplar dem baklänges för att referenserna ska stämma)
s = sink()
q = queue(mu, s)
gen = generator(q, lmbda)

# Schemalägg de första händelserna i signalList
send(GENERATE, 0.0, gen, [])  # Starta kundgenereringen
send(MEASUREMENT, 0.0, q, [])  # Starta mätningarna i kön


while simTime < stopTime:
    [simTime, signalType, dest, info] = heapq.heappop(signalList)
    dest.treatSignal(signalType, info)


###################################################
#
# Add code to print final result
#
###################################################

# Uppgift 3.5 & 3.6: Normaliserat histogram TILLSAMMANS med teoretiska pk
max_k = max(q.measuredValues)

# 1. Plotta histogrammet (Simulerade p_k)
bins = np.arange(-0.5, max_k + 1.5, 1)
plt.hist(
    q.measuredValues,
    bins=bins,
    density=True,
    rwidth=0.8,
    color="skyblue",
    edgecolor="black",
    label="Simulerat (Histogram)",
)

# 2. Plotta den teoretiska kurvan (Teoretiska p_k från pkMM1.py)
k_vals = np.array([i for i in range(0, max_k + 1)])
rho = lmbda / mu
pk_teoretisk = (rho**k_vals) * (1 - rho)

plt.plot(k_vals, pk_teoretisk, "r-o", linewidth=2, label="Teoretiskt (Kurva)")

plt.xlabel("Antal jobb i systemet (k)")
plt.ylabel("Sannolikhet (p_k)")
plt.title("M/M/1 Simulering vs Teori")
plt.legend()
plt.grid(axis="y", alpha=0.75)
plt.show()
