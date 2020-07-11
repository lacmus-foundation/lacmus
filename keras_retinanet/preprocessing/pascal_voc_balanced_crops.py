import itertools
import numpy as np
import random
import os

from PIL import Image

from ..utils.crops_sampling import PositiveSampling, NegativeSampling
from ..preprocessing.pascal_voc import PascalVocGenerator


class CropDescription:
    def __init__(self, image_index, positive):
        self.image_index = image_index
        self.positive = positive

        # Needed to save crop position between load_image_group and load_annotations_group calls
        self.last_x_min = -1
        self.last_y_min = -1


class SamplingBalancer:
    def __init__(self):
        # negative value for extra negative samples generated, positive - for extra positive
        self.imbalance = 0

    def get_samples_balanced(self, count, positive_planned, positive_sampling, negative_sampling):
        negative_planned = not positive_planned
        if positive_planned and self.imbalance > 0:
            if negative_sampling.samples_available:
                counterweight = min(count, self.imbalance)
                samples = negative_sampling.get_samples(counterweight)
                self.imbalance -= counterweight
                reminder = count - counterweight
                if reminder > 0:
                    if positive_sampling.samples_available:
                        samples += positive_sampling.get_samples(reminder)
                    else:
                        samples += negative_sampling.get_samples(reminder)
                        self.imbalance -= reminder
            else:
                # Just as planned. Will try to balance on the next attempt.
                samples = positive_sampling.get_samples(count)
        elif negative_planned and self.imbalance < 0:
            if positive_sampling.samples_available:
                counterweight = min(count, -self.imbalance)
                samples = positive_sampling.get_samples(counterweight)
                self.imbalance += counterweight
                reminder = count - counterweight
                if reminder > 0:
                    if negative_sampling.samples_available:
                        samples += negative_sampling.get_samples(reminder)
                    else:
                        samples += positive_sampling.get_samples(reminder)
                        self.imbalance += counterweight
            else:
                # Just as planned. Will try to balance on the next attempt.
                samples = negative_sampling.get_samples(count)
        elif positive_planned and positive_sampling.samples_available:
            samples = positive_sampling.get_samples(count)
        elif positive_planned and not positive_sampling.samples_available:
            self.imbalance -= count
            samples = negative_sampling.get_samples(count)
        elif negative_planned and negative_sampling.samples_available:
            samples = negative_sampling.get_samples(count)
        elif negative_planned and not negative_sampling.samples_available:
            self.imbalance += count
            samples = positive_sampling.get_samples(count)

        return samples


