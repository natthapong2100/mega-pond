import pygame
import time
import random
import consts

from FishData import FishData
from vivisystem.models import VivisystemFish
from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List

# initiate FISH_ASSETS_PATH, pond_assets, fish_sprites_container
FISH_ASSETS_PATH = "./assets/images/sprites"
pond_assets = {"local-pond", "foreign-pond", "matrix-pond", "doo-pond", "khor-pond", "aquagang"} # foreign(=1) + 5 = 6
fish_sprites_container = {p: ([], []) for p in pond_assets}

def load_sprites_right(pond_name):
    path = f"{FISH_ASSETS_PATH}/{pond_name}/"
    for i in range(1, 5):
        fish_path = path + str(i) + ".png"
        img = pygame.image.load(str(fish_path))
        img = pygame.transform.scale(img, (100, 100))
        img = pygame.transform.flip(img, True, False)
        fish_sprites_container[pond_name][0].append(img)


def load_sprites_left(pond_name):
    path = f"{FISH_ASSETS_PATH}/{pond_name}/"
    for i in range(1, 5):
        fish_path = path + str(i) + ".png"
        img = pygame.image.load(fish_path)
        img = pygame.transform.scale(img, (100, 100))
        fish_sprites_container[pond_name][1].append(img)


def load_sprites():
    for pond in pond_assets:
        load_sprites_left(pond)
        load_sprites_right(pond)


load_sprites()

SCREEN_WIDTH = 1180
SCREEN_HEIGHT = 300

class Fish(pygame.sprite.Sprite):
    def __init__(self, pos_x=None, pos_y=None, genesis="mega-pond", parent = None, data: FishData = None):
        super().__init__()
        
        
        self.fishData = data or FishData(genesis, parent)
         
        #swimming controller
        # self.direction = "RIGHT"
        self.face = 1
        self.attack_animation = False
        self.sprites = [] #Main sprite
        self.leftSprite = []
        self.rightSprite = []
        self.loadSprite()

        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.left = self.fishData.x # pos_x
        self.rect.top = self.fishData.y
        self.rect.right = self.fishData.x + 100
        self.attack_animation = True
        self.current_sprite = 0
        self.rect = self.image.get_rect()
        # self.rect.topleft = [pos_x, pos_y]
        self.rect.topleft = [self.fishData.x, self.fishData.y]
        self.in_pond_sec = 0
        self.gaveBirth = False
        self.speed = 0.05 # speed (initial)
        # self.speed = float(random.randrange(5, 20)) / 100 # speed (random)
        
    @classmethod
    def fromVivisystemFish(cls, fish: VivisystemFish):
        fish_data = FishData(fish.genesis, fish.lifetime, fish.parent_id,
                             fish.crowd_threshold, fish.pheromone_threshold)
        return cls(data=fish_data)

    def toVivisystemFish(self) -> VivisystemFish:
        return VivisystemFish(fish_id=self.getId(), parent_id=self.fishData.getId(), genesis=self.fishData.getGenesis(), crowd_threshold=self.getCrowdThresh(),
                              pheromone_threshold=self.fishData.pheromoneThresh, lifetime=self.getLifetime())

    def getFishData(self):
        return self.fishData

    def getFishTLPos(self):
        return self.rect.topleft
    
    def getFishx(self):
        return self.rect.left

    def getFishy(self):
        return self.rect.top

    def die(self):
        self.kill()


    def flipSprite(self):

        if self.face == 1:
            self.sprites=self.rightSprite
        elif self.face == -1:
            self.sprites=self.leftSprite
            
        self.current_sprite = 0

    # def loadSprite(self):
    #     path = "./assets/images/sprites/"
        
    #     if self.fishData.genesis == "mega-pond":
    #         path += "local-pond/"
    #     else:
    #         path += "foreign-pond/"
        
    #     # if self.fishData.genesis == "mega-pond":
    #     #     path += "local-pond/"
    #     # else:
    #     #     path += "foreign-pond/"

    #     self.loadSpriteRight(path, self.sprites)
    #     self.loadSpriteLeft(path)
    #     self.loadSpriteRight(path, self.rightSprite)
    
    def loadSprite(self):
        path = "local-pond"
        if (
            self.fishData.genesis != "mega-pond" 
            and self.fishData.genesis 
            not in pond_assets
        ):
            path = "foreign-pond"
        elif self.fishData.genesis in pond_assets:
            path = self.fishData.genesis

        self.sprites = fish_sprites_container[path][0]
        self.leftSprite = fish_sprites_container[path][1]
        self.rightSprite = fish_sprites_container[path][0]
        self.current_sprite = 0

    # def loadSpriteRight(self, path, spriteContainer):
    #     for i in range(1, 5):
    #         fish_path = path + str(i) + ".png"
    #         img = pygame.image.load(str(fish_path))
    #         img = pygame.transform.scale(img, (100, 100))
    #         img = pygame.transform.flip(img, True, False)
    #         spriteContainer.append(img)
    #     self.current_sprite = 0
        

    # def loadSpriteLeft(self, path):
    #     for i in range(1, 5):
    #         fish_path = path + str(i) + ".png"
    #         img = pygame.image.load(fish_path)
    #         img = pygame.transform.scale(img, (100, 100))
    #         self.leftSprite.append(img)
    #     self.current_sprite = 0
    
    def updateAnimation(self):
        if self.attack_animation == True:
            self.current_sprite += self.speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]
    
    def update(self):
        self.move(3) # speed at horizontal = 3
  

    def move(self, speed_x):
        if self.rect.left <= 0:
            # print("chon left")
            self.face = 1
            # print("x axis" + str(self.rect.left) + str(self.face))
            self.flipSprite()
        
        elif self.rect.left >= 1180:
            # print("chon right")
            self.face = -1
            # print("x axis" + str(self.rect.left)  + str(self.face))
            self.flipSprite()

        speed_x = random.randint(1, 5) * self.face

        self.rect.x += speed_x
        self.updateAnimation()

    def increasePheromone(self, n):
        self.fishData.pheromone += n

    def migrate(self):
        pass
    
    def getId(self):
        return self.fishData.id
    
    def getLifetime(self):
        return self.fishData.lifetime

    def isPregnant(self, current_pheromone):
        if current_pheromone < self.fishData.pheromoneThresh:
            return False
        self.fishData.pheromoneThresh += self.fishData.pheromoneThresh
        return True

    def updateLifeTime(self):
        self.in_pond_sec += 1
        self.fishData.lifetime -= 1
        
        if self.fishData.lifetime <= 60:
            self.fishData.size = "small"
        elif self.fishData.lifetime >= 30 and self.fishData.lifetime <=50:
            self.fishData.size = "medium"
        elif self.fishData.lifetime >= 20:
            self.fishData.size = "large"
        elif self.fishData.lifetime == 0:
            self.fishData.status = "dead"


    def resetPheromone(self):
        self.fishData.pheromone = 0
    
    def getGenesis(self):
        return self.fishData.genesis

    def getCrowdThresh(self):
            return self.fishData.crowdThreshold

    def giveBirth(self):
        self.gaveBirth = True
        

