import torch
import time
import cv2
from PIL import Image
import numpy as np
import pathlib
import torchvision
import torchvision.transforms as T
import matplotlib.pyplot as plt
import random
import time
import os
from scipy.stats import mode

gen_path = pathlib.Path.cwd()

 # These are the classes that are available in the COCO-Dataset
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu" 
  
###########################################################
# YOLO

def camera_yolo():
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    cam = cv2.VideoCapture(0)
    
    while(True): 
        ret, frame = cam.read()
        frame = frame[:, :, [2,1,0]]
        frame = Image.fromarray(frame) 
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        results = model(frame,size=640)
        cv2.imshow('YOLO', np.squeeze(results.render()))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()

def image_yolo(img_path):
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    image = cv2.imread(img_path)
    image = image[:, :, [2,1,0]]
    image = Image.fromarray(image) 
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    results = model(image,size=640)
    while(True): 

        cv2.imshow('YOLO', np.squeeze(results.render()))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

###########################################################
# MASKCNN

#model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained_backbone=True)
model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
model.eval()

def random_colour_masks(mask, img):
    """
    random_colour_masks
    parameters:
      - image - predicted masks
    method:
      - the masks of each predicted object is given random colour for visualization
    """
    mask = mask.astype(np.uint8)
    # Apply the mask to the image
    masked_image = cv2.bitwise_and(img, img, mask=mask)
    # Get the non-zero pixel values within the mask
    non_zero_pixels = masked_image[mask > 0]

    r = np.zeros_like(mask).astype(np.uint8)
    g = np.zeros_like(mask).astype(np.uint8)
    b = np.zeros_like(mask).astype(np.uint8)
    r[mask == 1], g[mask == 1], b[mask == 1] = np.mean(non_zero_pixels,  axis=tuple(range(non_zero_pixels.ndim-1)))
    color = [np.max(r), np.max(g), np.max(b)]
    coloured_mask = np.stack([r, g, b], axis=2)
    return coloured_mask, color

def get_prediction(img_path, threshold):
    """
    get_prediction
    parameters:
      - img_path - path of the input image
    method:
      - Image is obtained from the image path
      - the image is converted to image tensor using PyTorch's Transforms
      - image is passed through the model to get the predictions
      - masks, classes and bounding boxes are obtained from the model and soft masks are made binary(0 or 1) on masks
        ie: eg. segment of cat is made 1 and rest of the image is made 0

    """
    img = Image.open(img_path)
    transform = T.Compose([T.ToTensor()])
    img = transform(img)
    pred = model([img])
    pred_score = list(pred[0]['scores'].detach().numpy())
    pred_t = [pred_score.index(x) for x in pred_score if x>threshold][-1]
    masks = (pred[0]['masks']>0.5).squeeze().detach().cpu().numpy()
    pred_class = [COCO_INSTANCE_CATEGORY_NAMES[i] for i in list(pred[0]['labels'].numpy())]
    pred_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(pred[0]['boxes'].detach().numpy())]
    masks = masks[:pred_t+1]
    pred_boxes = pred_boxes[:pred_t+1]
    pred_class = pred_class[:pred_t+1]
    return masks, pred_boxes, pred_class


def instance_segmentation_api(img_path, threshold=0.5, rect_th=2, text_size=1, text_th=2, show_img=False):
    """
    instance_segmentation_api
    parameters:
      - img_path - path to input image
    method:
      - prediction is obtained by get_prediction
      - each mask is given random color
      - each mask is added to the image in the ration 1:0.8 with opencv
      - final output is displayed
    """
    masks, boxes, pred_cls = get_prediction(img_path, threshold)
    colours = [pred_cls, []]
    if show_img:
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_masks = []
        for i in range(len(masks)):
            rgb_mask, color = random_colour_masks(masks[i], img)
            colours[1].append(color)
            rgb_masks.append(rgb_mask)

            img = cv2.addWeighted(img, 1, rgb_mask, 0.5, 0)
            pt1 = (int(boxes[i][0][0]), int(boxes[i][0][1]))
            pt2 = (int(boxes[i][1][0]), int(boxes[i][1][1]))
            cv2.rectangle(img, pt1, pt2,color=(0, 255, 0), thickness=rect_th)
            text_org = (int(boxes[i][0][0]), int(boxes[i][0][1]))
            cv2.putText(img,pred_cls[i], text_org, cv2.FONT_HERSHEY_SIMPLEX, text_size, (0,255,0),thickness=text_th)
        result = np.full((rgb_masks[0].shape), (0,0,0), dtype=np.uint8)
        for mask in rgb_masks[:1]:
            result = cv2.add(result, mask)
        plt.imshow(result)
        plt.show()
        plt.figure(figsize=(20,30))
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
        plt.show()
    return dict(zip(pred_cls, masks)), colours


###########################################################
# GET_COLOR

def get_color(img_path, results, method='average'):
    # Initialize an array to store average pixel values for each mask
    most_common_pixel_values = []
    colors = {}
    img = cv2.imread(img_path)
    # Iterate over the masks
    for label in results:
        mask = results[label]
        # Ensure mask is a numpy array and of the correct data type
        mask = mask.astype(np.uint8)

        # Check if the mask has the same shape as the image
        if mask.shape[:2] != img.shape[:2]:
            raise ValueError("Mask and image shapes do not match.")

        # Apply the mask to the image
        masked_image = cv2.bitwise_and(img, img, mask=mask)
        # Get the non-zero pixel values within the mask
        non_zero_pixels = masked_image[mask > 0]

        
        if method == 'most':
            # Calculate the most common pixel value within the threshold
            threshold = 10
            if len(non_zero_pixels) > threshold:
                most_common_pixel_value, _ = mode(non_zero_pixels)
                colors[label]=most_common_pixel_value[0]
            else:
                most_common_pixel_values.append(None)
        if method == 'average':
            # Calculate average pixel values for the masked region
            average_pixel_value = np.mean(non_zero_pixels,  axis=tuple(range(non_zero_pixels.ndim-1)))
            colors[label] = (average_pixel_value)

    # Print or use the average_pixel_values as needed
    return colors

#image_yolo('descriptors/nightstand-2.jpg')


# img = Image.open('test-img.jpg')

# # Running inference on the image
# transform = T.Compose([T.ToTensor()])
# img_tensor = transform(img)
# pred = model([img_tensor])
# masks = (pred[0]['masks']>0.5).squeeze().detach().cpu().numpy()
# masks.shape
# # plt.imshow(masks[0], cmap='gray')
# # plt.show()


# # Let's color the `person` mask using the `random_colour_masks` function
# mask1 = random_colour_masks(masks[0], img)

# # Let's blend the original and the masked image and plot it.
# blend_img = cv2.addWeighted(np.asarray(img), 0.5, mask1, 0.5, 0)

# plt.imshow(blend_img)
# plt.show()
img_path = 'citrus.jpg'
results, colours = instance_segmentation_api(img_path, 0.75, show_img=True)
# [[201, 127, 34], [179, 96, 53], [190, 186, 76]]
print(colours)
colors = get_color(img_path, results)
print(colors)
# for k, v in colors:
#     print(k,v)
