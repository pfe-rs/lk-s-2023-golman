import cv2
import numpy as np

def mnk(x: list, y: list):
    if len(x) < 2:
        return 0, 0

    xy = np.multiply(x, y)
    x2 = np.multiply(x, x)

    b = (np.sum(y) - np.sum(xy) * (len(x) / np.sum(x)))/(np.sum(x) - np.sum(x2) * (len(x) / np.sum(x)))
    a = (np.sum(y) - np.sum(x) * b) / len(x)

    return a,b

if __name__ == "__main__":
    # x = [8, 3,  2, 10, 11, 3, 6, 5, 6, 8]
    # y = [4, 12, 1, 12, 9,  4, 9, 6, 1, 14]

    x = []
    y = []

    while True:
        x.append(int(input("x> ")))
        y.append(int(input("y> ")))

        n,k = mnk(x, y)
        print(f"k:{k}, n:{n}")
