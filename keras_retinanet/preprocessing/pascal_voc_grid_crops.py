from itertools import groupby
import os
from typing import NamedTuple

from PIL import Image
import random

from ..preprocessing.pascal_voc import PascalVocGenerator
from ..utils.grid_cropper import ImageGridCropper
from ..utils.image import compute_resize_scale, resize_image


class CropReference(NamedTuple):
    image_index: int
    crop_number: int


class PascalVocGridCropsGenerator(PascalVocGenerator):

    def __init__(self,
                 window_w,
                 window_h,
                 overlap_w,
                 overlap_h,
                 min_cropped_bbox_square,
                 group_by_image=True,
                 **kwargs):
        self.cropper = ImageGridCropper(window_w, window_h, overlap_w, overlap_h, min_cropped_bbox_square)
        self.group_by_image = group_by_image
        self.crops_grid_by_size = dict()
        self.image_sizes = dict()
        self.image_cache = dict()

        super(PascalVocGridCropsGenerator, self).__init__(**kwargs)

    @staticmethod
    def _calc_aspect_ratio(width, height):
        return float(width) / float(height)

    def _get_image_size(self, image_index):
        if image_index not in self.image_sizes:
            path = os.path.join(self.data_dir, 'JPEGImages', self.image_names[image_index] + self.image_extension)
            # turns out to be quicker way to get image size only than cv2.imread
            im = Image.open(path)
            width, height = im.size

            scale = 1
            if not self.no_resize:
                scale = compute_resize_scale(
                    (height, width, -1),
                    min_side=self.image_min_side,
                    max_side=self.image_max_side)
                width = int(width * scale)
                height = int(height * scale)
            self.image_sizes[image_index] = (width, height, scale)

        width, height, _ = self.image_sizes[image_index]
        return width, height

    def _get_crops_range_cached(self, crops_range_cache, image_index):
        w, h, _ = self.image_sizes[image_index]
        if not (w, h) in crops_range_cache:
            crops_range_cache[(w, h)] = list(range(self.cropper.calc_crops_count(w, h)))

        return crops_range_cache[(w, h)]

    def _get_crop_from_grid(self, crop_number, width, height):
        if not (width, height) in self.crops_grid_by_size:
            self.crops_grid_by_size[(width, height)] = self.cropper.get_image_grid(width, height)
        return self.crops_grid_by_size[(width, height)][crop_number]

    def _get_image_cached(self, image_index):
        if image_index not in self.image_cache:
            self.image_cache.clear()
            image = super().load_image(image_index)

            scale = 1
            if not self.no_resize:
                image, scale = resize_image(image, self.image_min_side, self.image_max_side)
            self.image_cache[image_index] = (scale, image)
        return self.image_cache[image_index]

    def _load_crop(self, crop_reference):
        scale, crop_image = self._get_image_cached(crop_reference.image_index)
        height, width, _ = crop_image.shape

        crop = self._get_crop_from_grid(crop_reference.crop_number, width, height)
        return crop_image[crop.ymin:crop.ymax, crop.xmin:crop.xmax]

    def group_images(self):

        """
        Overload of Generator base method. Forms groups of crops instead of image groups
        """
        images_indexes = list(range(super().size()))

        # determine the order of the images
        order = list(images_indexes)
        if self.group_method == 'random':
            random.shuffle(order)
        elif self.group_method == 'ratio':
            order.sort(key=lambda img: self._calc_aspect_ratio(*self._get_image_size(img)))

        # calculate continuous crops references list,
        # with indexes of the crop's image and position of the crop inside it
        range_cache = dict()

        crops = [CropReference(img, crop) for img in order for crop in
                 self._get_crops_range_cached(range_cache, img)]

        # divide crops into groups, divided either by images or batch_size
        if self.group_by_image:
            self.groups = [list(img_crops) for _, img_crops in groupby(crops, lambda ref: ref.image_index)]
        else:
            crops_count = len(crops)
            batch_borders = range(0, crops_count, self.batch_size)
            self.groups = [[crops[c % crops_count] for c in range(b, b + self.batch_size)] for b in batch_borders]

        self.crop_references = [crop for group in self.groups for crop in group]

    def resize_image(self, image):
        """ Overloads base generator method, does nothing as only crop, not whole image is passed here
        """
        return image, 1

    def load_image(self, image_index):
        """ Overloads base method, loading an crop instead of image with image_index.
        """
        crop_reference = self.crop_references[image_index]
        return self._load_crop(crop_reference)

    def load_image_group(self, group):
        """ Overloads base method, loading an crops group instead of images group.
        """
        return [self._load_crop(crop_ref) for crop_ref in group]


    def load_annotations(self, crop_index):
        crop_reference = self.crop_references[crop_index]
        width, height, scale = self.image_sizes[crop_reference.image_index]
        image_annotations = super().load_annotations(crop_reference.image_index)
        image_annotations['bboxes'] *= scale
        crop_rectangle = self._get_crop_from_grid(crop_reference.crop_number, width, height)
        return self.cropper.calc_annotations(image_annotations['labels'], image_annotations['bboxes'],
                                                        crop_rectangle)


    def load_annotations_group(self, group):
        """ Load annotations for all images in group and cut them corresponding to crops.
        """
        image_annotations = dict()
        group_annotations = []
        for crop in group:
            width, height, scale = self.image_sizes[crop.image_index]

            if crop.image_index not in image_annotations:
                image_annotations[crop.image_index] = super().load_annotations(crop.image_index)
                image_annotations[crop.image_index]['bboxes'] *= scale

            annotations = image_annotations[crop.image_index]
            assert (isinstance(annotations, dict)), \
                '\'load_annotations\' should return a list of dictionaries, received: {}'.format(type(annotations))
            assert ('labels' in annotations), \
                '\'load_annotations\' should return a list of dictionaries that contain \'labels\' and \'bboxes\'.'
            assert ('bboxes' in annotations), \
                '\'load_annotations\' should return a list of dictionaries that contain \'labels\' and \'bboxes\'.'


            crop_rectangle = self._get_crop_from_grid(crop.crop_number, width, height)
            crop_annotation = self.cropper.calc_annotations(annotations['labels'], annotations['bboxes'],
                                                            crop_rectangle)
            group_annotations.append(crop_annotation)

        return group_annotations

    def size(self):
        """ Size of the cropped dataset.
        """
        return sum([len(group) for group in self.groups])

if __name__ == '__main__':
    generator = PascalVocGridCropsGenerator(
        500, 500, 150, 150, 0.75, group_by_image=True, data_dir="../../../data/laddv4/spring", set_name='test')

    group_index = 41
    group = generator.groups[group_index]
    crops_group = generator.load_image_group(group)
    annotations_group = generator.load_annotations_group(group)
    print(annotations_group)