class FishContainer(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # self.fishes['mega-pond']['113230'] = {Fish1, Fish2, ...}
        self.fishes: DefaultDict[str, Dict[str, Fish]] = defaultdict(dict)
        self.percentage: Dict[str, float] = {}
        self.limit = consts.FISHES_DISPLAY_LIMIT
        self.last_updated_time = time.time()

        # self.population_history['mega-pond'] = [(timestamp, count), ...]
        self.population_history: DefaultDict[str,
                                             List[List[tuple]]] = defaultdict(list)

    def add_fish(self, fish: Fish):
        self.fishes[fish.getGenesis()][fish.getId()] = fish
        self.update_percentages()
        if self.get_total() < self.limit:
            self.add(fish)

    def remove_fish(self, genesis, fish_id):
        if genesis in self.fishes:
            self.fishes[genesis].pop(fish_id, None)
            self.update_percentages()

    def update_fishes(self, update: Callable[[Fish], None]):
        for genesis in list(self.fishes.keys()):
            for fish in list(self.fishes[genesis].values()):
                update(fish)

    def get_total(self) -> int:
        return sum([len(self.fishes[key]) for key in self.fishes.keys()])

    def get_percentages(self) -> Dict[str, float]:
        return self.percentage

    def update_percentages(self):
        for genesis in self.fishes.keys():
            total = self.get_total()
            self.percentage[genesis] = len(
                self.fishes[genesis]) / total if total > 0 else 0

    def update_population_history(self, current_time):
        if current_time - self.last_updated_time <= 2:
            return
        for genesis in self.fishes.keys():
            self.population_history[genesis].append(
                (current_time, len(self.fishes[genesis])))
        self.last_updated_time = current_time

    def get_population_history(self):
        return self.population_history

    def update_display(self):
        current_time = time.time()
        self.update_population_history(current_time)

        self.last_update_time = current_time

        total_fishes = self.get_total()
        if total_fishes > self.limit:
            self.empty()
            for fish_type in self.fishes.keys():
                fish_type_limit = int(self.percentage[fish_type] * self.limit)
                for i, (fish_id, fish_sprite) in enumerate(self.fishes[fish_type].items()):
                    if i < fish_type_limit:
                        self.add(fish_sprite)
                    else:
                        break

        self.update()

    def getFishes(self):
        fishes = []
        for fish in self.fishes['mega-pond'].values():
            fishes.append(fish)
        return fishes
