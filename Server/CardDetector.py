############## Python-OpenCV Playing Card Detector ###############
#
# Author: Evan Juras
# Date: 9/5/17
# Description: Python script to detect and identify playing cards
# from a PiCamera video feed.
#

# Import necessary packages
import cv2
import numpy as np
import time
import os
import Cards
import VideoStream


def start(imgName):
### ---- INITIALIZATION ---- ###
# Define constants and initialize variables

## Camera settings
    tile_names = []
    IM_WIDTH = 1280
    IM_HEIGHT = 720
    FRAME_RATE = 10

## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

## Define font to use
    font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize camera object and video feed from the camera. The video stream is set up
# as a seperate thread that constantly grabs frames from the camera feed.
# See VideoStream.py for VideoStream class definition
## IF USING USB CAMERA INSTEAD OF PICAMERA,
## CHANGE THE THIRD ARGUMENT FROM 1 TO 2 IN THE FOLLOWING LINE:

#videostream = VideoStream.VideoStream((IM_WIDTH,IM_HEIGHT),FRAME_RATE,2,0).start()
#time.sleep(3) # Give the camera time to warm up

# Load the train rank and suit images
    path = os.path.dirname(os.path.abspath(__file__))
    #train_tiles = Cards.load_patterns( path + '/Card_Imgs/')
    train_tiles = Cards.load_patterns( path + '/Regular/')

### ---- MAIN LOOP ---- ###
# The main loop repeatedly grabs frames from the video stream
# and processes them to find and identify playing cards.

#cam_quit = 0 # Loop control variable

# Begin capturing frames
#while cam_quit == 0:

    # Grab frame from video stream
    #image = videostream.read()
    image = cv2.imread(imgName)


    # Start timer (for calculating frame rate)
    #t1 = cv2.getTickCount()

    # Pre-process camera image (gray, blur, and threshold it)
    pre_proc = Cards.preprocess_image(image)



    # Find and sort the contours of all cards in the image (query cards)
    cnts_sort, cnt_is_card = Cards.find_tiles(pre_proc)

    # If there are no contours, do nothing
    if len(cnts_sort) != 0:

        # Initialize a new "cards" list to assign the card objects.
        # k indexes the newly made array of cards.
        tiles = []
        k = 0

        # For each contour detected:
        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):
                # Create a card object from the contour and append it to the list of cards.
            # preprocess_card function takes the card contour and contour and
                # determines the cards properties (corner points, etc). It generates a
                # flattened 200x300 image of the card, and isolates the card's
                # suit and rank from the image.
                tiles.append(Cards.preprocess_tile(cnts_sort[i],image))

                # Find the best rank and suit match for the card.
                tiles[k].best_match,tiles[k].diff = Cards.match_tile(tiles[k],train_tiles)
                print(tiles[k].best_match)
                tile_names.append(tiles[k].best_match)
                print('---------------')
                # Draw center point and match result on the image.
                image = Cards.draw_results(image, tiles[k])
                k = k + 1
        # Draw card contours on image (have to do contours all at once or
        # they do not show up properly for some reason)
            if (len(tiles) != 0):
                temp_cnts = []
                for i in range(len(tiles)):
                    temp_cnts.append(tiles[i].contour)
                    cv2.drawContours(image,temp_cnts, -1, (27,150,194), 20)
        print(tile_names)

    # Draw framerate in the corner of the image. Framerate is calculated at the end of the main loop,
    # so the first time this runs, framerate will be shown as 0.
#cv2.putText(image,"FPS: "+str(int(frame_rate_calc)),(10,26),font,0.7,(255,0,255),2,cv2.LINE_AA)

# Finally, display the image with the identified cards!
#out = open("found.jpg", "wb")
#out.write(image)
#out.close()

    cv2.imwrite('found.jpg', image)
    return tile_names
#cv2.imshow("Card Detector",image)
#cv2.imwrite('found.jpg',cv2.Canny(imageToShow,1280,720))
#cv2.imshow("CardDetector",cv2.imread('found.jpg'))

    # Calculate framerate
#t2 = cv2.getTickCount()
#time1 = (t2-t1)/freq
#frame_rate_calc = 1/time1

    # Poll the keyboard. If 'q' is pressed, exit the main loop.
#key = cv2.waitKey(1) & 0xFF
#if key == ord("q"):
#cam_quit = 1


# Close all windows and close the PiCamera video stream.
#cv2.destroyAllWindows()
#videostream.stop()
#start('First.jpg')
