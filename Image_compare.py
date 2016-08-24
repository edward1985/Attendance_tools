# -*- coding: utf-8 -*-
__author__ = 'Gongming Yang'
# Created and owned by:Gongming Yang
# Whelcome to use this tool to record attendance

from PIL import Image,ImageChops,ImageFilter
import time

b=Image.open(u'20160402_181032.jpg')
im=Image.open(u'test2.png')
im1=Image.open(u'test1.png')

f = ImageChops.difference(im, im1).getbbox()


im=Image.new("L",(20,20))
im.paste(im1,(0,0))
im.show()

ctime = time.time();
diff = ImageChops.difference(a, b);

print time.time()-ctime;

print '---';



from PIL import Image
im = Image.open("bride.jpg")
im.rotate(45).show();

#data = im.tostring()
#im.fromstring(data)

#get bytes
print im.tobytes()
t = im.tobitmap()

#get Pixel
im = Image.open('image.gif')
rgb_im = im.convert('RGB')
r, g, b = rgb_im.getpixel((1, 1))
print r, g, b

# Find edges
from PIL import Image, ImageFilter
image = Image.open('your_image.png')
image = image.filter(ImageFilter.FIND_EDGES)
image.save('new_name.png')