# import necessary libraries
import cv2
import numpy as np


def setupVidCap(vidCapId: int = 2):
    vidcap = cv2.VideoCapture(vidCapId)
    vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280.0)
    vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)
    return vidcap


def loadImage(vidcap: cv2.VideoCapture):
    _, image = vidcap.read()
    print('loaded')
    return image


def closeVidCap(vidcap: cv2.VideoCapture):
    vidcap.release()


def showImage(image: cv2.Mat, title: str = "Image.png", waitKeyTimeout:int = 0):
    cv2.imshow(title,image)
    return cv2.waitKey(waitKeyTimeout)


def getDialatedEdges(image: cv2.Mat, kernel_size: tuple, anchor_size: tuple, lower_bound: tuple, upper_bound: tuple):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lowerb=lower_bound, upperb=upper_bound)
    element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
    
    dilatation_dst = cv2.dilate(mask, element)
    contours, _ = cv2.findContours(dilatation_dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # showImage(dilatation_dst)
    return contours


def definitelyGetDialatedEdges(vidcap: cv2.VideoCapture, image: cv2.Mat, kernel_size: tuple = (21,21), anchor_size: tuple = (10,10), lower_bound: tuple = (58, 100, 75), upper_bound: tuple = (67, 115, 179)):
    while True:
        contours = getDialatedEdges(image, kernel_size, anchor_size, lower_bound, upper_bound)
        
        # print(f"treuntno: {len(contours)}")
        
        if len(contours) == 4:
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
    # print(edgePoints)
    output = np.float32([[800,600],[800,0],[0,600],[0,0]])
    perspective_transform = cv2.getPerspectiveTransform(coords, output)
    
    dst = cv2.warpPerspective(image, perspective_transform, (800,600))
    
    return dst


def getFinalImage(vidcap: cv2.VideoCapture):
    while True:
        img = loadImage(vidcap)
                    
        contours = definitelyGetDialatedEdges(vidcap=vidcap, image=img, kernel_size=(31,31), anchor_size=(15,15), lower_bound=(52, 108, 75), upper_bound=(67, 130, 179))
        
        edges = findEdgePoints(contours=contours)
        
        shifted = doPerspectiveTransform(img, edgePoints=edges)
        
        if(showImage(shifted) == ord('y')):
            cv2.destroyAllWindows()
            return edges


def list_ports():
    """
    Test the ports and returns a tuple with the available ports 
    and the ones that are working.
    """
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." %dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return available_ports,working_ports


if __name__ == "__main__":
    # ask the user to confirm the suggested perspective transform is done well
    # list_ports()
    vidcap = setupVidCap(0)
    edges_to_use = getFinalImage(vidcap=vidcap)
    
    while True:
        try:
            # detect ball and act accordingly
            print(edges_to_use)
            # pass
        except KeyboardInterrupt:
            print("exiting...")
            # closeVidCap(vidcap)
            # pass
