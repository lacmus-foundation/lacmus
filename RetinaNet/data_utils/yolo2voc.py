# Script to convert yolo annotations to voc format
import os
import xml.etree.cElementTree as ET
from PIL import Image
import argparse

CLASS_MAPPING = {
    '0': 'Pedestrian'
    # Add remaining classes here.
}


def create_root(file_prefix, width, height):
    root = ET.Element("annotation")
    ET.SubElement(root, "filename").text = "{}.jpg".format(file_prefix)
    ET.SubElement(root, "folder").text = "images"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"
    return root


def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = voc_label[0]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = str(0)
        ET.SubElement(obj, "difficult").text = str(0)
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(voc_label[1])
        ET.SubElement(bbox, "ymin").text = str(voc_label[2])
        ET.SubElement(bbox, "xmax").text = str(voc_label[3])
        ET.SubElement(bbox, "ymax").text = str(voc_label[4])
    return root


def create_file(file_prefix, width, height, voc_labels, dest_dir):
    root = create_root(file_prefix, width, height)
    root = create_object_annotation(root, voc_labels)
    tree = ET.ElementTree(root)
    tree.write("{}/{}.xml".format(dest_dir, file_prefix))


def read_file(filename, src_dir, dest_dir):
    file_prefix = filename.split(".txt")[0]
    if os.path.isfile("{}/{}.JPG".format(src_dir, file_prefix)):
        os.rename("{}/{}.JPG".format(src_dir, file_prefix), "{}/{}.jpg".format(src_dir, file_prefix))
        print("renamed to {}.jpg".format(file_prefix))

    image_file_name = "{}.jpg".format(file_prefix)
    img = Image.open("{}/{}".format(src_dir, image_file_name))
    w, h = img.size
    with open("{}/{}".format(src_dir, filename), 'r') as file:
        lines = file.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip()
            data = line.split()
            voc.append(CLASS_MAPPING.get(data[0]))
            bbox_width = float(data[3]) * w
            bbox_height = float(data[4]) * h
            center_x = float(data[1]) * w
            center_y = float(data[2]) * h
            voc.append(int(center_x - (bbox_width / 2)))
            voc.append(int(center_y - (bbox_height / 2)))
            voc.append(int(center_x + (bbox_width / 2)))
            voc.append(int(center_y + (bbox_height / 2)))
            voc_labels.append(voc)
        create_file(file_prefix, w, h, voc_labels, dest_dir)
    print("Processing complete for file: {}".format(filename))

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Script which converts yolo to pascal voc')
    parser.add_argument('--src', help='source annotation dir.')
    parser.add_argument('--dest', help='destination annotation dir.')
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)

    if not os.path.exists(args.dest):
        os.makedirs(args.dest)
    for filename in os.listdir(args.src):
        if filename.endswith('txt'):
            read_file(filename,args.src , args.dest)
        else:
            print("Skipping file: {}".format(filename))


if __name__ == "__main__":
    main()
