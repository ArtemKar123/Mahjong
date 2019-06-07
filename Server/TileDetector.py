import cv2
import numpy as np
import time
import os
import Tiles



def start(imgName, num):
    tile_names = []
    tile_x = []

    font = cv2.FONT_HERSHEY_SIMPLEX

    path = os.path.dirname(os.path.abspath(__file__))
    train_tiles = Tiles.load_patterns( path + '/new/')
    image = cv2.imread(imgName)


    pre_proc = Tiles.preprocess_image(image)
    cv2.imwrite('pre_proc.jpg', pre_proc)
    cnts_sort, cnt_is_card = Tiles.find_tiles(pre_proc)

    if len(cnts_sort) != 0:

        tiles = []
        k = 0

        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):
                tiles.append(Tiles.preprocess_tile(cnts_sort[i],image,i))

                tiles[k].best_match,tiles[k].diff = Tiles.match_tile(tiles[k],train_tiles,i)
                tile_x.append(tiles[k].coord)
        #        print(tiles[k].best_match)
                tile_names.append(tiles[k].best_match)
        #        print('---------------')
                image = Tiles.draw_results(image, tiles[k])
                k = k + 1
            if (len(tiles) != 0):
                temp_cnts = []
                for i in range(len(tiles)):
                    temp_cnts.append(tiles[i].contour)
                    cv2.drawContours(image,temp_cnts, -1, (27,150,194), 5)
        tile_names, tile_x = sort(tile_names,tile_x)
        #print(tile_names)
    cv2.imwrite('found.jpg', image)
    return tile_names
def sort(tiles,x):
    isDone = False
    while not isDone:
        isDone = True
        for i in range(len(tiles)-1):
            if x[i] > x[i+1]:
                a = x[i]
                x[i] = x[i+1]
                x[i+1] = a
                a = tiles[i]
                tiles[i] = tiles[i+1]
                tiles[i+1] = a
                isDone = False
    return tiles,x
