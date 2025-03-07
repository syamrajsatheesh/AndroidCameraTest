# USAGE
# python match.py --template template.png --images source.jpg

# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
# Importing Image class from PIL module 
from PIL import Image 

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--template", required=True, help="Path to template image")
ap.add_argument("-i", "--images", required=True,
	help="Path to images where template will be matched")
ap.add_argument("-v", "--visualize",
	help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())

# load the image image, convert it to grayscale, and detect edges
template = cv2.imread(args["template"])
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

# loop over the images to find the template in
#for imagePath in glob.glob(args["images"] + "/*.jpg"):
for imagePath in glob.glob(args["images"]):
	# load the image, convert it to grayscale, and initialize the
	# bookkeeping variable to keep track of the matched region
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	found = None

	# loop over the scales of the image
	for scale in np.linspace(0.2, 1.0, 20)[::-1]:
		# resize the image according to the scale, and keep track
		# of the ratio of the resizing
		resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
		r = gray.shape[1] / float(resized.shape[1])

		# if the resized image is smaller than the template, then break
		# from the loop
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break

		# detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		edged = cv2.Canny(resized, 50, 200)
		result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

		# check to see if the iteration should be visualized
		if args.get("visualize", False):
			# draw a bounding box around the detected region
			clone = np.dstack([edged, edged, edged])
			cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
				(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
			cv2.imshow("Visualize", clone)
			cv2.waitKey(1000)

		# if we have found a new maximum correlation value, then ipdate
		# the bookkeeping variable
		if found is None or maxVal > found[0]:
			found = (maxVal, maxLoc, r)

	# unpack the bookkeeping varaible and compute the (x, y) coordinates
	# of the bounding box based on the resized ratio
	(_, maxLoc, r) = found
	(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
	(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

	# draw a bounding box around the detected result and display the image
	cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
	cv2.imshow("Image", image)
	cv2.imwrite('box.png', image)
	#cv2.waitKey(0)

print ('Cordinates:',startX,startY,endX,endY)
print (found)
print ("Logo found")
#print (args["images"])

# Opens a image in RGB mode 
im = Image.open(args["images"]) 
  
# Size of the image in pixels (size of orginal image) 
# (This is not mandatory) 
#width, height = im.size 
  
# Setting the points for cropped image 
left = startX
top = startY
right = endX
bottom = endY
  
# Cropped image of above dimension 
# (It will not change orginal image) 
im1 = im.crop((left, top, right, bottom)) 
oldsize = im1.size
#print ('Oldsize:',oldsize)

#Resize result to template dimensions
im2 = Image.open(args["template"])
wid, hgt = im2.size


newsize = (wid, hgt) 
im1 = im1.resize(newsize) 
  
# Shows the image in image viewer 
#im1.show() 
im1.save('crop.png', 'PNG')


##Imagecompare with DeepAI
print ('Comparing..')
# Posting a local image file:
import requests
r = requests.post(
    "https://api.deepai.org/api/image-similarity",
    files={
        'image1': open('crop.png', 'rb'),
        'image2': open(args["template"], 'rb'),
    },
    headers={'api-key': 'cbbfac12-2fd1-481a-84be-8d0eb90ec21a'}
)
print(r.json())

  
