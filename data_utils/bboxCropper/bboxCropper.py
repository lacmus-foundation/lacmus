import cv2
from pathlib import Path
import xml.etree.ElementTree as ET 
import numpy as np
import os
import random

def main():
    
    # open CFG file, define paths and crops shapes  
    
    config = open('config.cfg')
    for line in config:
        if line.startswith('CROP_SIZE'):
            crop_size = int(line.split('=')[1].strip().replace('\n',''))
        if line.startswith('DATASET_PATH'):
            dataset_path = Path(line.split('=')[1].strip().replace('\n',''))
        if line.startswith('CROPS_FOLDER'):
            crops_folder = line.split('=')[1].strip().replace('\n','')
        if line.startswith('FRAMES_FOLDER'):
            frames_folder = line.split('=')[1].strip().replace('\n','')
        if line.startswith('MASKS_FOLDER'):
            masks_folder = line.split('=')[1].strip().replace('\n','')
        if line.startswith('INVERT_MASKS'):
            invert_masks = line.split('=')[1].strip().replace('\n','')
            if invert_masks.lower() in ['false']:
                invert_masks = False
            else:
                invert_masks = True
            
    images_folder      =         'JPEGImages'
    annotations_folder =         'Annotations'  
    config.close()

    print('Dataset location: ', dataset_path)
    
   # Create folders for outputs
    if frames_folder not in os.listdir(dataset_path):
        os.mkdir(Path(dataset_path, frames_folder))
        print('Created folder: ', Path(dataset_path, frames_folder))
    if crops_folder not in os.listdir(dataset_path):
        os.mkdir(Path(dataset_path, crops_folder))
        print('Created folder: ', Path(dataset_path, crops_folder))
    if masks_folder not in os.listdir(dataset_path):
        os.mkdir(Path(dataset_path, masks_folder))
        print('Created folder: ', Path(dataset_path, masks_folder))

    print('Processing started...')
        
    # parse each annotation file
    
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
                        
                        # get initial bbox corners
                        ymin = int(box.findtext('ymin'))
                        ymax = int(box.findtext('ymax'))
                        xmin = int(box.findtext('xmin'))
                        xmax = int(box.findtext('xmax'))
                        
                        # calculate necessary padding to get crop of crop_size
                        padding_w = int((crop_size - (xmax - xmin))/2.)
                        padding_h = int((crop_size - (ymax - ymin))/2.)
                        
                        # get random shift within 25% of crop_size from bbox center
                        random_dx = int((random.random()-.5)*.5*crop_size)
                        random_dy = int((random.random()-.5)*.5*crop_size)
                        
                        # calculate crop corners
                        new_xmin = xmin - padding_w + random_dx
                        new_xmax = xmax + padding_w + random_dx
                        new_ymin = ymin - padding_h + random_dy
                        new_ymax = ymax + padding_h + random_dy
                        
                        # do not proceed if crop is outside of image
                        if (new_xmin<1 or new_xmax>width-1 or new_ymin<1 or new_ymax>height-1):continue
                        
                        dx = new_xmax - new_xmin
                        dy = new_ymax - new_ymin
                        
                        # correct crop corners to get exact crop_size
                        if dx<crop_size:
                            if ((new_xmax+new_xmin)/2.)<(width/2.):
                                new_xmax+=1
                            else:
                                new_xmin-=1
                                
                        if dy<crop_size:
                            if ((new_ymax+new_ymin)/2.)<(height/2.):
                                new_ymax+=1
                            else:
                                new_ymin-=1
                       
                        # create crop
                        crop = img.copy()
                        crop = crop[new_ymin:new_ymax, new_xmin:new_xmax]
                        
                        # create binary mask
                        mask = np.zeros_like(img).astype(bool)
                        mask[ymin:ymax, xmin:xmax]=True
                        if invert_masks: mask = np.invert(mask)
                        mask = (mask[new_ymin:new_ymax, new_xmin:new_xmax][:,:,0]*255).astype('uint8')
                                            
                        # cut out bbox contents from the crop to get a frame
                        frame = img.copy()
                        frame[ymin:ymax, xmin:xmax] = 0
                        frame = frame[new_ymin:new_ymax, new_xmin:new_xmax]
                        
                        # save all this stuff
                        cv2.imwrite(str(Path(dataset_path, masks_folder, filename[:-4]+'_'+str(bbox_num)+'_mask.png')), mask)               
                        cv2.imwrite(str(Path(dataset_path, frames_folder, filename[:-4]+'_'+str(bbox_num)+'_crop.jpg')), frame)
                        cv2.imwrite(str(Path(dataset_path, crops_folder, filename[:-4]+'_'+str(bbox_num)+'_pic.jpg')), crop)
                        
                        # goto next bbox in current file
                        bbox_num = bbox_num + 1
                        
        if passed_files in range(int(n_files/10), n_files, int(n_files/10)): print(str(int(passed_files/n_files*10*10)+1)+'% done...')
        passed_files+=1

    print('Crop completed.')                   
                            
if __name__=='__main__':
    main()
