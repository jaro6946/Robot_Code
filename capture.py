#This file defines a function take which sets up the camera and controls the robot.  Any CV functions you want to use are nested within this function


import cv2
#The * allows the function take to accept any number of input arguments.  cvProcess will be an array that holds them all.
def take(*cvProcess):
	# import the necessary packages
	from picamera.array import PiRGBArray
	from picamera import PiCamera
	import time
	
	#import RPi.GPIO as GPIO
	import RPi.GPIO as GPIO

	#set whether you want to start with manual or automattic control
	auto=1

	
	#These three variables are used in the control of the robot.  Their values must be set prior to their use
	flag=0
	hflag=0
	lastSpeed=0
	
	#One of my electric motors was faster than the other, so this vlue represents that difference
	offset=10
	
	#defines a function that limits a number to be within 0 to 100.
	def limit(inp):
		if inp<0:
			out=0
		elif inp>100:
			out=100
		else:
			out=inp
		return(out)

	def forward():
		GPIO.output(R_Motor_1, GPIO.LOW)
		GPIO.output(R_Motor_2, GPIO.HIGH)
		GPIO.output(L_Motor_1, GPIO.LOW)
		GPIO.output(L_Motor_2, GPIO.HIGH)

	def backward():
		GPIO.output(R_Motor_1, GPIO.HIGH)
		GPIO.output(R_Motor_2, GPIO.LOW)
		GPIO.output(L_Motor_1, GPIO.HIGH)
		GPIO.output(L_Motor_2, GPIO.LOW)

	def right():
		GPIO.output(R_Motor_1, GPIO.HIGH)
		GPIO.output(R_Motor_2, GPIO.LOW)
		GPIO.output(L_Motor_1, GPIO.LOW)
		GPIO.output(L_Motor_2, GPIO.HIGH)

	def left():

		GPIO.output(R_Motor_1, GPIO.LOW)
		GPIO.output(R_Motor_2, GPIO.HIGH)
		GPIO.output(L_Motor_1, GPIO.HIGH)
		GPIO.output(L_Motor_2, GPIO.LOW)


	#GPIO Pin numbering
	R_Motor_1=20
	R_Motor_2=19
	R_Motor_PWM=18

	L_Motor_1=21
	L_Motor_2=22
	L_Motor_PWM=13

	#GPIO set up
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(R_Motor_1, GPIO.OUT)
	GPIO.setup(R_Motor_2, GPIO.OUT)
	GPIO.setup(L_Motor_1, GPIO.OUT)
	GPIO.setup(L_Motor_2, GPIO.OUT)
	GPIO.setup(R_Motor_PWM, GPIO.OUT)
	GPIO.setup(L_Motor_PWM, GPIO.OUT)

	#PWM pin setup 
	pwmR = GPIO.PWM(R_Motor_PWM, 1000)
	pwmL = GPIO.PWM(L_Motor_PWM, 1000)

	
	#This will be the name of the window that will show the video feed
	windowName="video" 

	


	#Pi Camera setup
	camera = PiCamera()
	camera.resolution = (300, 250)
	camera.framerate = 15
	rawCapture = PiRGBArray(camera, size=(300, 250))
	
	count=1
	# allow the camera to warmup
	time.sleep(0.1)
	# Capture frames from the camera.  
	#The first loop runs through just to open a named window
	# This named window allows us to define track bars in the second loop interation and run our nested CV functions
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		
		image = frame.array
		image=cv2.flip(image,0)


		if count==2:
			def nothing(*arg):
				pass
			cv2.createTrackbar('Speed', windowName, 50, 100-offset, nothing)
		
		
		#Run a image processing function if desired.  Modify if you would like to run multiple
		if count > 1:
			if len(cvProcess)==1:
				#You can save the function in the input argument to another name and then run it, as I have done here
				function=cvProcess[0]
				image, coordinates=function(windowName,image,count)
		
		speed = cv2.getTrackbarPos('Speed', windowName)
		
		# show the frame
		cv2.imshow(windowName, image)
		key = cv2.waitKey(1) & 0xFF
	 
		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)
		
		count=count+1
		# if the `q` key was pressed, break from the loop
		if count==1:
			speed = 0
		
			
		# The following is code to control the motors in two mode.  With one I can control the robot with my keyboard, the other is autonomous  
		#I used the Qunqi L298N Motor Driver

		if auto>0: #If True, manual control is engaged
			
			if key==ord('w'):
				
				forward()
			
				#The following code changes the speed only if the speed has been updated on the trackbar
				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed+offset)
					lastSpeed=speed
				#flag is used to make sure the stop order is not automatically changed back to the current speed on the trackbar
				flag=1

				print("forward")

			#' ' represents the space bar
			elif key==ord(' '):

				backward()

				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed+offset)
					lastSpeed=speed
				flag=1
				print("backward")


			elif key==ord('a'):
				
				left()

				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed)
					lastSpeed=speed
				flag=1
				print("left")


			elif key==ord('d'):
				
				right()

				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed)
					lastSpeed=speed
				flag=1
				print("right")

			elif key==ord('s'):
				if lastSpeed != 0:
					pwmR.start(0)
					pwmL.start(0)
					lastSpeed=0
				flag=0
				print("stop")


			elif key == 27:
				break

			elif key == ord('p'):
				if lastSpeed != 0:
					pwmR.start(0)
					pwmL.start(0)
					lastSpeed=0
				flag=1
				time.sleep(5)

			elif key== ord('l'):
				auto=0
				key=0

			#Ensures our speed is being updated to reflect trackbar changes
			elif lastSpeed != speed and flag==1:
				pwmL.start(speed)
				pwmR.start(speed)
				lastSpeed=speed

				


		if auto==0:  #If True, set to autonomous mode
			
			x_val=coordinates[0]-150
			
			

			if key == 27:
				break

			#Pauses for 5 seconds
			elif key == ord('p'):
				pwmR.start(0)
				pwmL.start(0)
				time.sleep(5)

			#Turns back on manual control
			elif key== ord('l'):
				key=0
				auto=1
				if lastSpeed != 0:
					pwmR.start(0)
					pwmL.start(0)
					lastSpeed=0
				flag=0

			#hflag or hysterisis flag allow for hysterisis in this autonomous system.
			elif -100<x_val<100 and hFlag==1:
				
				forward()

				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed+offset)
					lastSpeed=speed
				print("forward")

			elif x_val<-50:
				
				left()

				if lastSpeed != 30:
					pwmR.start(30)
					pwmL.start(30+offset)
					lastSpeed=speed
				print("left")
				

			elif x_val>50:
				
				right()

				if lastSpeed != 30:
					pwmR.start(30)
					pwmL.start(30+offset)
					lastSpeed=speed
				print("right")

			else:
				
				forward()
				
				if lastSpeed != speed:
					pwmR.start(speed)
					pwmL.start(speed+offset)
					lastSpeed=speed
				print("forward")
				if hFlag==0:
					hFlag=1
				else:
					hFlag=0

	

cv2.destroyAllWindows()