class PascalVocBalancedCropsGenerator(PascalVocGenerator):

    def __init__(self,
                 crop_width,
                 crop_height,
                 negatives_per_positive=0,
                 **kwargs):
        self.label = 0
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.negatives_per_positive = negatives_per_positive
        self.balancer = SamplingBalancer()
        self.image_cache = dict()
        self.image_bboxes = dict()

        super(PascalVocBalancedCropsGenerator, self).__init__(**kwargs)

    @property
    def no_negatives(self):
        return self.negatives_per_positive == 0

    def _crop_fromImage(self, image, crop):
        return image[crop.y_min:crop.y_max + 1, crop.x_min:crop.x_max + 1]

    def _sample_from_image_cached(self, image_index, count, is_positive):
        if image_index not in self.image_cache:
            self.image_cache.clear()
            image = super().load_image(image_index)
            height, width, _ = image.shape

            self.image_bboxes[image_index] = super().load_annotations(image_index)['bboxes']

            positive_sampling = PositiveSampling(
                width, height, self.crop_width, self.crop_height, self.image_bboxes[image_index])
            if self.no_negatives and positive_sampling.samples_available:
                negative_sampling = None
            else:
                negative_sampling = NegativeSampling(
                    width, height, self.crop_width, self.crop_height, self.image_bboxes[image_index])

            self.image_cache[image_index] = {
                'image': image,
                'positive_sampling': positive_sampling,
                'negative_sampling': negative_sampling
            }

        image = self.image_cache[image_index]['image']
        positive_sampling = self.image_cache[image_index]['positive_sampling']
        negative_sampling = self.image_cache[image_index]['negative_sampling']

        crops = self.balancer.get_samples_balanced(count, is_positive, positive_sampling, negative_sampling)
        return [(self._crop_fromImage(image, crop), crop.x_min, crop.y_min) for crop in crops]

    def size(self):
        """ Size of the cropped dataset.
        """
        return super().size() * (1 + self.negatives_per_positive)

    def image_aspect_ratio_pil(self, image_index):
        path = os.path.join(self.data_dir, 'JPEGImages', self.image_names[image_index] + self.image_extension)
        image = Image.open(path)
        return float(image.width) / float(image.height)

    def group_images(self):
        """
        Overload of Generator base method. Forms groups of crops instead of image groups
        """
        # determine the order of the images
        images_count = super().size()
        order = self.get_images_order(
            images_count, lambda image_index: self.image_aspect_ratio_pil(image_index))

        samples_per_image = 1 + self.negatives_per_positive
        samples = itertools.chain.from_iterable((itertools.repeat(i, samples_per_image) for i in order))

        is_positive = [True] * images_count + [False] * images_count * self.negatives_per_positive
        random.shuffle(is_positive)
        self.crops_references = [CropDescription(image_index=img, positive=p) for img, p in zip(samples, is_positive)]
        crops_count = len(self.crops_references)
        batch_borders = range(0, crops_count, self.batch_size)
        self.groups = [[self.crops_references[c % crops_count] for c in range(b, b + self.batch_size)] for b in
                       batch_borders]

    def resize_image(self, image):
        """ Overloads base generator method, does nothing as only crop, not whole image is passed here
        """
        return image, 1

    def load_image(self, image_index):
        """ Overloads base method, sampling a crop instead of image with image_index.
        """
        crop_description = self.crops_references[image_index]
        crop_info = self._sample_from_image_cached(crop_description.image_index, 1, crop_description.positive)[0]
        crop_description.last_x_min = crop_info[1]
        crop_description.last_y_min = crop_info[2]
        return crop_info[0]

    def load_annotations(self, image_index):
        """
        Overloads base method, loading annotations for crop, with cropped bounding boxes
        """
        crop_description = self.crops_references[image_index]
        crop_bboxes = []

        image_bboxes = self.image_bboxes[crop_description.image_index]

        for bbox in image_bboxes:
            crop_bbox = [0] * 4
            crop_bbox[0] = self._get_offset_inside(bbox[0], crop_description.last_x_min, self.crop_width)
            crop_bbox[1] = self._get_offset_inside(bbox[1], crop_description.last_y_min, self.crop_height)
            crop_bbox[2] = self._get_offset_inside(bbox[2], crop_description.last_x_min, self.crop_width)
            crop_bbox[3] = self._get_offset_inside(bbox[3], crop_description.last_y_min, self.crop_height)

            if (crop_bbox[2] > crop_bbox[0]) and (crop_bbox[3] > crop_bbox[1]):
                crop_bboxes.append(crop_bbox)

        labels = np.full(len(crop_bboxes), self.label)
        crop_bboxes = crop_bboxes or np.empty((0, 4))
        return {
                'labels': labels,
                'bboxes': np.array(crop_bboxes)
            }


    def load_image_group(self, group):
        """ Overloads base method, loading an crops group instead of images group.
        """
        subgroups = itertools.groupby(group, lambda c: (c.image_index, c.positive))
        image_crops = []
        for key, subgroup in subgroups:
            subgroup = list(subgroup)
            crops_infos = self._sample_from_image_cached(key[0], len(subgroup), key[1])
            image_crops += [info[0] for info in crops_infos]
            for crop, description in zip(crops_infos, subgroup):
                description.last_x_min = crop[1]
                description.last_y_min = crop[2]

        return image_crops

    @staticmethod
    def _get_offset_inside(coordinate, min_border, size):
        offset = max(0, coordinate - min_border)
        return min(size, offset)

    def load_annotations_group(self, group):
        group_annotations = []
        for crop_description in group:
            crop_bboxes = []
            if crop_description.image_index not in self.image_bboxes:
                self.image_bboxes[crop_description.image_index] = super().load_annotations(crop_description.image_index)

            image_bboxes = self.image_bboxes[crop_description.image_index]
            for bbox in image_bboxes:
                crop_bbox = [0] * 4
                crop_bbox[0] = self._get_offset_inside(bbox[0], crop_description.last_x_min, self.crop_width)
                crop_bbox[1] = self._get_offset_inside(bbox[1], crop_description.last_y_min, self.crop_height)
                crop_bbox[2] = self._get_offset_inside(bbox[2], crop_description.last_x_min, self.crop_width)
                crop_bbox[3] = self._get_offset_inside(bbox[3], crop_description.last_y_min, self.crop_height)

                if (crop_bbox[2] > crop_bbox[0]) and (crop_bbox[3] > crop_bbox[1]):
                    crop_bboxes.append(crop_bbox)

            labels = np.full(len(crop_bboxes), self.label)
            crop_bboxes = crop_bboxes or np.empty((0, 4))
            group_annotations.append(
                {
                    'labels': labels,
                    'bboxes': np.array(crop_bboxes)
                })
            
        return group_annotations


