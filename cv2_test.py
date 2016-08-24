# -*- coding: utf-8 -*-
__author__ = 'Gongming Yang'
# Created and owned by:Gongming Yang
# Whelcome to use this tool to record attendance

import cv2

import cv2
import numpy as np

def get_im(src_im,rect=(0,0,100,100)):
    return cv2.getRectSubPix(src_im,(rect[2]-rect[0],rect[3]-rect[1]),((rect[2]+rect[0])/2,(rect[3]+rect[1])/2));

img = cv2.imread('picture_sanshidao.png',0)
im = cv2.imread('test2.png',0)
# im = get_im(img,(50,300,100,500))
# cv2.imshow('cropped', im)
cv2.imwrite('messigray.png',im)


# result = cv2.match_template(bigimg,img)
result = cv2.matchTemplate(im,img,cv2.TM_CCOEFF)
y,x = np.unravel_index(result.argmax(), result.shape)
im = get_im(img,(x,y,100+x,100+y))
cv2.imwrite('messigray.png',im)
print y,x
y,x = np.unravel_index(result.argmax(), result.shape)
print y,x

r = cv2.boundingRect(pts)
cv2.imwrite('roi.png', im[r[0]:r[0]+r[2], r[1]:r[1]+r[3]])
# All the 6 methods for comparison in a list
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

for meth in methods:
    img = img2.copy()
    method = eval(meth)

    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(img,top_left, bottom_right, 255, 2)

    # plt.subplot(121),plt.imshow(res,cmap = 'gray')
    # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    # plt.subplot(122),plt.imshow(img,cmap = 'gray')
    # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    # plt.suptitle(meth)

    # plt.show()