import os
import sys
import time
import stagecontroller
import cv2 as cv
import numpy as np
import math


chipFusedImage = cv.imread("Fused.jpg")
chipLocation = [0, 0, 0]
chip_center = [37.3, 93.4, 0]

# Ask user for camera ID
cameraID = 1

# Test function to open camera
try:
    camera = cv.VideoCapture(cameraID)
    img = camera.read()[1]
    camera.release()
except:
    print("Error: Could not open the camera.")

def openCamera():
    camera = cv.VideoCapture(cameraID)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv.CAP_PROP_BUFFERSIZE, 1)
    return camera

def get_offset_between_images(large_image, small_image):
    large_gray = cv.cvtColor(large_image, cv.COLOR_BGR2GRAY)
    small_gray = cv.cvtColor(small_image, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(large_gray, small_gray, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    return max_loc

def calibrate_chip_location(controller):
    # Take picture of chip
    chipImage = takePicture(controller,filename="images/chipImage.png")

    # Find chip in fused image
    offset = get_offset_between_images(chipFusedImage, chipImage)

    x = offset[0] + controller.get_position()[0]
    y = offset[1] + controller.get_position()[1]

    print("Chip location: ({}, {})".format(x, y))

    chipLocation[0] = x
    chipLocation[1] = y
    
def get_focus_score(image):
    laplacian = cv.Laplacian(image, cv.CV_64F)
    variance = laplacian.var()
    
    return variance

def gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, numX, numY, numZ, delay = 0.8, folder = None):
    if not folder:
        curent_time = time.strftime("%Y%m%d-%H%M%S")
        folder = os.path.join("images", curent_time)
    
    # check folder
    if not os.path.exists(folder):
        os.makedirs(folder)
   
    # Delete files in folder
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))

    diffX = endX - startX
    diffY = endY - startY
    diffZ = endZ - startZ

    stepSizeX = diffX / max(numX - 1, 1)
    stepSizeY = diffY / max(numY - 1, 1)
    stepSizeZ = diffZ / max(numZ - 1, 1)

    print("Taking pictures in a grid from ({}, {}, {}) to ({}, {}, {})".format(startX, startY, startZ, endX, endY, endZ))
    # Count number of pictures to be taken
    numPictures = numX * numY * numZ
    print("Number of pictures to be taken: {}".format(numPictures))

    camera = openCamera()

    for i in range(numX):
        x = startX + i * stepSizeX
      
        for j in range(numY):
            
            if i % 2 == 0:
                y = startY + j * stepSizeY
            else:
                y = endY - j * stepSizeY

            for k in range(numZ):
                
                if j % 2 == 0:
                    z = startZ + k * stepSizeZ
                else:
                    z = endZ - k * stepSizeZ

                print("Moving to coordinates ({}, {}, {})".format(x, y, z))
                controller.move_to(x, y, z)
                # Take picture here
                time.sleep(delay)
                xr = round(x, 2)
                yr = round(y, 2)
                zr = round(z, 2)
                filename = os.path.join(folder, "image_{}_{}_{}.png".format(xr, yr, zr))
                takePicture(controller, camera, filename)

                count = i * numY * numZ + j * numZ + k + 1
                print("Picture {} of {} taken".format(count, numPictures))

    camera.release()

        
def focusCameraByZ(controller):
    camera = openCamera()

    scale = controller.get_scale()

    
    minZ = 0
    maxZ = 20

    numImages = 40
    division = (maxZ - minZ) / numImages
    bestFocus = 0
    bestZ = 0

    for i in range(numImages + 1):
        z = minZ + i * division
        print("Moving to z = {}".format(z))
        controller.move_to(None, None, z)
        img = takePicture(controller, camera, save=False)

        if img is None:
            break

        focus = get_focus_score(img)
        
        print("Focus score: {}".format(focus))

        if focus > bestFocus:
            bestFocus = focus
            bestZ = z

    imagesPerScale = 4
    numScales = 4

    # Maximize focus score, search along grid, then refine
    zAccumulator = bestZ
    bestFocus = 0
    bestZ = 0

    refineRegion = 1

    hasError = False

    
    for i in range(numScales):
        division = refineRegion / (((imagesPerScale) ** (i * 0.5 + 1)))

        if division < 1/scale[2]:
            division = 1/scale[2]

        bestCurrentFocus = 0
        bestCurrentZ = 0
        for j in range(imagesPerScale + 1):
            z = (j - imagesPerScale / 2 - 1) * division + zAccumulator

            if j == 0:
                controller.move_to(None, None, max(z - division,0))
                time.sleep(0.25)
            if z < minZ or z > maxZ:
                continue

            print("Moving to z = {}".format(z))
            controller.move_to(None, None, z)
            time.sleep(0.25)
            img = takePicture(controller, camera, save=False)

            if img is None:
                hasError = True
                break
                

            focus = get_focus_score(img)
            
            print("Focus score: {}".format(focus))

            new_filename = "focus/focus_{}_{}.png".format(round(z,5), focus)
            cv.imwrite(new_filename, img)

            if focus > bestCurrentFocus:
                bestCurrentFocus = focus
                bestCurrentZ = z
        
        if hasError:
            break

        zAccumulator = bestCurrentZ
        bestZ = bestCurrentZ
        bestFocus = bestCurrentFocus

        if division <= 1/scale[2]:
            break

    print("Best focus: {} at z = {}".format(bestFocus, bestZ))
    controller.move_to(None, None, max(bestZ - 1, 0))
    time.sleep(1)
    controller.move_to(None, None, bestZ)

    camera.release()


