#importing necessary packages
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

#reading an image
def read_image(image_path:str, window_name:str = 'Image'):
    print('Task has started')
    print('Press any key to cancel')
    #Load an image from the given path
    img = cv.imread(image_path)
    #Displying the loaded image
    cv.imshow(window_name, img)
    #Additional functions for ensuring productivity
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

def read_video(video_path:str, window_name:str = 'Video'):
    #Load a video from the given path
    capture = cv.VideoCapture(video_path)
    print('Task has started')
    print("Press 'x' key to cancel")
    #Calling a loop
    while True:
        #loading a frame from the video
        ret, frame = capture.read()
        # If there are no more frames to read, break out of the loop
        if not ret:
            print('All frames in the Video are succesfully played --- No frames are there/left to read in the path specified')
            break
        #Displying the loaded frame
        cv.imshow(window_name, frame)
        #Giving an opportunity for the user to cancel the process
        if cv.waitKey(20)&0xFF==ord('x'):
            print ('Operation cancelled by the user')
            break
    print('Task has ended')
    #Relasing the Video file
    capture.release()
    #Additional functions for ensuring productivity
    cv.destroyAllWindows()

   #rescaling the image
def rescale_image(image_path:str, scale:float, window_name:str = 'Rescaled Image'):
    print('Task has started')
    print('Press any key to cancel')
    #reading an image
    frame = cv.imread(image_path)
    #Setting the width
    width = int(frame.shape[1]*scale)
    #Setting the height
    height = int(frame.shape[0]*scale)
    #Combining them into a tuple
    dimensions = (width, height)
    #Using a predefined function from opencv to rescale the image into a variable
    resized_image = cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)
    #Displying the rescaled image
    cv.imshow(window_name, resized_image)
    #Additional functions for ensuring productivity
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#rescaling the video
def rescale_video(video_path:str, scale:float, window_name:str = 'Rescaled Video'):
    #Reading the video
    cap = cv.VideoCapture(video_path)
    print('Task has started')
    print("Press 'x' key to cancel")
    #Calling a loop
    while True:
        #loading a frame from the video
        ret, frame = cap.read()
        if not ret:
            # If there are no more frames to read, break out of the loop
            print('All frames in the Video are succesfully played --- No frames are there/left to read in the path specified')
            break
        #Setting the width
        width = int(frame.shape[1] * scale)
        #Setting the height
        height = int(frame.shape[0] * scale)
        #Combining them into a tuple
        dimensions = (width, height)
        #Using a predefined function from opencv to rescale the video into a variable
        resized_frame = cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)
        #Displying the rescaled video
        cv.imshow(window_name, resized_frame)
        #Giving an opportunity for the user to cancel the process
        if cv.waitKey(20) & 0xFF == ord('x'):
            print('Operation cancelled by the user')
            break
    print('Task has ended')
    #Relasing the Video file
    cap.release()
    #Additional functions for ensuring productivity
    cv.destroyAllWindows()

