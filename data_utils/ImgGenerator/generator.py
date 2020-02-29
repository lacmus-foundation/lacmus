import cv2
from pathlib import Path
import xml.etree.ElementTree as ET 
import numpy as np
import os
import random
from scipy import ndimage

def transform_target_image(img, p_width, inpaint_width):
    ''' Create boolean and gradient masks for an image, then apply random transformation both for image and masks.
    Returns transformed image ind its masks.'''
    
    img_h, img_w, _ = img.shape
 
    # boolean mask of (target size)+(border size) for inpainting
    boolean_mask = np.zeros_like(img).astype('uint8')
    boolean_mask[inpaint_width:img_h-inpaint_width, inpaint_width:img_w-inpaint_width, :]=255
    
    # boolean mask of (target size) for bbox generation
    frame_h = int(np.ceil((img_h-2*inpaint_width)/(1+2*p_width)))
    frame_w = int(np.ceil((img_w-2*inpaint_width)/(1+2*p_width)))
    
    dh = int((img_h-frame_h)/2)
    dw = int((img_w-frame_w)/2)
    
    target_frame = np.zeros_like(img).astype('uint8')
    target_frame[dh:img_h-dh, dw:img_w-dw, :]=255
    
    # gradient mask for simple image mixing
    gradient_mask = np.ones_like(img).astype('float')
    
    for h in range(inpaint_width):
        for w in range(img_w):
            gradient_mask[h, w, :] = h/inpaint_width

    for h in range(img_h-inpaint_width, img_h):
        for w in range(img_w):
            gradient_mask[h, w, :] = (img_h-h)/inpaint_width
            
    for h in range(img_h):
        for w in range(inpaint_width):
            if h<inpaint_width or h>img_h-inpaint_width:               
                gradient_mask[h, w, :] = min(gradient_mask[h, w, 0], w/inpaint_width)
            else:            
                gradient_mask[h, w, :] = w/inpaint_width 
            
    for h in range(img_h):
        for w in range(img_w-inpaint_width, img_w):
            if h<inpaint_width or h>img_h-inpaint_width:
                gradient_mask[h, w, :] = min(gradient_mask[h, w, 0], (img_w-w)/inpaint_width)
            else:            
                gradient_mask[h, w, :] = (img_w-w)/inpaint_width  
                
    # random rotation    
    angle = random.random()*360    
    res_img = ndimage.rotate(img, angle)
    boolean_mask = ndimage.rotate(boolean_mask, angle)
    gradient_mask = ndimage.rotate(gradient_mask, angle)
    target_frame = ndimage.rotate(target_frame, angle)
        
    return res_img, boolean_mask, gradient_mask, target_frame



def place_img_to_background(img, back, b_mask, grad_mask, t_frame):
    ''' Place target image on background, then generate bbox corners'''
    
    # get background size    
    height = back.shape[0]
    width = back.shape[1]
    
    # get insertion point
    h0 = int(random.random()*(height-img.shape[0]))
    w0 = int(random.random()*(width-img.shape[1]))
    
    # extend target img to background size    
    targ = np.zeros_like(back)
    targ[h0:h0+img.shape[0], w0:w0+img.shape[1], :] = img

    # extend target grad_mask to background size
    g_mask = np.zeros_like(back).astype('float')
    g_mask[h0:h0+img.shape[0], w0:w0+img.shape[1], :] = grad_mask
    
    # mix images
    res_img = (targ*g_mask + back*(1-g_mask)).astype('uint8')
    
    # generate bbox
    bbox={}
    bbox['xmin'] = np.min(np.argwhere(np.sum(t_frame[:,:,0], axis=0))) + w0
    bbox['xmax'] = np.max(np.argwhere(np.sum(t_frame[:,:,0], axis=0))) + w0
    bbox['ymin'] = np.min(np.argwhere(np.sum(t_frame[:,:,0], axis=1))) + h0
    bbox['ymax'] = np.max(np.argwhere(np.sum(t_frame[:,:,0], axis=1))) + h0
        
    return res_img, bbox



def draw_bbox(image, bbox):
    '''Draws bbox on image, inputs: image and bbox as a dict'''
    
    image_h, image_w, _ = image.shape

    xmin = bbox['xmin']
    ymin = bbox['ymin']
    xmax = bbox['xmax']
    ymax = bbox['ymax']

    cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (0,255,0), 3)
        
    return image  