if __name__ == '__main__':
    import sys

    neg_to_pos = 3
    batch = 8
    generator = PascalVocBalancedCropsGenerator(
        1333, 800,
        negatives_per_positive=neg_to_pos,
        batch_size=batch,
        data_dir="../../../data/laddv4/spring",
        set_name='test')
    groups = [[crop.image_index for crop in group] for group in generator.groups]
    if all([len(group) == batch for group in groups]):
        print('[OK] Testing generator batch size')
    else:
        print('[FAILED] Testing generator batch size')
        sys.exit(-1)

    if [len(set(group)) == batch // (1 + neg_to_pos) for group in groups]:
        print('[OK] Testing generator image samples ordering')
    else:
        print('[FAILED] Testing generator image samples ordering')
        sys.exit(-1)

    test_group = generator.load_image_group(generator.groups[-1])
    if all([img.shape == (800, 1333, 3) for img in test_group]):
        print('[OK] Testing crop sizes')
    else:
        print('[FAILED] Testing crop sizes')
        print([img.shape for img in test_group])
        sys.exit(-1)

    generator.load_annotations_group(generator.groups[-1])

    samples_types = [crop.positive for group in generator.groups for crop in group]
    positives = [st for st in samples_types if st]
    negatives = [st for st in samples_types if not st]
    if len(negatives) // len(positives) == neg_to_pos:
        print('[OK] Testing negative to positive samples rate')
    else:
        print('[FAILED] Testing negative to positive samples rate')
        sys.exit(-1)


    class DummySampling:
        def __init__(self, sample, available):
            self.sample = sample
            self.samples_available = available

        def get_samples(self, count):
            return [self.sample] * count


    from ..utils.crops_sampling import Crop

    positive_crop = Crop(0, 0, 0, 0)
    negative_crop = Crop(100, 100, 100, 100)
    positive_sampling = DummySampling(positive_crop, True)
    negative_sampling = DummySampling(negative_crop, True)
    balancer = SamplingBalancer()

    samples = balancer.get_samples_balanced(4, True, positive_sampling, negative_sampling)
    if ((balancer.imbalance == 0) and len(samples) == 4) and all([s == positive_crop for s in samples]):
        print('[OK] Testing positive balanced sampling')
    else:
        print('[FAILED] Testing positive balanced sampling')
        sys.exit(-1)

    samples = balancer.get_samples_balanced(4, False, positive_sampling, negative_sampling)
    if ((balancer.imbalance == 0) and len(samples) == 4) and all([s == negative_crop for s in samples]):
        print('[OK] Testing negative balanced sampling')
    else:
        print('[FAILED] Testing negative balanced sampling')
        sys.exit(-1)

    positive_sampling.samples_available = False
    samples = balancer.get_samples_balanced(4, True, positive_sampling, negative_sampling)
    if ((balancer.imbalance == -4) and len(samples) == 4) and all([s == negative_crop for s in samples]):
        print('[OK] Testing negative imbalanced sampling')
    else:
        print('[FAILED] Testing negative imbalanced sampling')
        sys.exit(-1)

    positive_sampling.samples_available = True
    samples = balancer.get_samples_balanced(6, False, positive_sampling, negative_sampling)
    counterweight_samples = samples[:4]
    negative_samples = samples[4:]
    if ((balancer.imbalance == 0)
        and len(negative_samples) == 2) \
            and all([s == positive_crop for s in counterweight_samples]) \
            and all([s == negative_crop for s in negative_samples]):
        print('[OK] Testing re-balancing sampling with positives')
    else:
        print('[FAILED] Testing re-balancing sampling with positives')
        sys.exit(-1)

    negative_sampling.samples_available = False
    samples = balancer.get_samples_balanced(4, False, positive_sampling, negative_sampling)
    if ((balancer.imbalance == 4) and len(samples) == 4) and all([s == positive_crop for s in samples]):
        print('[OK] Testing positive imbalanced sampling')
    else:
        print('[FAILED] Testing positive imbalanced')
        sys.exit(-1)

    negative_sampling.samples_available = True
    samples = balancer.get_samples_balanced(2, True, positive_sampling, negative_sampling)
    if ((balancer.imbalance == 2)
        and len(samples) == 2) \
            and all([s == negative_crop for s in samples]):
        print('[OK] Testing re-balancing sampling with negatives')
    else:
        print('[FAILED] Testing re-balancing sampling with negatives')
        sys.exit(-1)


    crop = (100, 100, 200, 200)
    bbox = (150, 150, 250, 250)
    width = crop[2] - crop[0]
    height = crop[3] - crop[1]
    x_min = PascalVocBalancedCropsGenerator._get_offset_inside(bbox[0], crop[0], width)
    y_min = PascalVocBalancedCropsGenerator._get_offset_inside(bbox[1], crop[1], height)
    x_max = PascalVocBalancedCropsGenerator._get_offset_inside(bbox[2], crop[2], width)
    y_max = PascalVocBalancedCropsGenerator._get_offset_inside(bbox[3], crop[3], height)
    if (x_min == 50) and (y_min == 50) and (x_max == 50) and (y_max == 50):
        print("[OK] Testing coordinate offset inside a crop")
    else:
        print("[FAILED] Testing coordinate offset inside a crop")
        sys.exit(-1)