#painting an image
def paint_image(color,color_range, window_name: str = 'Painted Image'):
    print('Task has started')
    print("Press any key to cancel")
    blank = np.zeros((500, 500, 3), dtype='uint8')
    # Setting a color to the specific region defined by color_range
    blank[color_range[0]:color_range[1], color_range[2]:color_range[3]] = color
    # Displaying the output image
    cv.imshow(window_name, blank)
    # Additional functions for ensuring productivity
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Draws a rectangle
def draw_rectangle(color, outline:int = 2, window_name:str = 'Rectangle'):
    print('Task has started')
    print('Press any key to cancel')
    blank = np.zeros((500,500,3), dtype='uint8')
    #Drawing a rectangle using OpenCV's function
    cv.rectangle(blank, (0,0), (blank.shape[1]//2, blank.shape[0]//2), color, thickness=outline)
    #Displaying the output image
    cv.imshow(window_name, blank)
    print('Task has ended')
    cv.waitKey(0)
    cv.destroyAllWindows()

#Draws a circle
def draw_circle(color, outline, radius):
    print('Task has started')
    print('Press any key to cancel')
    blank = np.zeros((500,500,3), dtype='uint8')
    #Drawing a circle using OpenCV's function
    cv.circle(blank, (blank.shape[1]//2, blank.shape[0]//2), radius, color, thickness=outline)
    #Displaying the output image
    cv.imshow('Circle', blank)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Draws a line
def draw_line(color, outline):
    print('Task has started')
    print('Press any key to cancel')
    blank = np.zeros((500,500,3), dtype='uint8')
    cv.line(blank, (0,0), (300,400), color, outline)
    #Displaying the output image
    cv.imshow('Line', blank)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Writes text
def write_text(text, color, outline):
    print('Task has started')
    print('Press any key to cancel')
    blank = np.zeros((500,500,3), dtype='uint8')
    cv.putText(blank, text, (0,255), cv.FONT_HERSHEY_TRIPLEX, 1.0, color, outline)
    #Displaying the output image
    cv.imshow('Text', blank)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Convertion of RGB to Greyscale
def img_RGB2GREY(image_path:str,window_name:str = 'Greyscale'):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    grey_img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    cv.imshow(window_name,grey_img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Edge Cascade
def img_EDGECASCADE_CANNY(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    canny = cv.Canny(img,125,175)
    cv.imshow(window_name,canny)
    cv.waitKey(0)
    cv.destroyAllWindows()

#Dialation
def img_DIALATE(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    canny = cv.Canny(img,125,175)
    dialated = cv.dilate(canny,(3,3),iterations=1)
    cv.imshow(window_name,dialated)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Erosion
def img_ERODE(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    canny = cv.Canny(img,125,175)
    dialated = cv.dilate(canny,(3,3),iterations=1)
    eroded = cv.erode(dialated,(3,3),iterations=1)
    cv.imshow(window_name,eroded)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Image scaling
def img_SCALE_ENLARGE(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    enlarged = cv.resize(img,None,fx=1.5,fy=1.5,interpolation=cv.INTER_CUBIC)
    cv.imshow(window_name,enlarged)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

def img_SCALE_SHRINK(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    shrinked = cv.resize(img,(250,250),interpolation=cv.INTER_AREA)
    cv.imshow(window_name,shrinked)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Contours
def img_FIND_CONTOURS(image_path:str,window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    # Let's load a simple image with 3 black squares
    image = cv.imread(image_path)
    cv.waitKey(0)
    # Grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Find Canny edges
    edged = cv.Canny(gray, 30, 200)
    cv.waitKey(0)
    
    # Finding Contours
    # Use a copy of the image e.g. edged.copy()
    # since findContours alters the image
    contours, hierarchy = cv.findContours(edged,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    
    cv.imshow('Canny Edges After Contouring', edged)
    cv.waitKey(0)
    
    print("Number of Contours found = " + str(len(contours)))
    
    # Draw all contours
    # -1 signifies drawing all contours
    cv.drawContours(image, contours, -1, (0, 255, 0), 3)
    
    cv.imshow('Contours', image)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Shifts the position of the image
def image_translate(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    #creating a list
    rows, cols = img.shape
    M = np.float32([[1,0,100],[0,1,50]])
    dst = cv.warpAffine(img, M, (cols,rows))
    #Displaying the output image
    cv.imshow('Translated Image', dst) 
    print('Task has ended')
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows() 

#Flipping an image Vertically
def img_flipV(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    rows, cols = img.shape
    M = np.float32([[1, 0, 0], [0, -1, rows],[0, 0, 1]])
    reflected_img = cv.warpPerspective(img, M,(int(cols),int(rows)))
    #Displaying the output image
    cv.imshow('Vertically flipped Image', reflected_img)
    print('Task has ended')
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Flipping an image Horizontally
def img_flipH(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    rows, cols = img.shape
    M = np.float32([[-1, 0, cols], [0, 1, 0], [0, 0, 1]])
    reflected_img = cv.warpPerspective(img, M,(int(cols),int(rows)))
    #Displaying the output image
    cv.imshow('Horizontally flipped Image', reflected_img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Rotating an Image
def r_img(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    rows, cols = img.shape
    M = np.float32([[1, 0, 0], [0, -1, rows], [0, 0, 1]])
    img_rotation = cv.warpAffine(img, cv.getRotationMatrix2D((cols/2, rows/2), 30, 0.6), (cols, rows))
    #Displaying the output image
    cv.imshow('Rotated Image', img_rotation)
    cv.imwrite('Saved Files/Rotated Image.jpg', img_rotation)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Task has ended')

#Shrinking an Image
def s_img(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    img_shrinked = cv.resize(img, (350, 300), interpolation = cv.INTER_AREA)
    #Displaying the output image
    cv.imshow('Shrinked Image', img_shrinked)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Task has ended')

#Enlarging an Image
def e_img(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path)
    img_enlarged = cv.resize(img, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
    #Displaying the output image
    cv.imshow('Enlarged Image', img_enlarged)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Task has ended')

#Cropping an image
def c_img(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    cropped_img = img[100:300, 100:300]
    cv.imwrite('Saved Files/Cropped Image.jpg', cropped_img)
    #Displaying the output image
    cv.imshow('Cropped Image', cropped_img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Shearing an Image in X-axis
def SHEAR_img_X(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    rows, cols = img.shape
    M = np.float32([[1, 0.5, 0], [0, 1, 0], [0, 0, 1]])
    sheared_img = cv.warpPerspective(img, M, (int(cols*1.5), int(rows*1.5)))
    #Displaying the output image
    cv.imshow('Sheared X-axis', sheared_img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Shearing an Image in Y-axis
def SHEAR_img_Y(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path, 0)
    rows, cols = img.shape
    M = np.float32([[1, 0, 0], [0.5, 1, 0], [0, 0, 1]])
    sheared_img = cv.warpPerspective(img, M,
    (int(cols*1.5), int(rows*1.5)))
    #Displaying the output image
    cv.imshow('Sheared Y-axis', sheared_img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Blurring an image using 2D Convolution method
def BLUR_2DKconv(image_path):
    print('Task has started')
    print('Press any key to cancel')
    # Reading the image
    image = cv.imread(image_path)
    # Creating the kernel with numpy
    kernel2 = np.ones((5, 5), np.float32)/25
    # Applying the filter
    img = cv.filter2D(src=image, ddepth=-1, kernel=kernel2)
    # showing the image
    cv.imshow('Original', image)
    cv.imshow('Kernel Blur', img)
    cv.waitKey(0)
    print('Task has ended')
    cv.destroyAllWindows()

#Blurring an image using Average Blur
def BLUR_Avg(image_path):
    print('Task has started')
    print('Press any key to cancel')
    image = cv.imread(image_path)
    # Applying the filter
    averageBlur = cv.blur(image, (5, 5))
    # Showing the image
    cv.imshow('Original', image)
    cv.imshow('Average blur', averageBlur)
    cv.waitKey()
    print('Task has ended')
    cv.destroyAllWindows() 

#Blurruing an image using Gaussian Blur
def BLUR_Gaus(image_path):
    print('Task has started')
    print('Press any key to cancel')
    image = cv.imread(image_path)
    # Applying the filter
    gaussian = cv.GaussianBlur(image, (3, 3), 0)
    # Showing the image
    cv.imshow('Original', image)
    cv.imshow('Gaussian blur', gaussian)
    cv.waitKey()
    print('Task has ended')
    cv.destroyAllWindows()

#Blurruing an image using Median Blur
def BLUR_Mead(image_path):
    print('Task has started')
    print('Press any key to cancel')
    # Reading the image
    image = cv.imread(image_path)
    # Applying the filter
    medianBlur = cv.medianBlur(image, 9)
    # Showing the image
    cv.imshow('Original', image)
    cv.imshow('Median blur',medianBlur)
    cv.waitKey()
    print('Task has ended')
    cv.destroyAllWindows()

#Blurruing an image using Bilateral Blur
def BLUR_Bilat(image_path):
    print('Task has started')
    print('Press any key to cancel')
    # Reading the image
    image = cv.imread(image_path)
    # Applying the filter
    bilateral = cv.bilateralFilter(image,
    9, 75, 75)
    # Showing the image
    cv.imshow('Original', image)
    cv.imshow('Bilateral blur', bilateral)
    cv.waitKey()
    print('Task has ended')
    cv.destroyAllWindows()

#Seperating BGR color channels
def split_COLORSPACES(image_path:str, window_name:str):
    print('Task has started')
    print('Press any key to cancel')
    image = cv.imread(image_path)
    B, G, R = cv.split(image)
    # Corresponding channels are separated
    cv.imshow("Original", image)
    cv.waitKey(0)
    cv.imshow("Blue", B)
    cv.waitKey(0)
    cv.imshow("Green", G)
    cv.waitKey(0)
    cv.imshow("Red", R)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Task has ended')

def img_maskCIRCLE(image_path):
    print('Task has started')
    print('Press any key to cancel')
    img = cv.imread(image_path) 
    cv.imshow('Original image', img)
    blank = np.zeros(img.shape[:2], dtype='uint8')
    cv.imshow('Blank Image', blank)
    circle = cv.circle(blank,
    (img.shape[1]//2,img.shape[0]//2),200,255, -1)
    cv.imshow('Mask',circle)
    masked = cv.bitwise_and(img,img,mask=circle)
    cv.imshow('Masked Image', masked)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print('Task has ended')


def img_ALPHABLEND(image1_path: str, image2_path: str):
    print('Task has started')
    print('Press any key to cancel') 
    img1 = cv.imread(image1_path)
    img2 = cv.imread(image2_path)
    img2 = cv.resize(img2, img1.shape[1::-1])
    cv.imshow("img 1",img1)
    cv.waitKey(0)
    cv.imshow("img 2",img2)
    cv.waitKey(0)
    choice = 1
    while (choice) :
        alpha = 0.5
        dst = cv.addWeighted(img1, alpha , img2, 1-alpha, 0)
        # img3 = cv.imread(dst)
        cv.imshow("alpha blending 1",dst)
        cv.waitKey(0)
        cv.destroyAllWindows()
        print('Task has ended')
        # choice = int(input("Enter 1 to continue and 0 to exit"))
        break

def img_COLORHIST(image_path:str):
    print('Task has started')
    n_img = cv.imread(image_path)
    plt.hist(n_img.ravel(), bins=256, range=(0.0, 1.0), fc='k',ec='k') #calculating histogram
    histr = cv.calcHist([n_img],[0],None,[256],[0,256])
    # show the plotting graph of an image
    plt.plot(histr)
    plt.show()
    print('Task has ended')

def bitwise_AND():
    print('Task has started')
    print('Press any key to cancel')
    img1 = cv.imread('Resources/Photos/1bit1.png')
    img2 = cv.imread('Resources/Photos/2bit2.png')
    
    # Check if the dimensions of img1 and img2 are the same, and resize if needed
    if img1.shape[:2] != img2.shape[:2]:
        img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Perform bitwise AND operation
    dest_and = cv.bitwise_and(img1, img2, mask=None)
    
    # Display the result
    cv.imshow('Bitwise AND', dest_and)
    
    # Wait for a key press and then close the window
    if cv.waitKey(0) & 0xFF == 27:
        cv.destroyAllWindows()
        print('Task has ended')

def bitwise_OR():
    print('Task has started')
    print('Press any key to cancel')
    img1 = cv.imread('Resources/Photos/1bit1.png')
    img2 = cv.imread('Resources/Photos/2bit2.png')
    
    # Check if the dimensions of img1 and img2 are the same, and resize if needed
    if img1.shape[:2] != img2.shape[:2]:
        img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))

    # cv.bitwise_or is applied over the
    # image inputs with applied parameters 
    dest_or = cv.bitwise_or(img2, img1, mask = None)
    
    # the window showing output image
    # with the Bitwise OR operation
    # on the input images
    cv.imshow('Bitwise OR', dest_or)
    
    # De-allocate any associated memory usage  
    if cv.waitKey(0) & 0xff == 27: 
        cv.destroyAllWindows() 

def bitwise_XOR():
    print('Task has started')
    print('Press any key to cancel')
    img1 = cv.imread('Resources/Photos/1bit1.png')
    img2 = cv.imread('Resources/Photos/2bit2.png')
    
    # Check if the dimensions of img1 and img2 are the same, and resize if needed
    if img1.shape[:2] != img2.shape[:2]:
        img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))
    # cv.bitwise_xor is applied over the
    # image inputs with applied parameters 
    dest_xor = cv.bitwise_xor(img1, img2, mask = None)
    
    # the window showing output image
    # with the Bitwise XOR operation
    # on the input images
    cv.imshow('Bitwise XOR', dest_xor)
    
    # De-allocate any associated memory usage  
    if cv.waitKey(0) & 0xff == 27: 
        cv.destroyAllWindows() 
        print('Task has ended')
    
def bitwise_NOT():
    print('Task has started')
    print('Press any key to cancel')
    img1 = cv.imread('Resources/Photos/1bit1.png')
    img2 = cv.imread('Resources/Photos/2bit2.png')
    
    # Check if the dimensions of img1 and img2 are the same, and resize if needed
    if img1.shape[:2] != img2.shape[:2]:
        img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))

    # cv.bitwise_not is applied over the
    # image input with applied parameters 
    dest_not1 = cv.bitwise_not(img1, mask = None)
    dest_not2 = cv.bitwise_not(img2, mask = None)
    
    # the windows showing output image
    # with the Bitwise NOT operation
    # on the 1st and 2nd input image
    cv.imshow('Bitwise NOT on image 1', dest_not1)
    cv.imshow('Bitwise NOT on image 2', dest_not2)
    
    # De-allocate any associated memory usage  
    if cv.waitKey(0) & 0xff == 27: 
        cv.destroyAllWindows() 
        print('Task has ended')

