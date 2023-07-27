# import necessary libraries
import cv2
import numpy as np
import operator

def setupVidCap(vidCapId: int = 2):
    vidcap = cv2.VideoCapture(vidCapId)
    # vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280.0)
    # vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)
    
    vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    vidcap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # manual mode
    vidcap.set(cv2.CAP_PROP_EXPOSURE, 200)
    vidcap.set(cv2.CAP_PROP_AUTO_WB, 0)
    return vidcap


def loadImage(vidcap: cv2.VideoCapture):
    _, image = vidcap.read()
    # print('loaded')
    return image


def closeVidCap(vidcap: cv2.VideoCapture):
    vidcap.release()


def showImage(image: cv2.Mat, title: str = "Image.png", waitKeyTimeout:int = 0):
    cv2.imshow(title,image)
    return cv2.waitKey(waitKeyTimeout)


def getDialatedEdges(image: cv2.Mat, kernel_size: tuple, anchor_size: tuple, lower_bound: tuple, upper_bound: tuple):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lowerb=lower_bound, upperb=upper_bound)
    # showImage(mask)
    element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
    
    dilatation_dst = cv2.dilate(mask, element)
    # showImage(dilatation_dst)
    contours, _ = cv2.findContours(dilatation_dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # showImage(dilatation_dst)
    return contours


def findBall(image: cv2.Mat):
    # kernel_size = (11,11)
    # anchor_size = (1,1)
    lower_bound = (1,72,135)
    upper_bound = (17,180,255)

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lowerb=lower_bound, upperb=upper_bound)
    showImage(mask, waitKeyTimeout=1)
    
    # element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
    # dilatation_dst = cv2.dilate(mask, element)
    # showImage(dilatation_dst)
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # showImage(mask, waitKeyTimeout=1)
    try:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        return ((x+x+w)//2,(y+y+h)//2)
    except ValueError:
        # ball not in frame
        return None


def findMarkers(image: cv2.Mat):
    c = []

    while len(c) < 4:
        # lower_bound = (100, 100, 100)
        # upper_bound = (120, 150, 255)
        lower_bound = (108,82,73)
        upper_bound = (137,193,179)
        # upper_bound = (240, 255, 63) # hsv(240, 100%, 25%)
        # lower_bound = (210, 255, 127) # hsv(210, 100%, 50%)

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, lowerb=lower_bound, upperb=upper_bound)

        # showImage(mask)
        # showImage(mask, waitKeyTimeout=1)
        
        # opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_size)
        # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel_size)
        # showImage(mask, waitKeyTimeout=1)
        # showImage(closing, waitKeyTimeout=1)

        # element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
        # dilatation_dst = cv2.dilate(closing, element)
        # showImage(dilatation_dst, waitKeyTimeout=1)
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # showImage(dilatation_dst)
        c = sorted(contours, key=cv2.contourArea, reverse=True)
        # for contour in c:
        #     area = cv2.contourArea(contour=contour)
        #     if area > 1:
        #         print(area)
            # cv2.waitKey(0)
        # print(c[:4])
    
    return c[:4]


def definitelyGetDialatedEdges(vidcap: cv2.VideoCapture, image: cv2.Mat, kernel_size: tuple = (21,21), anchor_size: tuple = (10,10), lower_bound: tuple = (58, 100, 75), upper_bound: tuple = (67, 115, 179), corners = 4):
    while True:
        contours = getDialatedEdges(image, kernel_size, anchor_size, lower_bound, upper_bound)
        
        # print(f"treuntno: {len(contours)}")
        
        if len(contours) == corners:
            return contours

        image = loadImage(vidcap=vidcap)


def findEdgePoints(contours: cv2.Mat):
    edgePoints = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        center = (np.round((x+x+w)/2).astype(np.uint16),np.round((y+y+h)/2).astype(np.uint16))
        
        edgePoints.append(center)
    
    return edgePoints


def doPerspectiveTransform(image: cv2.Mat, edgePoints: tuple):
    coords = np.float32(edgePoints)

    output = np.float32([[800,600],[800,0],[0,600],[0,0]])
    perspective_transform = cv2.getPerspectiveTransform(coords, output)
    
    dst = cv2.warpPerspective(image, perspective_transform, (800,600))
    
    return dst


# def getFinalImage(vidcap: cv2.VideoCapture):
#     while True:
#         img = loadImage(vidcap)
#         # showImage(img)
#         # contours = definitelyGetDialatedEdges(vidcap=vidcap, image=img, kernel_size=(31,31), anchor_size=(15,15), lower_bound=(52, 108, 75), upper_bound=(67, 130, 179))
#         # showImage(img)
#         contours = definitelyGetDialatedEdges(vidcap=vidcap, image=img, kernel_size=(21,21), anchor_size=(8,8), lower_bound=(40, 65, 0), upper_bound=(75, 150, 200))
    
#         edges = findEdgePoints(contours=contours)
        
#         shifted = doPerspectiveTransform(img, edgePoints=edges)
        
#         if showImage(shifted) == ord('y'):
#             cv2.destroyAllWindows()
#             return edges
        # if showImage(shifted) == ord('c'):
        #     # detect the orange ball
        #     # grayscale = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
        #     # optimized = shifted & 0b11000000
        #     # showImage(shifted)
        #     ball_contours = getDialatedEdges2(shifted, (21, 21), (8,8), (25, 200, 0), (50, 255, 255))

        # elif showImage(shifted) == ord('f'):
        #     cv2.destroyAllWindows()
        #     return (edges, 'f')


def getFinalImage2(vidcap: cv2.VideoCapture):
    while True:
        img = loadImage(vidcap=vidcap)
        markers = findMarkers(img)
        edges = findEdgePoints(contours=markers)
        transformed = doPerspectiveTransform(img, edgePoints=edges)
        # showImage(transformed)
        res = showImage(transformed)
        if res == ord('y'):
            cv2.destroyAllWindows()
            return edges
        elif res == ord('l'):
            print(edges)
        elif res == ord('f'):
            # print("to be flipped")
            nep = edges

            tmp = nep[1]
            nep[1] = nep[0]
            nep[0] = tmp

            tmp = nep[2]
            nep[2] = nep[3]
            nep[3] = tmp
            
            # new_image = doPerspectiveTransform(img, edgePoints=nep)
            # showImage(new_image)
            return nep


if __name__ == "__main__":
    # ask the user to confirm the suggested perspective transform is done well
    vidcap = setupVidCap(0)
    tableEdges = getFinalImage2(vidcap=vidcap)
    print(tableEdges)
    while True:
        img = loadImage(vidcap=vidcap)
        transformed = doPerspectiveTransform(img, edgePoints=tableEdges)
        findBall(transformed)
