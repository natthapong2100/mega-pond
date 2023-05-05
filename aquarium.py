
   
# import pygame
# import sys
# import random
# import os
# # from src.Fish import Fish
# from Pond import Pond
# os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1000,290)

# pond = Pond()
# pond.run()

import os
import sys
from vivisystem.client import VivisystemClient
from Pond import Pond
from FishStore import FishStore, connect_to_redis

os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (1000, 290)

if __name__ == "__main__":
    pond_name = sys.argv[1] if len(sys.argv) > 1 else "mega-pond"
    
    db_i = int(sys.argv[2]) if len(sys.argv) > 1 and len(sys.argv) > 2 else 0
    r = connect_to_redis(db=db_i)
    fishStore = FishStore(r, db_i=db_i)
    vivi_client = VivisystemClient("ws://127.0.0.1:5000", pond_id=pond_name) # ws://localhost:5000 ( -> may be not for macOS)
    pond = Pond(fishStore=fishStore, vivi_client=vivi_client, name=pond_name)
    
    print(f"{pond_name} is starting...")
    pond.run()
    
