import cv2
import numpy as np
import time
import os
import Tiles



def start(imgName):
    tile_names = []

    font = cv2.FONT_HERSHEY_SIMPLEX

    path = os.path.dirname(os.path.abspath(__file__))
    train_tiles = Cards.load_patterns( path + '/new/')
    image = cv2.imread(imgName)


    pre_proc = Cards.preprocess_image(image)

    cnts_sort, cnt_is_card = Cards.find_tiles(pre_proc)

    if len(cnts_sort) != 0:

        tiles = []
        k = 0

        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):

                tiles.append(Cards.preprocess_tile(cnts_sort[i],image,i))

                tiles[k].best_match,tiles[k].diff = Cards.match_tile(tiles[k],train_tiles,i)
                print(tiles[k].best_match)
                tile_names.append(tiles[k].best_match)
                print('---------------')
                image = Cards.draw_results(image, tiles[k])
                k = k + 1
            if (len(tiles) != 0):
                temp_cnts = []
                for i in range(len(tiles)):
                    temp_cnts.append(tiles[i].contour)
                    cv2.drawContours(image,temp_cnts, -1, (27,150,194), 5)
        print(tile_names)
    cv2.imwrite('found.jpg', image)
    return tile_names
