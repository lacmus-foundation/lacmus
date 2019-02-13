import numpy as np
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
ap.add_argument("-s", "--size", required = False, type=int , default=500, help = "imege wide size, default = 500")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])

final_wide = args["size"]
r = float(final_wide) / image.shape[1]
dim = (final_wide, int(image.shape[0] * r))
image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
chennals = cv2.split(hsv)
chennal_h = chennals[0]
chennal_s = chennals[1]
chennal_v = chennals[2]

cv2.imshow('original',image)
cv2.imshow('gray',gray)
cv2.imshow('hsv',hsv)
cv2.imshow('h-chenal', chennal_h)
cv2.imshow('s-chenal', chennal_s)
cv2.imshow('v-chenal', chennal_v)
cv2.waitKey(0)