# import necessary libraries
import cv2
import numpy as np

def setupVidCap(vidCapId: int = 2):
    vidcap = cv2.VideoCapture(vidCapId)
    vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
    vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)
    return vidcap


def loadImage(vidcap: cv2.VideoCapture):
    _, image = vidcap.read()
    showImage(image)
    return image


def closeVidCap(vidcap: cv2.VideoCapture):
    vidcap.release()


def showImage(image, title: str = "Image", waitKeyTimeout:int = 0):
    cv2.imshow(title,image)
    cv2.waitKey(waitKeyTimeout)


def getDialatedEdges(vidcap: cv2.VideoCapture, image, kernel_size: tuple = (10,10), anchor_size: tuple = (4,4), lower_bound: tuple = (0,79,255), upper_bound: tuple = (9,90,255)):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    uglovi = 0
    konture = None

    while uglovi != 4:
        try:
            mask = cv2.inRange(hsv_image, lowerb=lower_bound, upperb=upper_bound)
            element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
            
            dilatation_dst = cv2.dilate(mask, element)
            contours, _ = cv2.findContours(dilatation_dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            uglovi = len(contours)
            
            print(f"treuntno: {uglovi}")
            showImage(dilatation_dst)
            konture = contours
            image = loadImage(vidcap=vidcap)
            
        except KeyboardInterrupt:
            break

    return konture


def findEdgePoints(contours):
    edgePoints = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        center = (np.round((x+x+w)/2).astype(np.uint16),np.round((y+y+h)/2).astype(np.uint16))
        
        edgePoints.append(center)
    
    return edgePoints


def doPerspectiveTransform(image, edgePoints: tuple):
    # coords = np.float32([[704,711],[821,63],[377,8],[111,548]])
    coords = np.float32(edgePoints)
    
    # TODO: check the oder in which coords are placed into
    #       edgePoints and adjust outut accordingly
    print(edgePoints)
    output = np.float32([[800,600],[800,0],[0,600],[0,0]])
    perspective_transform = cv2.getPerspectiveTransform(coords, output)
    
    dst = cv2.warpPerspective(image, perspective_transform, (800,600))
    
    return dst

if __name__ == "__main__":
    vidcap = setupVidCap()
    
    while True:
        try:
            img = loadImage(vidcap)
            
            contours = getDialatedEdges(vidcap, img, kernel_size=(21,21), anchor_size=(10,10))
            
            edges = findEdgePoints(contours=contours)

            shifted = doPerspectiveTransform(img, edgePoints=edges)
        
            showImage(shifted)
        except KeyboardInterrupt:
            print("exiting...")
            closeVidCap(vidcap)
