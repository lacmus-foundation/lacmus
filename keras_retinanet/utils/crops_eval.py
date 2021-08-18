from .eval import _compute_ap
from .anchors import compute_overlap

from tensorflow import keras
import numpy as np
import time
import cv2
import progressbar
assert(callable(progressbar.progressbar)), "Using wrong progressbar module, install 'progressbar2' instead."

from .visualization import draw_detections, draw_annotations
import os


def _get_detections(generator, model, score_threshold=0.05, max_detections=100, save_path=None):
    """ Get the detections using cropping generator, placing detections of the same image crops together.

    The result is a list of lists such that the size is:
        all_detections[num_images][num_classes] = detections[num_detections, 4 + num_classes]

    # Arguments
        generator       : The generator used to run images through the model and cut them to crops.
        model           : The model to run on the crops.
        score_threshold : The score confidence threshold to use.
        max_detections  : The maximum number of detections to use per crop.
        save_path       : The path to save the full images with visualized detections to.
    # Returns
        A list of lists containing the detections for each image in the generator.
    """

    images_count = generator.size()

    # Ensure that generator groups crops by images, to be able to distinguish between them
    if not generator.group_by_image or len(generator.groups) != images_count:
        raise ValueError('Need crop generator to have crops grouped by image!')

    image_indexes = list(range(images_count))
    all_detections = [[None for i in range(generator.num_classes()) if generator.has_label(i)] for j in image_indexes]
    all_inferences = [0.0 for i in range(images_count)]

    for group in progressbar.progressbar(generator.groups, prefix='Running network: '):
        image_index = _get_image_index(group)

        full_image = None
        if save_path is not None:
            full_image = generator.load_image(image_index)
            if keras.backend.image_data_format() == 'channels_first':
                full_image = full_image.transpose((2, 0, 1))
            draw_annotations(full_image, generator.load_annotations(image_index),
                             label_to_name=generator.label_to_name)

        for crop_reference in group:
            crop_image = generator.load_crop(crop_reference)
            crop_image = generator.preprocess_image(crop_image)

            if keras.backend.image_data_format() == 'channels_first':
                crop_image = crop_image.transpose((2, 0, 1))

            # run network
            start = time.time()
            boxes, scores, labels = model.predict_on_batch(np.expand_dims(crop_image, axis=0))[:3]
            inference_time = time.time() - start

            # correct boxes for crop offset and scale
            dx, dy, scale = generator.get_crop_transformations(crop_reference)
            # shift by crop offset
            boxes[:, :, 0] += dx
            boxes[:, :, 2] += dx
            boxes[:, :, 1] += dy
            boxes[:, :, 3] += dy

            # apply division in order to scale bboxes back to original size
            boxes /= scale

            # select indices which have a score above the threshold
            indices = np.where(scores[0, :] > score_threshold)[0]

            # select those scores
            scores = scores[0][indices]
            # find the order with which to sort the scores
            scores_sort = np.argsort(-scores)[:max_detections]

            # select detections
            crop_boxes = boxes[0, indices[scores_sort], :]
            crop_scores = scores[scores_sort]
            crop_labels = labels[0, indices[scores_sort]]
            crop_detections = np.concatenate(
                    [crop_boxes, np.expand_dims(crop_scores, axis=1), np.expand_dims(crop_labels, axis=1)], axis=1)

            if full_image is not None:
                draw_detections(full_image, crop_boxes, crop_scores, crop_labels,
                                    label_to_name=generator.label_to_name, score_threshold=score_threshold)

            # copy detections to all_detections
            for label in range(generator.num_classes()):
                if not generator.has_label(label):
                    continue

                crop_label_detections = crop_detections[crop_detections[:, -1] == label, :-1]
                if all_detections[image_index][label] is None:
                    all_detections[image_index][label] = crop_label_detections
                else:
                    all_detections[image_index][label] = np.concatenate([
                            all_detections[image_index][label], crop_label_detections])

            all_inferences[image_index] += inference_time

        if full_image is not None and save_path is not None:
            cv2.imwrite(os.path.join(save_path, '{}.png'.format(image_index)), full_image)

    return all_detections, all_inferences


def _get_image_index(group):
    group_images = [c.image_index for c in group]
    if len(set(group_images)) != 1:
        raise ValueError('Need crop generator to have crops grouped by image!')
    image_index = group_images[0]
    return image_index


