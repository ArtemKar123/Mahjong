############## Playing Card Detector Functions ###############
#
# Author: Evan Juras
# Date: 9/5/17
# Description: Functions and classes for CardDetector.py that perform
# various steps of the card detection algorithm


# Import necessary packages
import numpy as np
import cv2
import time

### Constants ###

# Adaptive threshold levels
BKG_THRESH = 60
CARD_THRESH = 30

DIFF_MAX = 20000
CARD_MAX_AREA = 1000000
CARD_MIN_AREA = 10000 #DO NOT TOUCH
count = 1

font = cv2.FONT_HERSHEY_SIMPLEX

### Structures to hold query card and train card information ###

class Query_tile:
    """Structure to store information about query cards in the camera image."""

    def __init__(self):
        self.contour = [] # Contour of card
        self.width, self.height = 0, 0 # Width and height of card
        self.corner_pts = [] # Corner points of card
        self.center = [] # Center point of card
        self.warp = [] # 200x300, flattened, grayed, blurred image
        self.img = [] # Thresholded, sized image of card
        self.best_match = "Unknown" # Best matched
        self.diff = 0 # Difference between rank image and best matched train rank image

class Train:
    """Structure to store information about train rank images."""

    def __init__(self):
        self.img = [] # Thresholded, sized rank image loaded from hard drive
        self.name = "Placeholder"


### Functions ###
def load_patterns(filepath):
    """Loads rank images from directory specified by filepath. Stores
    them in a list of Train_ranks objects."""

    train_tiles = []
    i = 0

    #for Rank in ['m11','m2','m3','m4','m5','m6','m7','m8','m9','p1','p2','p3','p4','p5','p6','p7','p8','p9','s1','s2','s3','s4','s5','s6','s7','s8','s9','dr','dg','dw','we','ww','ws','wn']:
    for Rank in ['Chun','Haku','Man1','Man2','Man3','Man4','Man5','Man6','Man7','Man8','Man9','Pin1','Pin2','Pin3','Pin4','Pin5','Pin6','Pin7','Pin8','Pin9','Sou1','Sou2','Sou3','Sou4','Sou5','Sou6','Sou7','Sou8','Sou9','Ton','Shaa','Nan','Pei','Hatsu']:
        train_tiles.append(Train())
        train_tiles[i].name = Rank
        filename = Rank + '.jpg'
        train_tiles[i].img = cv2.imread(filepath+filename, cv2.IMREAD_GRAYSCALE)
        train_tiles[i].img = cv2.resize(train_tiles[i].img, (200,300), 0, 0)
        i = i + 1

    return train_tiles


def preprocess_image(image):
    """Returns a grayed, blurred, and adaptively thresholded camera image."""

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)

    # The best threshold level depends on the ambient lighting conditions.
    # For bright lighting, a high threshold must be used to isolate the cards
    # from the background. For dim lighting, a low threshold must be used.
    # To make the card detector independent of lighting conditions, the
    # following adaptive threshold method is used.
    #
    # A background pixel in the center top of the image is sampled to determine
    # its intensity. The adaptive threshold is set at 50 (THRESH_ADDER) higher
    # than that. This allows the threshold to adapt to the lighting conditions.
    img_w, img_h = np.shape(image)[:2]
    bkg_level = gray[int(img_h/100)][int(img_w/2)]
    thresh_level = bkg_level + BKG_THRESH

    retval, thresh = cv2.threshold(blur,thresh_level,255,cv2.THRESH_BINARY)
    return thresh

def find_tiles(thresh_image):
    """Finds all card-sized contours in a thresholded camera image.
    Returns the number of cards, and a list of card contours sorted
    from largest to smallest."""

    # Find contours and sort their indices by contour size
    #dummy
    cnts,hier = cv2.findContours(thresh_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i : cv2.contourArea(cnts[i]),reverse=True)

    # If there are no contours, do nothing
    print('LEN',len(cnts))
    if len(cnts) == 0:
        return [], []

    # Otherwise, initialize empty sorted contour and hierarchy lists
    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts),dtype=int)

    # Fill empty lists with sorted contour and sorted hierarchy. Now,
    # the indices of the contour list still correspond with those of
    # the hierarchy list. The hierarchy array can be used to check if
    # the contours have parents or not.
    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    # Determine which of the contours are cards by applying the
    # following criteria: 1) Smaller area than the maximum card size,
    # 2), bigger area than the minimum card size, 3) have no parents,
    # and 4) have four corners
    for i in range(len(cnts_sort)):
        size = cv2.contourArea(cnts_sort[i])
        peri = cv2.arcLength(cnts_sort[i],True)
        approx = cv2.approxPolyDP(cnts_sort[i],0.01*peri,True)
        #print(size)
        print(len(approx), size, hier_sort[i][3])
        if ((size < CARD_MAX_AREA) and (size > CARD_MIN_AREA)
            and (hier_sort[i][3] == -1) and (len(approx) <= 6)):
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card

