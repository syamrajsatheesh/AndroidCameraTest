# Importing Image class from PIL module 
from PIL import Image 

#Resize result to template dimensions
im = Image.open('41.jpg')
wid, hgt = im.size

wid2 = int(wid/3)
hgt2 = int(hgt/3)
print (wid2,hgt2)

newsize2 = (wid2, hgt2) 
im1 = im.resize(newsize2)

im1.save('41.png', 'PNG')