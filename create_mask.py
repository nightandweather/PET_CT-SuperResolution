import cv2
import numpy as np
import pydicom
import os

# Function to apply the mask on the DICOM image
def apply_mask(dicom_image, mask):
    result = cv2.bitwise_and(dicom_image, dicom_image, mask=mask)
    return result

# Function to update the displayed image and mask
def update_display():
    global current_slice, dicom_images, mask, wl, ww, mask_array, drawing, rect_start

    dicom_image = dicom_images[current_slice].pixel_array.astype(np.float32)

    # Apply Window Level and Window Width settings
    dicom_image = np.clip((dicom_image - (wl - ww / 2)) / ww * 255, 0, 255)

    # Convert to uint8 for display
    dicom_image = dicom_image.astype(np.uint8)

    # Draw rectangles on the mask
    if drawing and rect_start is not None:
        rect_end = (mouse_x, mouse_y)
        cv2.rectangle(mask, rect_start, rect_end, 255, -1)

    result_image = apply_mask(dicom_image, mask)

    # Update the mask array
    mask_array[current_slice] = (mask > 0).astype(np.uint8)

    cv2.imshow('DICOM Image', dicom_image)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result Image', result_image)

# Function for mouse events
def on_mouse(event, x, y, flags, param):
    global drawing, rect_start, mouse_x, mouse_y, current_slice, mask

    mouse_x, mouse_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        rect_start = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect_start = None
        update_display()

    # Handle right mouse button to erase rectangles
    elif event == cv2.EVENT_RBUTTONDOWN:
        cv2.circle(mask, (x, y), 10, 0, -1)  # Use a circle to erase the drawn rectangle
        update_display()

    # Handle mouse wheel event for slice navigation
    elif event == cv2.EVENT_MOUSEWHEEL:
        delta = flags
        if delta > 0 and current_slice < len(dicom_images) - 1:
            current_slice += 1
        elif delta < 0 and current_slice > 0:
            current_slice -= 1

        update_display()

# Function to update WL and WW settings from trackbars
def on_change(_):
    global wl, ww
    wl = cv2.getTrackbarPos('WL', 'Controls')
    ww = cv2.getTrackbarPos('WW', 'Controls')
    update_display()

# Function for mouse scroll event
def on_mouse_scroll(event, x, y, flags, param):
    global current_slice, dicom_images, mask

    if event == cv2.EVENT_MOUSEWHEEL:
        delta = flags
        if delta > 0 and current_slice < len(dicom_images) - 1:
            current_slice += 1
        elif delta < 0 and current_slice > 0:
            current_slice -= 1

        update_display()

# Initialize variables
drawing = False
rect_start = None
current_slice = 0
mask = np.zeros((512, 512), np.uint8)
dicom_folder = r'C:\Users\NM_RR\Documents\GitHub\PET_CT-SuperResolution\1067272\1067272_20231214'  # Replace with the actual path to your DICOM folder
wl, ww = 40, 400  # Initial Window Level and Window Width settings

# Load DICOM images from the folder
dicom_files = [file for file in os.listdir(dicom_folder) if file.endswith('.dcm')]
dicom_files.sort()
dicom_images = [pydicom.dcmread(os.path.join(dicom_folder, file)) for file in dicom_files]

# Create a window and set mouse callback for drawing rectangles
cv2.namedWindow('DICOM Image')
cv2.setMouseCallback('DICOM Image', on_mouse)

# Create a control window with trackbars for WL and WW
cv2.namedWindow('Controls')
cv2.createTrackbar('WL', 'Controls', wl, 2000, on_change)
cv2.createTrackbar('WW', 'Controls', ww, 2000, on_change)

# Create a NumPy array to store the mask information
mask_array = np.zeros((len(dicom_images), 512, 512), dtype=np.uint8)

while True:
    update_display()

    # 'ESC' key to exit
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

# Save the mask array as a NumPy file
np.save('mask_array.npy', mask_array)

cv2.destroyAllWindows()