def _get_annotations(generator):
    """ Get the ground truth annotations for the whole image from the generator.

    The result is a list of lists such that the size is:
        all_detections[num_images][num_classes] = annotations[num_detections, 5]

    # Arguments
        generator : The generator used to retrieve ground truth annotations.
    # Returns
        A list of lists containing the annotations for each image in the generator.
    """

    images_count = generator.size()

    # Ensure that generator groups crops by images, to be able to distinguish between them
    if not generator.group_by_image or len(generator.groups) != images_count:
        raise ValueError('Need crop generator to have crops grouped by image!')

    image_indexes = list(range(images_count))

    all_annotations = [[None for i in range(generator.num_classes())] for j in image_indexes]

    for group in progressbar.progressbar(generator.groups, prefix='Running network: '):
        image_index = _get_image_index(group)

        # load the annotations
        annotations = generator.load_annotations(image_index)

        # copy detections to all_annotations
        for label in range(generator.num_classes()):
            if not generator.has_label(label):
                continue

            all_annotations[image_index][label] = annotations['bboxes'][annotations['labels'] == label, :].copy()

    return all_annotations


def evaluate(
    generator,
    model,
    iou_threshold=0.5,
    score_threshold=0.05,
    max_detections=100,
    save_path=None
):
    """ Evaluate a given dataset using a given model and grid crops generator.
        Note: the code is slightly different to its eval.py counterpart

    # Arguments
        generator       : The generator that represents the cropped dataset to evaluate.
        model           : The model to evaluate.
        iou_threshold   : The threshold used to consider when a detection is positive or negative.
        score_threshold : The score confidence threshold to use for detections.
        max_detections  : The maximum number of detections to use per image.
        save_path       : The path to save images with visualized detections to.
    # Returns
        A dict mapping class names to mAP scores and inference time.
    """

    # gather all detections and annotations
    all_detections, all_inferences = _get_detections(generator, model, score_threshold=score_threshold,
                                                     max_detections=max_detections, save_path=save_path)
    all_annotations = _get_annotations(generator)
    average_precisions = {}

    # process detections and annotations
    for label in range(generator.num_classes()):
        if not generator.has_label(label):
            continue

        false_positives = np.zeros((0,))
        true_positives = np.zeros((0,))
        scores = np.zeros((0,))
        num_annotations = 0.0

        for group in progressbar.progressbar(generator.groups, prefix='Running network: '):
            image_index = _get_image_index(group)

            detections = all_detections[image_index][label]
            annotations = all_annotations[image_index][label]
            num_annotations += annotations.shape[0]
            detected_annotations = []

            for d in detections:
                scores = np.append(scores, d[4])

                if annotations.shape[0] == 0:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)
                    continue

                overlaps = compute_overlap(np.expand_dims(d, axis=0), annotations)
                assigned_annotation = np.argmax(overlaps, axis=1)
                max_overlap = overlaps[0, assigned_annotation]

                if max_overlap >= iou_threshold:
                    if assigned_annotation not in detected_annotations:
                        false_positives = np.append(false_positives, 0)
                        true_positives  = np.append(true_positives, 1)
                        detected_annotations.append(assigned_annotation)
                    else:
                        false_positives = np.append(false_positives, 0)
                        true_positives = np.append(true_positives, 0)
                else:
                    false_positives = np.append(false_positives, 1)
                    true_positives  = np.append(true_positives, 0)

        # no annotations -> AP for this class is 0 (is this correct?)
        if num_annotations == 0:
            average_precisions[label] = 0, 0
            continue

        # sort by score
        indices = np.argsort(-scores)
        false_positives = false_positives[indices]
        true_positives = true_positives[indices]

        # compute false positives and true positives
        false_positives = np.cumsum(false_positives)
        true_positives = np.cumsum(true_positives)

        # compute recall and precision
        recall = true_positives / num_annotations
        precision = true_positives / np.maximum(true_positives + false_positives, np.finfo(np.float64).eps)

        # compute average precision
        average_precision = _compute_ap(recall, precision)
        average_precisions[label] = average_precision, num_annotations

        # inference time
        inference_time = np.sum(all_inferences) / generator.size()

    return average_precisions, inference_time

if __name__ == '__main__':
    from ..preprocessing.pascal_voc_grid_crops import PascalVocGridCropsGenerator
    from keras_retinanet import models
    from keras_retinanet.utils.gpu import setup_gpu

    setup_gpu(0)

    # Will be equivalent to the same (resized) images
    generator = PascalVocGridCropsGenerator(
        1333, 800, 0, 0,
        0.75,
        group_by_image=True,
        shuffle_groups=False,
        data_dir="../../../data/laddv4/winter",
        set_name='test')
    model_path = '../../snapshots/resnet50_liza_alert_v1_interface.h5'
    model = models.load_model(model_path, backbone_name='resnet50')
    results_dir = '../../../data/test_detections'

    ap, inferences = evaluate(generator, model)

    # should show value close to the metric of the snapshot on usual generator
    if ap[0][0] > 0.95:
        print('[OK] Testing on usual snapshot')
    else:
        print('[FAILED] Testing on usual snapshot')
