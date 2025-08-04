import numpy
import torch
import os
from PIL import Image, ImageDraw
import io
import json
import cv2
import numpy as np

FIL_DIR = os.path.dirname((os.path.abspath(__file__)))
# model_path = torch.hub.load('ultralytics/yolov5', 'custom', FIL_DIR+'/weights/best-sol.pt')
img_upload_dir = os.path.join(FIL_DIR, "files/uploads/")
img_results_dir = os.path.join(FIL_DIR, '../media/results/')


def save_image(img_data, img_name, save_to=img_upload_dir):
    input_image = Image.open(img_data.file).convert("RGB")
    input_image.save(os.path.join(save_to, img_name))


def process_image(img_path, mdl):
    input_image = Image.open(io.BytesIO(img_path)).convert("RGB")
    print(type(input_image))
    results = mdl(input_image)
    print(results)
    return json.loads(results.pandas().xyxy[0].to_json(orient="records"))


def process_image_v1(img_data, mdl, filename):
    print(type(img_data))
    input_image = Image.open(img_data.file).convert("RGB")
    print(type(input_image))
    results = mdl(input_image)[0]

    # Get root box
    root_boxes = (results.boxes.cls == 0).nonzero(as_tuple=True)[0].tolist()

    # Get necrosis boxes
    nec_boxes = (results.boxes.cls == 1).nonzero(as_tuple=True)[0].tolist()
    print(root_boxes, nec_boxes)
    print(results.path)

    # Get necrosis masks and root masks
    root_mask = results.masks.xyn[root_boxes[0]]
    nec_masks = {str(n): results.masks.xyn[n].tolist() for n in nec_boxes}

    pr = process_results(results, nec_boxes, root_boxes, img_results_dir, filename)
    return pr, 'http://localhost:8000/static/'+filename, len(nec_boxes), nec_masks
    # return pr, os.path.join(img_results_dir, filename), len(nec_boxes), nec_masks


def process_image_v2(img_path, mdl):
    input_image = Image.open(img_path).convert("RGB")
    print(type(input_image))
    results = mdl(input_image)[0]

    # Get root box
    root_boxes = (results.boxes.cls == 0).nonzero(as_tuple=True)[0].tolist()

    # Get necrosis boxes
    nec_boxes = (results.boxes.cls == 1).nonzero(as_tuple=True)[0].tolist()
    print(root_boxes, nec_boxes)
    print(results.path)

    # Get necrosis masks and root masks
    root_mask = results.masks.xyn[root_boxes[0]]
    nec_masks = {str(n): results.masks.xyn[n].tolist() for n in nec_boxes}

    pr = process_results(results, nec_boxes, root_boxes, img_results_dir, os.path.basename(img_path))
    return pr, os.path.basename(img_path).replace('.jpg', '.png'), len(nec_boxes), nec_masks


# def get_necrosis_percentage(necrosis_masks, root_mask,):
#     root_pixels = root_mask[0] * root_mask[1]
#     # nec_pixels+= res.masks.xy.shape[0]
#
#     pass


