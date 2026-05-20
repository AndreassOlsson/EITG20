import heapq
import random
import numpy as np
from queue import Queue

signalList = []

def send(signalType, evTime, destination, info):
    heapq.heappush(signalList, (evTime, signalType, destination, info))

GENERATE = 1
ARRIVAL = 2
MEASUREMENT = 3
DEPARTURE = 4

simTime = 0.0
stopTime = 100000.0
        

class larger():
    def __gt__(self, other):
        return False


class generator(larger):
    def __init__(self, lambda1):
        self.lambda1 = lambda1
        send(GENERATE, self.arrivalTime(), self, None)
    def arrivalTime(self):
        return simTime + random.expovariate(self.lambda1)
    def treatSignal(self, x, info):
        if x == GENERATE:
            send(ARRIVAL, simTime, sendTo(self), simTime)
            send(GENERATE, self.arrivalTime(), self, None)



class queue(larger):
    def __init__(self, mu):
        self.measuredValues = []
        self.buffer = Queue(maxsize=0)
        self.mu = mu 
        send(MEASUREMENT, simTime + random.expovariate(1), self, None)
    def serviceTime(self):
        return simTime + random.expovariate(self.mu)
    def treatSignal(self, x, info):
        if x == ARRIVAL: 
            if self.buffer.empty():
                send(DEPARTURE, self.serviceTime(), self, None) 
            self.buffer.put(info)
        elif x == DEPARTURE:
            tid = self.buffer.get()
            send(ARRIVAL, simTime, sendTo(self), tid)
            if not self.buffer.empty():
                send(DEPARTURE,  self.serviceTime(), self, None)  
        elif x == MEASUREMENT:
            self.measuredValues.append(self.buffer.qsize())
            send(MEASUREMENT, simTime + random.expovariate(1), self, [])

            
class sink(larger):
    def __init__(self):
        self.T = [] 
    def treatSignal(self, x, info):
        self.T.append(simTime - info)

# Below the queueing network is set up. 

# A vector where q[i] is node i is created. The first position in the list is not 
# used so that q[i] correspondst to node number i, for convenience.  
q = [None, queue(10), queue(14), queue(22), queue(9), queue(11)] 

# Sinks and generators are created.
sink1 = sink()
sink2 = sink()
gen1 = generator(7.5)
gen2 = generator(10)

# The function sendTo(source) gives the routing in the queueing network
def sendTo(source):
    if source == q[1]:
        return q[3]
    elif source == q[2]:
        return q[3]
    elif source == q[3]:
        if random.random() < 0.4:
            return q[4]
        else:
            return q[5]
    elif source == q[4]:
        return sink1
    elif source == q[5]:
        return sink2
    elif source == gen1:
        return q[1]
    elif source == gen2:
        return q[2]


# The main simulation loop
while simTime < stopTime:
    [simTime, signalType, dest, info] = heapq.heappop(signalList)
    dest.treatSignal(signalType, info)

# The mean number of customers in each node i printed:  
for i in range(1,6):
    print(i, ': ', np.mean(q[i].measuredValues))
    

    




