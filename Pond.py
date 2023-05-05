import enum
from re import S
# from turtle import update
from PondData import PondData
from Fish import Fish, FishContainer
# from run import Dashboard
from dashboard import Dashboard
from pondDashboard import PondDashboard
from random import randint
from FishData import FishData
from FishStore import FishStore

from random import randint, choice
from typing import Union
from vivisystem.client import VivisystemClient
from vivisystem.models import VivisystemPond, VivisystemFish, EventType

import random
import pygame
import pygame_menu
import sys
import consts
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic, QtGui
import threading
from Client import Client
class Pond:

    def __init__(self, fishStore: FishStore, vivi_client: VivisystemClient ,name):
        
        # if genesis == None:
        #     genesis = "mega-pond"
        # else:
        #     pass
        
        self.name = name
        
        
        self.fish_container = FishContainer()
        self.fishes = []
        self.moving_sprites = pygame.sprite.Group()
        self.bombImage = pygame.image.load("./assets/images/sprites/bomb.png")
        self.bombImage = pygame.transform.scale(self.bombImage, (128,128))
        self.msg = ""
        self.pondData = PondData(self.name)
        self.network = None
        self.bombTime = 0
        self.displaybomb = False
        
        # NEW
        self.vivi_client = vivi_client
        self.connected_ponds = {}
        self.fishStore: FishStore = fishStore
        self.pheromone = self.fishStore.get_pheromone()
        
        # events
        self.UPDATE_EVENT = pygame.USEREVENT + 1
        self.PHEROMONE_EVENT = pygame.USEREVENT + 2
        self.SHARK_EVENT = pygame.USEREVENT + 3
        self.SEND_STATUS_EVENT = pygame.USEREVENT + 4
        
        for fish in self.fishStore.get_fishes().values():
            self.fish_container.add_fish(fish)
        self.fish_container.update_display()

    def getPondData(self):
        return self.pondData

    def getPopulation(self):
        return self.fish_container.get_total()
    
    def randombomb(self):
        dead = randint(0, len(self.fishes)-1)
        return self.fishes[dead]

    # def bombAttack(self, screen, fish):
    #     screen.blit(self.bombImage, (fish.getFishx(), fish.getFishy())) 
    #     self.removeFish(fish)
    #     fish.die()
           

    def spawnFish(self, parentFish: Fish = None):
        tempFish = Fish(100, 100, self.name, parentFish.getId() if parentFish else "-")
        self.fishStore.add_fish(tempFish.fishData)
        self.fish_container.add_fish(tempFish)
        
    def pheromoneCloud(self ):
        if self.fish_container.get_total() > consts.FISHES_POND_LIMIT:
            return

        self.pheromone += randint(20, 50) * consts.BIRTH_RATE # make it random ***
        # self.pheromone += 20 # set it initially
        self.fishStore.set_pheromone(self.pheromone)

    def addFish(self, fish: Fish): #from another pond
        self.fishStore.add_fish(fish.fishData)
        self.fish_container.add_fish(fish)

    
    def removeFish(self, fish):
        print("---------------------------FISH SHOULD BE REMOVED-------------------------")
        print(fish.getId())
        self.fish_container.remove_fish(fish.getGenesis(), fish.getId())
        fish.die()

    def update(self, injectPheromone=False):
        self.fish_container.update_fishes(self.update_fish)
        self.fishStore.set_pheromone(self.pheromone)
    
    def update_fish(self, f: Fish, injectPheromone = False):
        f.updateLifeTime() # decrease life time by 1 sec (change to increase instead)
        if f.fishData.status == "dead":
            self.removeFish(f)
            return
        
        if f.isPregnant(self.pheromone):  # check that pheromone >= pheromone threshold
            newFish = Fish(50, randint(50, 650), f.getGenesis(), f.getId())
            self.fishStore.add_fish(newFish.fishData)
            self.addFish(newFish)
            self.pheromone -= f.fishData.crowdThreshold // 2
        
        if self.connected_ponds:
            if f.getGenesis() != self.name and f.in_pond_sec >= 5 and not f.gaveBirth:
                newFish = Fish(50,randint(50, 650),f.fishData.genesis, f.fishData.id)
                self.addFish( newFish )
                newFish.giveBirth() ## not allow baby fish to breed
                print("ADD FISH MIGRATED IN POND FOR 5 SECS")
                f.giveBirth()
        
            if f.getGenesis() == self.name and f.in_pond_sec <= 15:
                pass
            elif f.getGenesis() == self.name and f.in_pond_sec >= 15:
                if self.connected_ponds:
                    random_pond = random.choice(list(self.connected_ponds))
                    self.vivi_client.migrate_fish(
                        random_pond, f.toVivisystemFish())
                    self.removeFish(f)
            else:
                if self.getPopulation() > f.getCrowdThresh():
                    random_pond = random.choice(list(self.connected_ponds))
                    self.vivi_client.migrate_fish(
                        random_pond, f.toVivisystemFish())
                    self.removeFish(f)
        if injectPheromone:
            self.pheromoneCloud()
        
    
    def handle_migrate(self, fish: VivisystemFish):
        fish = Fish.fromVivisystemFish(fish)
        self.addFish(fish)

    def handle_status(self, pond: VivisystemPond):
        self.connected_ponds[pond.name] = pond

    def handle_disconnect(self, pond_name: str):
        if pond_name in self.connected_ponds:
            del self.connected_ponds[pond_name]
            print(pond_name, "Disconnected")
 
            
    # Main program
    def run(self):
        mapHandler = {
            EventType.MIGRATE: self.handle_migrate,
            EventType.STATUS: self.handle_status,
            EventType.DISCONNECT: self.handle_disconnect
        }
        for event, handler in mapHandler.items():
            self.vivi_client.handle_event(event, handler)


        dashboard: Union[None, Dashboard] = None
        vivisystem_dashboard: Union[None, PondDashboard] = None

        pygame.init()
        screen = pygame.display.set_mode((1280, 720))

        bg = pygame.image.load("./assets/images/background/bg.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        pygame.display.set_caption(f"Fish Haven Project: {self.name}")
        clock = pygame.time.Clock()
        # start_time = pygame.time.get_ticks()
        # pregnant_time = pygame.time.get_ticks()

        self.spawnFish()

        app = QApplication(sys.argv)
        other_pond_list = []

        running = True
        pygame.time.set_timer(self.UPDATE_EVENT, 1000)
        pygame.time.set_timer(self.SEND_STATUS_EVENT, 2000)
        pygame.time.set_timer(self.PHEROMONE_EVENT, 15000)
        pygame.time.set_timer(self.SHARK_EVENT, 15000)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.time.set_timer(self.UPDATE_EVENT, 0)
                    pygame.time.set_timer(self.PHEROMONE_EVENT, 0)
                    pygame.time.set_timer(self.SHARK_EVENT, 0)
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        dashboard = Dashboard(self.fish_container) # Our Dashboard
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                    elif event.key == pygame.K_LEFT:
                        vivisystem_dashboard = PondDashboard(self.network) # PondDashboard
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                elif event.type == self.UPDATE_EVENT:
                    self.update()
                elif event.type == self.PHEROMONE_EVENT:
                    self.pheromoneCloud()
                elif event.type == self.SHARK_EVENT:
                    pass
                elif event.type == self.SEND_STATUS_EVENT:
                    self.vivi_client.send_status(VivisystemPond(
                        name=self.name, pheromone=self.pheromone, total_fishes=self.getPopulation()))

            if dashboard:
                dashboard.update_dashboard(self.pheromone)
            if vivisystem_dashboard:
                vivisystem_dashboard.update_dashboard()

            self.fish_container.update_display()

            screen.fill((0, 0, 0))
            screen.blit(bg, [0, 0])
            self.fish_container.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
        