



#This function finds the largest region of a specific color, and then returns the coordinates of the center of mass of that region.  
#If that color is not present the coordinate (150,150) as this is the center of the image, and will direct the robot to remain
#moving straight 

#This fuction is designed to be called within the loop of a fuction that is capuring or playing video
#Specifically this fucntion works well with the capture.py file

#This define th function conDet


from __future__ import print_function

def conDet(windowName,img,count):

    # Python 2/3 compatibility
    

    import cv2
    import numpy as np

    # relative module
    import video

    # built-in module
    import sys


    #sets how much to blur
    filt=39
    #sets the darkness threshold
    thrs=50
    
    #This if statement only runs once to initialize the trackbars    
    if count==2:   

        def nothing(*arg):
            pass


        
        cv2.createTrackbar('r', windowName, 125, 255-thrs, nothing)
        cv2.createTrackbar('g', windowName, 26, 255-thrs, nothing)
        cv2.createTrackbar('b', windowName, 15, 255-thrs, nothing)
        cv2.createTrackbar('thresh', windowName, 8, 100, nothing) 

       
        

    r = cv2.getTrackbarPos('r', windowName)
    g = cv2.getTrackbarPos('g', windowName)
    b = cv2.getTrackbarPos('b', windowName)
    threshol = cv2.getTrackbarPos('thresh', windowName)
    

    lower=[b,g,r]
    lower=np.array(lower, dtype="uint8")
   
    #This function checks for a specific range of colors in the image img and returns a black and white image.  
    #White represents areas that are the specific range of colors
    #This image will be jaggeed looking
    mask=cv2.inRange(img,lower,lower+thrs)
 
    vis = img.copy()
    vis = np.uint8(vis)
    mask=np.uint8(mask)
    #Every value of of the colored image vis that is not the specified color is set to black in the color image
    vis[mask==0]=(0,0,0)
    
    
    #Make color image grey
    gray = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)
    #Blur image to smooth it
    blurred = cv2.GaussianBlur(gray, (filt, filt), 0)
    #Create black and white image where white areas are those that where brighter than a certain adjustable threshold 
    thresh = cv2.threshold(blurred, threshol, 255, cv2.THRESH_BINARY)[1]


    #Draw contours around white regions
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0]

    
    
    splotch = np.zeros((1,20),dtype=np.uint16)
    
    splotch=splotch[0]
    
    original=vis.copy()

    maxmass=0
    i=-1
    lastmax=0
    mass=0
    if cnts is None:
        cnts=[1,1]

    for d in cnts:
        i=i+1;
        
      
        try:   
            splotch[i] = cv2.contourArea(d)
            
    
            #returns index of max area contour
        
            mass = cv2.contourArea(d)
            if mass > maxmass:
                maxmass=mass
            lastmax=mass
        except:
            lastmax=mass

    print('maxmass %f' % (maxmass))
    # loop over the contours
    i=0
    for c in cnts:
        i=i+1;
        
  
        
        try:
            
            mass = cv2.contourArea(c)
            
            #Calculate center of mass of every contour.
            M = cv2.moments(c)
            
            cX = int(M["m10"] / mass)
            
            cY = int(M["m01"] / mass)
            
            
            #Draw the contour of the biggest contour in green and not biggest in red
            print("maxmass, mass %f, %f" %(maxmass, mass))
            if maxmass-5 <= mass:
                cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            if maxmass > mass:
                cv2.drawContours(img, [c], -1, (0, 0, 255), 2)


            cv2.putText(img, str(mass), (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        except:
            print("There are no contours for me to draw")
            
                
    print("\n")
    #An RGB array is 3D while a grayscale is 2D.  In order to show them together they must have the same dimentions
    #cvtColor using cv2.COLOR_GRAY2RGB will make grayscale images 3D.
    thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2RGB)
    #hstack means horizontal stack.  You can show videos sise by side using it.
    finalImg=np.hstack([img, vis, thresh]) 

    try:
        return(finalImg,[cX, cY])
    except:
        cX=150
        cY=150
        return(finalImg,[cX, cY])