def process_results(model_results, necrosis_idx, root_idx, save_dir, img_path, save_result=True, save_mask=False):
    """
    Function to process the results from the model.
    Performs background removal and saves masks.
    """

    img_rgb = model_results.orig_img  # Read image
    # img_mask = np.zeros(img_rgb.shape, np.int32)  # Create mask
    # img_mask = Image.new('RGBA', model_results.orig_shape, color='black')
    # poly_mask = img_rgb.copy()
    # img_draw = ImageDraw.Draw(img_mask)
    #
    root_mask = np.zeros(model_results.orig_shape, np.uint8)
    nec_mask = np.zeros(model_results.orig_shape, np.uint8)
    # fill_mask = ''
    # pil_mask = Image.fromarray(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGBA),  'RGBA')
    # # pil_mask = Image.fromarray(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
    # # pil_mask = Image.fromarray(img_rgb)
    # pil_draw = ImageDraw.Draw(pil_mask, 'RGBA')
    # img_draw.polygon(model_results.masks.xy[root_idx[0]], fill=(255,0,0, 255))
    #
    # root_pixels = model_results.masks.xy[root_idx[0]].shape[0]

    cv2.fillPoly(root_mask, [model_results.masks.xy[root_idx[0]].astype('int')], color=[255])
    root_area = cv2.countNonZero(root_mask)
    # contours, hierarchy = cv2.findContours(root_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # root_contour_area = sum([cv2.contourArea(c) for c in contours])
    print(root_area)
    # print(root_contour_area)

    # root_mask_draw = ImageDraw.Draw(root_mask)
    # root_mask_draw.polygon(root_pixels, fill=255)s
    # print(type(root_mask))
    # root_mask = cv2.fillPoly(img_rgb, root_pixels, color=(0, 255, 0))
    nec_pixels = 0
    for n in necrosis_idx:
        mask_points = [model_results.masks.xy[n].astype('int')]  # Get mask x and y points
        # print(mask_points[0])
        nec_pixels += model_results.masks.xy[n].shape[0]

        # pil_draw.polygon(model_results.masks.xy[n], fill=(255, 0, 0, 230))

        # fill_mask = cv2.fillPoly(img_mask, mask_points, color=(0, 255, 0))  # Fill detected mask polygon
        # cv2.fillPoly(img_rgb, mask_points, color=(0, 255, 0))
        cv2.fillPoly(nec_mask, mask_points, color=[255])
        cv2.polylines(img_rgb, mask_points, color=(255, 0, 0), thickness=6, isClosed=True)

        # img_draw.polygon(model_results.masks.xy[n], fill=(0, 255, 0))
        # pil_draw.polygon(model_results.masks.xy[n], fill=(0, 255, 0, 100))

    nec_area = cv2.countNonZero(nec_mask)
    print(nec_area)

    # seg_rgb = cv2.bitwise_and(img_rgb, img_rgb, mask=fill_mask)  # Segment original image

    nec_per = (nec_area/root_area)* 100

    print(f'Orig: {nec_per}')
    print(f'New: {(nec_area/root_area) * 100}')

    cv2.putText(img_rgb, f'{nec_per:.2f}%', (int(model_results.orig_shape[1]/2), 100), color=(255, 0, 0),
                thickness=5, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=5)
    # pil_draw.text((int(model_results.orig_shape[1]/2), 100), f'{nec_per:.2f}%', fill=(0, 0, 255), font_size=50)

    if save_result:
        # cv2.imwrite(save_dir + img_path, img_rgb)
        # pil_mask.save(os.path.join(save_dir, 'pillow-'+img_path.replace('.jpg', '.png')))
        # pil_mask.save(os.path.join(save_dir, img_path.replace('.jpg', '.png')))
        # cv2.imwrite(os.path.join(save_dir, 'poly-' + img_path.replace('.jpg', '.png')), poly_mask)
        cv2.imwrite(os.path.join(save_dir, img_path.replace('.jpg', '.png')), img_rgb)
        # cv2.imwrite(save_dir + "ann-" + img_name, img_rgb)
    # if save_mask:
    #     # cv2.imwrite(save_dir + "/masks-"+img_path, fill_mask)
    #     img_mask.save(os.path.join(save_dir, 'mask-' + img_path.replace('.jpg', '.png')))

    return nec_per

    # return seg_rgb, os.path.basename(model_results.path)
# def process_images(file_list, mdl=model_path):
#     print(type(file_list[0]))
#     pil_files = [Image.open(f.file).convert("RGB") for f in file_list]
#     print(type(pil_files[0]))
#     results = mdl(pil_files)


def draw_annotations(img_data, detections):
    img = np.asarray(Image.open(img_data.file).convert("RGB"))
    # print(type(img))
    for d in detections:
        cv2.rectangle(
            img,
            (int(d['xmin']), int(d['ymin'])),
            (int(d['xmax']), int(d['ymax'])),
            (255, 0, 0),
            2
        )
    return img


def save_img(img_arr, img_name, path_to_save=img_results_dir):
    cv2.imwrite(os.path.join(path_to_save, img_name), cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB))
    return os.path.join(path_to_save, img_name)
