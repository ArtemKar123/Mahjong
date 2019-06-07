import numpy as np
import cv2

BKG_THRESH = 60
CARD_THRESH = 30

DIFF_MAX = 300000
CARD_MAX_AREA = 1000000
CARD_MIN_AREA = 20000 #DO NOT TOUCH
count = 1

font = cv2.FONT_HERSHEY_SIMPLEX


class Query_tile:

    def __init__(self):
        self.contour = []
        self.width, self.height = 0, 0
        self.corner_pts = []
        self.center = []
        self.warp = []
        self.img = []
        self.best_match = "Unknown"
        self.diff = 0
        self.x = 0
        self.coord = 0

class Train:

    def __init__(self):
        self.img = []
        self.name = "Placeholder"


def load_patterns(filepath):

    train_tiles = []
    i = 0

    for Rank in ['Chun (2)', 'Chun (3)', 'Chun (4)', 'Chun (5)', 'Chun (6)', 'Chun', 'Haku (2)', 'Haku', 'Hatsu (2)', 'Hatsu (3)', 'Hatsu (4)', 'Hatsu (5)', 'Hatsu (6)', 'Hatsu', 'Man1 (2)', 'Man1', 'Man11', 'Man12', 'Man13', 'Man2 (2)', 'Man2', 'Man21', 'Man22', 'Man23', 'Man24', 'Man25', 'Man26', 'Man3', 'Man31', 'Man32', 'Man33', 'Man34', 'Man4', 'Man41', 'Man42', 'Man43', 'Man44', 'Man5 (2)', 'Man5', 'Man51', 'Man52', 'Man53', 'Man54', 'Man55', 'Man6 (2)', 'Man6 (3)', 'Man6', 'Man61', 'Man62', 'Man63', 'Man64', 'Man65', 'Man66', 'Man7', 'Man71', 'Man72', 'Man73', 'Man74', 'Man75', 'Man76', 'Man8 (2)', 'Man8', 'Man81', 'Man82', 'Man83', 'Man84', 'Man85', 'Man86', 'Man9', 'Man91', 'Man92', 'Man93', 'Man94', 'Man95', 'Nan (2)', 'Nan (3)', 'Nan (4)', 'Nan (5)', 'Nan (6)', 'Nan', 'Nan1', 'Nan2', 'Nan3', 'Pei (2)', 'Pei (3)', 'Pei (4)', 'Pei (5)', 'Pei (6)', 'Pei', 'Pin1', 'Pin11', 'Pin12', 'Pin13', 'Pin14', 'Pin15', 'Pin16', 'Pin2 (2)', 'Pin2', 'Pin21', 'Pin22', 'Pin23', 'Pin24', 'Pin25', 'Pin3', 'Pin31', 'Pin32', 'Pin33', 'Pin4', 'Pin41', 'Pin42', 'Pin43', 'Pin44', 'Pin5', 'Pin51', 'Pin52', 'Pin53', 'Pin6', 'Pin61', 'Pin62', 'Pin63', 'Pin7', 'Pin71', 'Pin72', 'Pin73', 'Pin8', 'Pin81', 'Pin82', 'Pin83', 'Pin84', 'Pin85', 'Pin9', 'Pin91', 'Pin92', 'Pin93', 'Pin94', 'Pin95', 'Pin96', 'Shaa (2)', 'Shaa (3)', 'Shaa (4)', 'Shaa (5)', 'Shaa', 'Sou1 (2)', 'Sou1', 'Sou11', 'Sou12', 'Sou2', 'Sou21', 'Sou22', 'Sou23', 'Sou24', 'Sou3 (2)', 'Sou3 (3)', 'Sou3', 'Sou31', 'Sou32', 'Sou4 (2)', 'Sou4 (3)', 'Sou4 (4)', 'Sou4', 'Sou41', 'Sou42', 'Sou5 (2)', 'Sou5 (3)', 'Sou5', 'Sou51', 'Sou6 (2)', 'Sou6 (3)', 'Sou6', 'Sou61', 'Sou62', 'Sou7 (2)', 'Sou7 (3)', 'Sou7 (4)', 'Sou7 (5)', 'Sou7', 'Sou71', 'Sou8 (2)', 'Sou8', 'Sou81', 'Sou82', 'Sou9 (2)', 'Sou9 (3)', 'Sou9', 'Sou91', 'Sou92', 'Ton (2)', 'Ton (3)', 'Ton (4)', 'Ton (5)', 'Ton (6)', 'Ton']:
        train_tiles.append(Train())
        train_tiles[i].name = Rank
        filename = Rank + '.jpg'
        train_tiles[i].img = cv2.imread(filepath+filename, cv2.IMREAD_GRAYSCALE)
        train_tiles[i].img = cv2.resize(train_tiles[i].img, (300,500), 0, 0)
        i = i + 1

    return train_tiles


def preprocess_image(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV )
    h_min = np.array((0, 0, 172), np.uint8)
    h_max = np.array((255, 209, 255), np.uint8)
    thresh = cv2.inRange(hsv, h_min, h_max)


    #gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(thresh,(5,5),0)

    img_w, img_h = np.shape(image)[:2]
    bkg_level = thresh[int(img_h/100)][int(img_w/2)]
    thresh_level = bkg_level + BKG_THRESH

    retval, thresh = cv2.threshold(blur,thresh_level,255,cv2.THRESH_BINARY)
    return thresh