def main():
 
    # open CFG file, define paths and crops shapes
    config = open('config.cfg')
    for line in config:
        if line.startswith('DATASET_PATH'):
            dataset_path = Path(line.split('=')[1].strip().replace('\n',''))
        if line.startswith('BACKGROUNDS_FOLDER'):
            backs_folder = line.split('=')[1].strip().replace('\n','')
        if line.startswith('AUGMENTED_FOLDER'):
            aug_folder = line.split('=')[1].strip().replace('\n','')
        if line.startswith('PADDING_WIDTH'):
            p_width = float(line.split('=')[1].strip().replace('\n',''))/100
        if line.startswith('INPAINT_PIXELS'):
            inpaint_width = int(line.split('=')[1].strip().replace('\n',''))
            
    images_folder      =         'JPEGImages'
    annotations_folder =         'Annotations'  
    config.close()

    # Create folders for outputs    
    if aug_folder not in os.listdir(dataset_path):
        os.mkdir(Path(dataset_path, aug_folder))
        os.mkdir(Path(dataset_path, aug_folder, 'Targets'))
        os.mkdir(Path(dataset_path, aug_folder, 'Annotations'))
        os.mkdir(Path(dataset_path, aug_folder, 'JPEGImages'))


    # parse each annotation file
    # cut targets of size: (bbox shape) + (padding width) + (inpaint pixels)
    # save crops in targ_folder
    
    print('Cropping targets...')
        
    n_files = len(os.listdir(Path(dataset_path, annotations_folder)))
    passed_files=1
    
    for filename in os.listdir(Path(dataset_path, annotations_folder)):
        
        if not filename.endswith('.xml'): continue
            
        fullname = Path(dataset_path, annotations_folder, filename)    
        tree = ET.parse(fullname)    
        root = tree.getroot()    
        bbox_num = 0
        img = cv2.imread(str(Path(dataset_path, images_folder, filename[:-3]+'jpg')))
    
        for rec in root:
            
            # get source image size
            if rec.tag == 'size': 
                height = int(rec.findtext('height'))
                width = int(rec.findtext('width'))
                
            # list all available bboxes        
            if rec.tag == 'object': 
                for box in rec:
                    if box.tag=='bndbox':
                        
                        # get bbox corners
                        ymin = int(box.findtext('ymin'))
                        ymax = int(box.findtext('ymax'))
                        xmin = int(box.findtext('xmin'))
                        xmax = int(box.findtext('xmax'))
                        
                        if (xmax-xmin)>(ymax-ymin):
                            frame_px = int((xmax-xmin)*p_width)
                        else:
                            frame_px = int((ymax-ymin)*p_width)
                            
                        new_xmin = xmin - frame_px - inpaint_width
                        new_xmax = xmax + frame_px + inpaint_width
                        new_ymin = ymin - frame_px - inpaint_width
                        new_ymax = ymax + frame_px + inpaint_width
                        
                        # do not proceed if target+frame are outside of image
                        if (new_xmin<1 or new_xmax>width-1 or new_ymin<1 or new_ymax>height-1):continue
                        
                        # cut&save target
                        targ = img[new_ymin:new_ymax, new_xmin:new_xmax]
                        cv2.imwrite(str(Path(dataset_path, aug_folder, 'Targets', filename[:-4]+'_'+str(bbox_num)+'_target.jpg')), targ)
                        
                        # goto next bbox in current file
                        bbox_num = bbox_num + 1
               
        if passed_files in np.int8(np.linspace(0,n_files,10)): print(str(int(passed_files/n_files*10*10))+'% done...')
        passed_files+=1
    
    print('Crop completed.')
    
    # transform cropped targets, then place them on backgrounds
    
    n_files = len(os.listdir(Path(dataset_path, backs_folder)))*len(os.listdir(Path(dataset_path, aug_folder, 'Targets')))
    passed_files=1
    
    print('Starting augmentation...')
    
    for background_file in os.listdir(Path(dataset_path, backs_folder)):
        
        back = cv2.imread(str(Path(dataset_path, backs_folder, background_file)))
        
        for target_file in os.listdir(Path(dataset_path, aug_folder, 'Targets')):    
            
            targ = cv2.imread(str(Path(dataset_path, aug_folder, 'Targets', target_file)))        
            
            # transform target image
            targ, b_mask, g_mask, t_frame = transform_target_image(targ, p_width, inpaint_width)
            
            # place transformed target image on background image
            res_img, bbox = place_img_to_background(targ, back, b_mask, g_mask, t_frame)
            
            # generate annotation
            tree = ET.parse('annotation_template.xml')    
            root = tree.getroot()    
    
            for rec in root:
    
                if rec.tag == 'filename':
                    rec.text = target_file[:-4]+'_on_'+ background_file[:-4] + '.jpg'
                
                if rec.tag == 'size':
                    rec[0].text = str(res_img.shape[0])
                    rec[1].text = str(res_img.shape[1])
                
                if rec.tag == 'object':
                    rec[4][0].text = str(bbox['ymin'])
                    rec[4][1].text = str(bbox['xmin'])
                    rec[4][2].text = str(bbox['ymax'])
                    rec[4][3].text = str(bbox['xmax'])          
            
            # uncomment line below if need to draw bboxes on images
            # res_img = draw_bbox(res_img, bbox)
    
            # save files
            tree.write(str(Path(dataset_path, aug_folder, 'Annotations', target_file[:-4]+'_on_'+ background_file[:-4]+'.xml')))
            cv2.imwrite(str(Path(dataset_path, aug_folder, 'JPEGImages', target_file[:-4]+'_on_'+ background_file[:-4]+'.jpg')), res_img)
           
            if passed_files in np.int8(np.linspace(0,n_files,10)): print(str(int(passed_files/n_files*10*10))+'% done...')
            passed_files+=1
            
    print('All images are processed.')

if __name__ == "__main__":
    main()