def takePicture(controller, cameraIn = None, filename = None, save = True):
    x = controller.get_position()[0]
    y = controller.get_position()[1]
    z = controller.get_position()[2]

    # Round to 2 decimal places
    x = round(x, 2)
    y = round(y, 2)
    z = round(z, 2)

    print("Taking picture at coordinates ({}, {}, {})".format(x, y, z))
    # Take picture here

    try:
        if cameraIn:
            camera = cameraIn
        else:
            camera = openCamera()
        img = camera.read()[1]
        img = camera.read()[1]

        # Rotate image 90
        # img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)


        # Save image
        if not filename:
            filename = "images/image_{}_{}_{}.png".format(x, y, z)
        
        # print dimensions of image
        print("Image dimensions: {}".format(img.shape))

        if save:
            cv.imwrite(filename, img)
        
        if not cameraIn:
            camera.release()

        return img
    except:
        print("Error taking picture")
        print(sys.exc_info()[0])
        return

def detect_black_contour():
    camera = openCamera()
    if not camera.isOpened():
        print("Error: Could not open the camera.")
        return None, None

    img = camera.read()[1]
    camera.release()

    # Convert the image to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Apply a binary threshold to get the black areas
    _, thresholded = cv.threshold(gray, 50, 255, cv.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv.findContours(thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour (assuming it's the one we're interested in)
        largest_contour = max(contours, key=cv.contourArea)

        # Calculate the center of the contour
        M = cv.moments(largest_contour)
        if M["m10"] != 0 and M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return img, (cX, cY)
        else:
            print("Error: Could not calculate the center of the contour.")
            return img, None
    else:
        print("No contours found.")
        return img, None

def calculate_angle(center1, center2):
    # Calculate the angle between the two centers
    delta_x = center2[0] - center1[0]
    delta_y = center2[1] - center1[1]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return angle

# def check_camera_alignment(controller):
#     controller.move_to(record_current_position[0], record_current_position[1], record_current_position[3])
#     # Take the first image and detect the contour center
#     img1, center1 = detect_black_contour()
#     if center1 is None:
#         return

#     # Simulate moving the camera
#     controller.move_to(record_current_position[0], record_current_position[1]+0.5, record_current_position[3])

#     # Take the second image after moving the camera and detect the contour center
#     img2, center2 = detect_black_contour()
#     if center2 is None:
#         return

#     # Calculate the angle between the two centers
#     angle = calculate_angle(center1, center2)
#     print(f"Angle between the centers: {angle:.2f} degrees")

#     # Draw the centers and the angle on the second image
#     cv.circle(img2, center1, 7, (255, 0, 0), -1)
#     cv.putText(img2, f"Center 1 ({center1[0]}, {center1[1]})", (center1[0] - 50, center1[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

#     cv.circle(img2, center2, 7, (0, 255, 0), -1)
#     cv.putText(img2, f"Center 2 ({center2[0]}, {center2[1]})", (center2[0] - 50, center2[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#     cv.putText(img2, f"Angle: {angle:.2f} degrees", (min(center1[0], center2[0]), min(center1[1], center2[1]) - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#     # Display the final image with the angle
#     controller.move_to(record_current_position[0], record_current_position[1], record_current_position[3])
#     cv.imshow('Angle Between Centers', img2)
#     cv.waitKey(0)
#     cv.destroyAllWindows()

def main():
    # Initialize and connect to the stage controller
    with stagecontroller.StageController(118548,129626,129642) as controller:
        if not controller.are_all_axis_connected():
            print("Failed to connect to all axes")
            exit(1)
    
        # Home the stage initially
        # controller.home()

        while True:
            try:
                # Request user input
                command = input("Enter command (or coordinates as X Y Z): ").strip()

                if command.lower() == 'picture':
                    takePicture(controller)
                elif command.lower() == 'stitch':
                    controller.move_to(chip_center[0], chip_center[1], chip_center[2])
                    focusCameraByZ(controller)

                    z = controller.get_position()[2]
                    x_half = 8
                    y_half = 5
                    grid_start = [chip_center[0] - x_half, chip_center[1] - y_half, z]
                    grid_end = [chip_center[0] + x_half, chip_center[1] + y_half, z]
                    grid_n = [5, 5, 1]

                    gridTakePicture(controller, grid_start[0], grid_start[1], grid_start[2], grid_end[0], grid_end[1], grid_end[2], grid_n[0], grid_n[1], grid_n[2], delay=0.2)
               
                elif command.lower() == 'center':
                    controller.move_to(chip_center[0], chip_center[1], chip_center[2])
                elif command.lower() == 'chip':
                    calibrate_chip_location(controller)
                elif command.lower() == 'grid':
                    # query user
                    #print("Enter start x, y, z/n")
                    startPos = input("Enter start x y z: ").strip().split()
                    if len(startPos) != 3:
                        print("Invalid input. Please enter three numeric values separated by spaces.")
                        continue

                    #print("Enter end x, y, z/n")
                    endPos = input("Enter end x y z: ").strip().split()
                    if len(endPos) != 3:
                        print("Invalid input. Please enter three numeric values separated by spaces.")
                        continue

                    stepNum = input("Enter number of steps in x, y, z: ").strip().split()
                    if len(stepNum) != 3:
                        print("Invalid input. Please enter three numeric values separated by spaces.")
                        continue

                    numX, numY, numZ = map(int, stepNum)

                    delay = float(input("Enter delay: "))

                    startX, startY, startZ = map(float, startPos)
                    endX, endY, endZ = map(float, endPos)

                    gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, numX, numY, numZ, delay)

                elif command.lower() == 'home':
                    # Home the stage
                    print("Homing the stage...")
                    controller.home()
                elif command.lower() == 'focus':
                    focusCameraByZ(controller)
                elif command.lower() == 'homex':
                    # Home the stage
                    print("Homing the stage along x")
                    controller.home(homeY=False, homeZ = False)
                elif command.lower() == 'homey':
                    # Home the stage
                    print("Homing the stage along y")
                    controller.home(homeX = False, homeZ = False)
                elif command.lower() == 'homez':
                    # Home the stage
                    print("Homing the stage along z")
                    controller.home(homeX = False, homeY = False)
                elif command.lower() == 'getpos':
                    # get current position
                    print("Current Position is: ", controller.get_position())
                    record_current_position = controller.get_position()
                elif command.lower() == 'aligncamera':
                    controller.move_to(record_current_position[0], record_current_position[1], record_current_position[2])
                    # Take the first image and detect the contour center
                    img1, center1 = detect_black_contour()
                    if center1 is None:
                        return

                    # Simulate moving the camera
                    controller.move_to(record_current_position[0], record_current_position[1]+0.5, record_current_position[2])

                    # Take the second image after moving the camera and detect the contour center
                    img2, center2 = detect_black_contour()
                    
                    if center2 is None:
                        return
                    
                    controller.move_to(record_current_position[0], record_current_position[1]-0.5, record_current_position[2])
                    
                    # Calculate the angle between the two centers
                    angle = calculate_angle(center1, center2)
                    print(f"Angle between the centers: {angle:.2f} degrees")

                    # Draw the centers and the angle on the second image
                    cv.circle(img2, center1, 7, (255, 0, 0), -1)
                    cv.putText(img2, f"Center 1 ({center1[0]}, {center1[1]})", (center1[0] - 50, center1[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    cv.circle(img2, center2, 7, (0, 255, 0), -1)
                    cv.putText(img2, f"Center 2 ({center2[0]}, {center2[1]})", (center2[0] - 50, center2[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    cv.putText(img2, f"Angle: {angle:.2f} degrees", (min(center1[0], center2[0]), min(center1[1], center2[1]) - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    # Display the final image with the angle
                    
                    cv.imshow('Angle Between Centers', img2)
                    cv.waitKey(0)
                    cv.destroyAllWindows()
                else:
                    # Parse coordinates from the command input
                    coords = command.split()
                    if len(coords) == 3:
                        try:
                            # can be num or -
                            x = None if coords[0] == '-' else float(coords[0])
                            y = None if coords[1] == '-' else float(coords[1])
                            z = None if coords[2] == '-' else float(coords[2])
                            # Move the stage to the specified coordinates
                            print(f"Moving to coordinates ({x}, {y}, {z})...")

                            controller.move_to(x, y, z)
                        except ValueError:
                            print("Invalid coordinates. Please enter three numeric values.")
                    else:
                        print("Invalid input. Please enter 'home' or three numeric values separated by spaces.")

            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()
