import random
import math
import datetime

def randId():
    digits = [i for i in range(0, 10)]
    random_str=""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    return random_str

def randSize():
    rand_num = random.random()
    size = ""
    if rand_num < 0.5:
        return size == "small"
    else:
        return size == "big"

def randCrowdThresh():
    return random.randint(5, 20)

def randPheromoneThresh():
    return random.randint(30, 60)

class FishData:
    def __init__(self, genesis, lifetime=None, parentId=None, crowThreshold=None, pheromoneThreshold=None):
        self.id = randId()
        self.size = "small" # just an initiate
        self.state = "in-pond"
        self.status = "alive"
        self.genesis = genesis ## Pond name
        self.crowdThreshold = crowThreshold or randCrowdThresh()
        self.pheromone = 0
        self.pheromoneThresh = pheromoneThreshold or randPheromoneThresh()
        self.x, self.y = random.randint(50, 650), random.randint(50, 650)
        self.parentId = parentId
        
        self.lifetime =  50
        self.parentId = parentId or randId()
        self.x, self.y = random.randint(50, 650), random.randint(50, 650)
        self.timestamp = datetime.datetime.now()
    def getId(self):
        return self.id
    def getSize(self):
        return self.size
    def getState(self):
        return self.state
    def getStatus(self):
        return self.status
    def getGenesis(self):
        return self.genesis
    def getcrowdThreshold(self):
        return self.crowdThreshold
    def pheromone(self):
        return self.pheromone
    def pheromoneThresh(self):
        return self.pheromoneThresh
    def getLifetime(self):
        return self.lifetime
    def parentId(self):
        return self.parentId

    def __str__(self):
        if self.parentId:
            return self.id + "Size: " + str(self.size) + " Genesis: " + self.genesis + " Parent: " + self.parentId + " Lifetime: " + str(self.lifetime)
        else:
            return self.id + "Size: " + str(self.size) + " Genesis: " + self.genesis + " Lifetime: " + str(self.lifetime)