def find_tiles(thresh_image):
    cnts,hier = cv2.findContours(thresh_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i : cv2.contourArea(cnts[i]),reverse=True)

    #print('LEN',len(cnts))
    if len(cnts) == 0:
        return [], []

    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts),dtype=int)

    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    for i in range(len(cnts_sort)):
        size = cv2.contourArea(cnts_sort[i])
        peri = cv2.arcLength(cnts_sort[i],True)
        approx = cv2.approxPolyDP(cnts_sort[i],0.01*peri,True)
        #print(len(approx), size, hier_sort[i][3])
        if ((size < CARD_MAX_AREA) and (size > CARD_MIN_AREA)
            and (hier_sort[i][3] == -1) and (len(approx) <= 16)):
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card

def preprocess_tile(contour, image, i):

    qTile = Query_tile()
    pts = []
    qTile.contour = contour
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    temporary = box
    peri = cv2.arcLength(box,True)
    approx = cv2.approxPolyDP(box,0.01*peri,True)
    pts = np.float32(approx)
    qTile.corner_pts = pts

    #print(pts)

    x,y,w,h = cv2.boundingRect(contour)
    qTile.width, qTile.height = w, h
    qTile.x = x
    qTile.coord = x + 5*y

    average = np.sum(pts, axis=0)/len(pts)

    print(average)
    cent_x = int(average[0][0])
    cent_y = int(average[0][1])
    qTile.center = [cent_x, cent_y]
    qTile.warp = flattener(image, pts, w, h,1)
    qTile.img = qTile.warp




    return qTile

def match_tile(qTile, train_tiles,num):

    best_match_diff = 300000
    best_match_name = "Unknown"
    best_name = "Unknown"
    i = 0

    #print('a', len(qTile.img))
    #a = 'found tile ' + str(num) + '.jpg'
    #cv2.imwrite(a,qTile.img)
    if (len(qTile.img) != 0):
        #print('b')
        for Tile in train_tiles:
                diff_img = cv2.absdiff(qTile.img, Tile.img)
                tile_diff = int(np.sum(diff_img)/255)
                #print(Tile.name,'diff =', tile_diff)
                if tile_diff < best_match_diff:
                #    print(Tile.name,'diff =', tile_diff)
                    best_diff_img = diff_img
                    best_match_diff = tile_diff
                    best_name = Tile.name
        #print('--')
    if (best_match_diff < DIFF_MAX):
        best_match_name = best_name
    if best_match_name[0:3] == 'Nan':
        best_match_name = 'Nan'
    elif best_match_name[0:4] == 'Haku':
        best_match_name = 'Haku'
    elif best_match_name[0:3] == 'Pei':
        best_match_name = 'Pei'
    elif best_match_name[0:4] == 'Shaa':
        best_match_name = 'Shaa'
    elif best_match_name[0:5] == 'Hatsu':
        best_match_name = 'Nan'
    elif best_match_name[0:3] == 'Ton':
        best_match_name = 'Ton'
    elif best_match_name[0:4] == 'Chun':
        best_match_name = 'Chun'
    else:
        best_match_name = best_match_name[0:4]
    return best_match_name, best_match_diff


def draw_results(image, qTile):

    x = qTile.center[0]
    y = qTile.center[1]

    name = qTile.best_match
    coord = qTile.coord
    #cv2.putText(image,(str(coord)),(x,y-10),font,1,(0,0,0),1,1)
    return image

def flattener(image, pts, w, h,c):
    temp_rect = np.zeros((4,2), dtype = "float32")

    s = np.sum(pts, axis = 2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]


    if w <= 0.8*h: #vertically oriented
        #print('-------------------1')
        temp_rect[0] = tl
        temp_rect[1] = tr
        temp_rect[2] = br
        temp_rect[3] = bl

    if w >= 1.2*h: #horizontally oriented
        #print('-------------------2')
        temp_rect[0] = tr
        temp_rect[1] = br
        temp_rect[2] = bl
        temp_rect[3] = tl


    if w > 0.8*h and w < 1.2*h: #diamond oriented
        #print('3')
        if pts[1][0][1] <= pts[3][0][1]:
        #    print('-------------------31')
            temp_rect[0] = pts[1][0] # Top left 0
            temp_rect[1] = pts[2][0] # Top right 1
            temp_rect[2] = pts[3][0] # Bottom right 2
            temp_rect[3] = pts[0][0] # Bottom left 3

        if pts[1][0][1] > pts[3][0][1]:
        #    print('-------------------32')
            temp_rect[0] = pts[2][0] # Top left
            temp_rect[1] = pts[3][0] # Top right
            temp_rect[2] = pts[0][0] # Bottom right
            temp_rect[3] = pts[1][0] # Bottom left


    maxWidth = 300
    maxHeight = 500

    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0, maxHeight-1]], np.float32)
    M = cv2.getPerspectiveTransform(temp_rect,dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    if c==1:
        warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)


    return warp
