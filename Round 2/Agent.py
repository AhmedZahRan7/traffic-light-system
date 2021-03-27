from math import floor
class directions:
    SOUTH = 0
    WEST = 1
    NORTH = 2
    EAST = 3
DETECTORS = [1,3,2,4,5,7,6,8]

MAX = 8
DEF = 3
MIN = 2
class Agent:
    continousZeroState = 0
    maxQuantum = [MAX,MAX,MAX,MAX]
    minQuantum = [MIN,MIN,MIN,MIN]
    defaultQuantum = [DEF,DEF,DEF,DEF]
    alpha = .6
    avgTime = [0,0,0,0,0,0,0,0,0]
    lanesLoad = [0,0,0,0]
    quantums = [defaultQuantum[0],defaultQuantum[1],defaultQuantum[2],defaultQuantum[3]]
    currentQuantum = 0
    currentOpen = directions.SOUTH
    state = []

    def reset(self):
        self.continousZeroState = 0
        self.maxQuantum = [MAX,MAX,MAX,MAX]
        self.minQuantum = [MIN,MIN,MIN,MIN]
        self.defaultQuantum = [DEF,DEF,DEF,DEF]
        self.alpha = .5
        self.avgTime = [0,0,0,0,0,0,0,0,0]
        self.lanesLoad = [0,0,0,0]
        self.quantums = [self.defaultQuantum[0],self.defaultQuantum[1],self.defaultQuantum[2],self.defaultQuantum[3]]
        self.currentQuantum = 0
        self.currentOpen = directions.SOUTH
        self.state = []
    
    def modifyAvg(self,idx):
        if self.state[idx] != -1:
            if idx > 4:
                self.state[idx] = self.state[idx] * 3
            self.avgTime[idx] = self.state[idx] * (self.alpha) + self.avgTime[idx] * (1-self.alpha)
        else:
            #TODO#
            return
        
    def expAvg(self,dir):
        self.modifyAvg(DETECTORS[dir])
        self.modifyAvg(DETECTORS[dir+4])

    def calculateAvgTime(self):
        self.expAvg(directions.SOUTH)
        self.expAvg(directions.NORTH)
        self.expAvg(directions.EAST)
        self.expAvg(directions.WEST)
    
    
    def modifyQuantums(self):
        loadSum = sum(self.lanesLoad)
        for i in range (0,4):
            if i == self.currentOpen:
                continue
            if loadSum==0:
                self.quantums[i] = self.defaultQuantum[i]
            else:    
                self.quantums[i] = max(self.minQuantum[i], min(self.maxQuantum[i],floor(4*self.defaultQuantum[i]*self.lanesLoad[i]/loadSum)))
                if self.quantums[i] == self.maxQuantum[i]:
                    self.maxQuantum[i] += .5
                if self.state[i+5] == 0:
                        self.quantums[i] = self.minQuantum[i]

    def reCalacLoad(self):
        self.lanesLoad[directions.SOUTH] = self.avgTime[DETECTORS[directions.SOUTH]] + self.avgTime[DETECTORS[directions.SOUTH+4]]
        self.lanesLoad[directions.NORTH] = self.avgTime[DETECTORS[directions.NORTH]] + self.avgTime[DETECTORS[directions.NORTH+4]]
        self.lanesLoad[directions.EAST] = self.avgTime[DETECTORS[directions.EAST]] + self.avgTime[DETECTORS[directions.EAST+4]]
        self.lanesLoad[directions.WEST] = self.avgTime[DETECTORS[directions.WEST]] + self.avgTime[DETECTORS[directions.WEST+4]]

    def selectNewLane(self):
        return self.lanesLoad.index(max(self.lanesLoad))


    def select_action(self, state, conn=None, vehicle_ids=None):
        if sum(state) <= 0:
            self.continousZeroState += 1
        else :
            self.continousZeroState = 0
        
        # if self.continousZeroState > 8:
        #     self.reset()
        
        self.state = state
        self.currentQuantum+=1
        self.calculateAvgTime()
        self.reCalacLoad()
        self.modifyQuantums()

        # print(self.lanesLoad)
        # print(self.quantums)
        if self.currentQuantum >= self.quantums[self.currentOpen]:
            self.currentQuantum = 0
            self.currentOpen = self.selectNewLane()
            return self.currentOpen
        else:
            return self.currentOpen
