import heapq
import random
import numpy as np

signalList = []

def send(signalType, evTime, destination, info):
    heapq.heappush(signalList, [evTime, signalType, destination, info])


READY = 1
ARRIVAL = 2
MEASUREMENT = 3
simTime = 0.0
stopTime = 123456.0
   
    
class larger():
    def __gt__(self, other):
        return False
    

class generator(larger):
    def __init__(self, sendTo):
        self.sendTo = sendTo
    def treatSignal(self, x, info):
        if x == READY:
            send(ARRIVAL, simTime, self.sendTo, simTime)
            send(READY, simTime + random.expovariate(1.0), self, None)


class queue(larger):
    def __init__(self, sendTo):
        self.numberInQueue = 0
        self.measuredValues = []
        self.sendTo = sendTo;
        self.numberBlocked = 0
        self.numberServed = 0
    def serviceTime(self):
        return random.expovariate(1.0)
    def treatSignal(self, x, info):
        if x == ARRIVAL:
            if self.numberInQueue == 0:
                send(READY, simTime + self.serviceTime(), self, None)
                self.numberInQueue = self.numberInQueue + 1
                self.info = info
                self.numberServed = self.numberServed + 1
            else:
                self.numberBlocked = self.numberBlocked + 1
        elif x == READY:
            self.numberInQueue = self.numberInQueue - 1
            send(READY, simTime, self.sendTo, self.info)
        elif x == MEASUREMENT:
            self.measuredValues.append(self.numberInQueue)
            send(MEASUREMENT, simTime + random.expovariate(0.5), self, None)

            
class sink(larger):
    def __init__(self):
        self.times = []
    def treatSignal(self, x, info):
        self.times.append(simTime - info)

         
s = sink()
q = queue(s)
gen = generator(q)


send(READY, 0, gen, [])
send(MEASUREMENT, 10.0, q, [])


while simTime < stopTime:
    [simTime, signalType, dest, info] = heapq.heappop(signalList)
    dest.treatSignal(signalType, info)


print('Mean number in queue: ', np.mean(q.measuredValues))
print('Mean time in queue: ', np.mean(s.times))
print('Probability of blocking: ', q.numberBlocked/(q.numberServed + q.numberBlocked))





