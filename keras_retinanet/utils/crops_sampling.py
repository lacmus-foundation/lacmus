import random


class Crop:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = int(x_min)
        self.y_min = int(y_min)
        self.x_max = int(x_max)
        self.y_max = int(y_max)
        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min


class EmptyCrop(Crop):
    def __init__(self, *args):
        super(EmptyCrop, self).__init__(*args)

    def intersect(self, bbox: '[x_min, y_min, x_max, y_max]'):
        x_inside = (self.x_min <= bbox[0] <= self.x_max) or (self.x_min <= bbox[2] <= self.x_max)
        y_inside = (self.y_min <= bbox[1] <= self.y_max) or (self.y_min <= bbox[3] <= self.y_max)
        return x_inside and y_inside

    def crop_around(self, bbox: '[x_min, y_min, x_max, y_max]', min_width, min_height):
        margins = []

        if self.height > min_height:
            if bbox[0] - self.x_min > min_width:
                # left margin, from top to bottom
                margins.append(EmptyCrop(self.x_min, self.y_min, bbox[0] - 1, self.y_max))

            if self.x_max - bbox[2] > min_width:
                # right margin, from top to bottom
                margins.append(EmptyCrop(bbox[2] + 1, self.y_min, self.x_max, self.y_max))

        if self.width > min_width:
            if bbox[1] - self.y_min >= min_height:
                # top margin, fro left to right
                margins.append(EmptyCrop(self.x_min, self.y_min, self.x_max, bbox[1] - 1))

            if self.y_max - bbox[3] >= min_height:
                # bottom margin, from left to right
                margins.append(EmptyCrop(self.x_min, bbox[3] + 1, self.x_max, self.y_max))

        return margins


class NegativeSampling:
    def __init__(self, image_width, image_height, crop_width, crop_height, bboxes):
        self.crop_width = crop_width
        self.crop_height = crop_height

        self.empty_areas = [EmptyCrop(0, 0, image_width, image_height)]

        for bbox in bboxes:
            area_index = 0
            while area_index < len(self.empty_areas):
                area = self.empty_areas[area_index]
                if area.intersect(bbox):
                    around_bbox = area.crop_around(bbox, crop_width, crop_height)
                    self.empty_areas[area_index:area_index + 1] = around_bbox
                    area_index += len(around_bbox)
                else:
                    area_index += 1

    def __get_random_crop_inside(self, area: EmptyCrop):
        gap_x = area.width - self.crop_width
        gap_y = area.height - self.crop_height
        x_min = area.x_min + random.randint(0, gap_x)
        y_min = area.y_min + random.randint(0, gap_y)
        x_max = x_min + self.crop_width - 1
        y_max = y_min + self.crop_height - 1

        return EmptyCrop(x_min, y_min, x_max, y_max)

    @property
    def samples_available(self):
        return len(self.empty_areas) > 0

    def get_samples(self, count):
        candidate_areas = random.choices(self.empty_areas, k=count)
        # as random shift is used, samples will be different even when there is only one empty area
        return [self.__get_random_crop_inside(area) for area in candidate_areas]


class PositiveSampling:
    def __init__(self, image_width, image_height, crop_width, crop_height, bboxes):
        self.image_width = image_width
        self.image_height = image_height
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.bboxes = bboxes

    def __get_random_crop_around(self, bbox):
        x_from = max(0, bbox[2] - self.crop_width)
        x_to = min(bbox[0], self.image_width - self.crop_width)
        y_from = max(0, bbox[3] - self.crop_height)
        y_to = min(bbox[1], self.image_height - self.crop_height)

        x_min = random.randint(x_from, x_to)
        x_max = x_min + self.crop_width - 1
        y_min = random.randint(y_from, y_to)
        y_max = y_min + self.crop_height - 1
        return Crop(x_min, y_min, x_max, y_max)

    @property
    def samples_available(self):
        return len(self.bboxes) > 0

    def get_samples(self, count=None):
        crops = []
        if not count:
            samples_bboxes = self.bboxes
        else:
            samples_bboxes = random.choices(self.bboxes, k=count)

        # as random shift is used, samples will be different even when count > len(bboxes)
        return [self.__get_random_crop_around(bbox) for bbox in samples_bboxes]


if __name__ == '__main__':
    import numpy as np
    import sys

    crop = EmptyCrop(0, 0, 200, 200)

    bbox_inside = np.array([50, 50, 150, 150])
    if crop.intersect(bbox_inside):
        print('[OK] Test bbox inside crop')
    else:
        print('[FAILED] Test bbox inside crop')
        sys.exit(-1)

    bbox_outside = np.array([300, 300, 300, 300])
    if not crop.intersect(bbox_outside):
        print('[OK] Test bbox outside crop')
    else:
        print('[FAILED] Test bbox outside crop')
        sys.exit(-1)

    bbox_intersect = np.array([150, 150, 250, 250])
    if crop.intersect(bbox_intersect):
        print('[OK] Test bbox intersecting crop')
    else:
        print('[FAILED] Test bbox intersecting crop')
        sys.exit(-1)

    crops_around = crop.crop_around(bbox_inside, 0, 0)
    if (len(crops_around) == 4) and (not any([c.intersect(bbox_inside) for c in crops_around])):
        print('[OK] Test cropping around inner bbox')
    else:
        print('[FAILED] Test cropping around inner bbox')
        sys.exit(-1)

    crops_around = crop.crop_around(bbox_intersect, 100, 100)
    if (len(crops_around) == 2) and (not any([c.intersect(bbox_intersect) for c in crops_around])):
        print('[OK] Test cropping around intersecting bbox')
    else:
        print('[FAILED] Test cropping around intersecting bbox')
        sys.exit(-1)