def preprocess_tile(contour, image):
    """Uses contour to find information about the query card. Isolates rank
    and suit images from the card."""

    # Initialize new Query_card object
    qTile = Query_tile()

    qTile.contour = contour

    # Find perimeter of card and use it to approximate corner points
    peri = cv2.arcLength(contour,True)
    approx = cv2.approxPolyDP(contour,0.01*peri,True)
    pts = np.float32(approx)
    qTile.corner_pts = pts

    # Find width and height of card's bounding rectangle
    x,y,w,h = cv2.boundingRect(contour)
    qTile.width, qTile.height = w, h

    # Find center point of card by taking x and y average of the four corners.
    average = np.sum(pts, axis=0)/len(pts)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    qTile.center = [cent_x, cent_y]

    # Warp card into 200x300 flattened image using perspective transform
    qTile.warp = flattener(image, pts, w, h)
    qTile.img = qTile.warp
    #qTile.img = cv2.flip(qTile.img,0)

    return qTile

def match_tile(qTile, train_tiles):
    """Finds best rank and suit matches for the query card. Differences
    the query card rank and suit images with the train rank and suit images.
    The best match is the rank or suit image that has the least difference."""

    best_match_diff = 30000
    best_match_name = "Unknown"
    best_name = "Unknown"
    i = 0

    # If no contours were found in query card in preprocess_card function,
    # the img size is zero, so skip the differencing process
    # (card will be left as Unknown)
    print('a', len(qTile.img))

    if (len(qTile.img) != 0):
        print('b')
        # Difference the query card rank image from each of the train rank images,
        # and store the result with the least difference
        for Tile in train_tiles:
                diff_img = cv2.absdiff(qTile.img, Tile.img)
                tile_diff = int(np.sum(diff_img)/255)
                #print(Tile.name,'diff =', tile_diff)
                if tile_diff < best_match_diff:
                    #print(Tile.name,'diff =', tile_diff)
                    best_diff_img = diff_img
                    best_match_diff = tile_diff
                    best_name = Tile.name

    # Combine best rank match and best suit match to get query card's identity.
    # If the best matches have too high of a difference value, card identity
    # is still Unknown
    if (best_match_diff < DIFF_MAX):
        best_match_name = best_name

    # Return the identiy of the card and the quality of the suit and rank match
    return best_match_name, best_match_diff


def draw_results(image, qTile):
    """Draw the card name, center point, and contour on the camera image."""

    x = qTile.center[0]
    y = qTile.center[1]
    cv2.circle(image,(x,y),15,(27,150,194),-1)

    name = qTile.best_match

    # Draw card name twice, so letters have black outlines
    cv2.putText(image,(name),(x-60,y-10),font,5,(0,225,225),15,10)
    #cv2.putText(image,(name'),(x-60,y-10),font,1,(50,200,200),2,cv2.LINE_AA)


    # Can draw difference value for troubleshooting purposes
    # (commented out during normal operation)
    #r_diff = str(qCard.rank_diff)
    #s_diff = str(qCard.suit_diff)
    #cv2.putText(image,r_diff,(x+20,y+30),font,0.5,(0,0,255),1,cv2.LINE_AA)
    #cv2.putText(image,s_diff,(x+20,y+50),font,0.5,(0,0,255),1,cv2.LINE_AA)

    return image

def flattener(image, pts, w, h):
    """Flattens an image of a card into a top-down 200x300 perspective.
    Returns the flattened, re-sized, grayed image.
    See www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/"""
    temp_rect = np.zeros((4,2), dtype = "float32")

    s = np.sum(pts, axis = 2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    # Need to create an array listing points in order of
    # [top left, top right, bottom right, bottom left]
    # before doing the perspective transform

    if w <= 0.8*h: # If card is vertically oriented
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h: # If card is horizontally oriented
        temp_rect[0] = tr
        temp_rect[1] = br
        temp_rect[2] = bl
        temp_rect[3] = tl

    # If the card is 'diamond' oriented, a different algorithm
    # has to be used to identify which point is top left, top right
    # bottom left, and bottom right.

    if w > 0.8*h and w < 1.2*h: #If card is diamond oriented
        # If furthest left point is higher than furthest right point,
        # card is tilted to the left.
        if pts[1][0][1] <= pts[3][0][1]:
            # If card is titled to the left, approxPolyDP returns points
            # in this order: top right, top left, bottom left, bottom right
            temp_rect[0] = pts[1][0] # Top left
            temp_rect[1] = pts[0][0] # Top right
            temp_rect[2] = pts[3][0] # Bottom right
            temp_rect[3] = pts[2][0] # Bottom left

        # If furthest left point is lower than furthest right point,
        # card is tilted to the right
        if pts[1][0][1] > pts[3][0][1]:
            # If card is titled to the right, approxPolyDP returns points
            # in this order: top left, bottom left, bottom right, top right
            temp_rect[0] = pts[0][0] # Top left
            temp_rect[1] = pts[3][0] # Top right
            temp_rect[2] = pts[2][0] # Bottom right
            temp_rect[3] = pts[1][0] # Bottom left


    maxWidth = 200
    maxHeight = 300

    # Create destination array, calculate perspective transform matrix,
    # and warp card image
    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0, maxHeight-1]], np.float32)
    M = cv2.getPerspectiveTransform(temp_rect,dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)



    return warp
