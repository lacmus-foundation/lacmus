''' 
https://github.com/lacmus-foundation/lacmus
Copyright (C) 2019-2020 lacmus-foundation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from __future__ import division
import numpy as np
import cv2

def _uniform(val_range):
    """ Uniformly sample from the given range.

    Args
        val_range: A pair of lower and upper bound.
    """
    return np.random.uniform(val_range[0], val_range[1])


def _clip(array):
    """
    Clip and convert an array of arbitrary shape to np.uint8.

    Args
        array: Array to clip.
    """
    return np.clip(array, 0, 255).astype(np.uint8)


def _check_range(val_range, min_val=None, max_val=None):
    """ Check whether the range is a valid range.

    Args
        val_range: A pair of lower and upper bound.
        min_val: Minimal value for the lower bound.
        max_val: Maximal value for the upper bound.
    """
    if val_range[0] > val_range[1]:
        raise ValueError('interval lower bound > upper bound')
    if min_val is not None and val_range[0] < min_val:
        raise ValueError('invalid interval lower bound')
    if max_val is not None and val_range[1] > max_val:
        raise ValueError('invalid interval upper bound')


class ImageAdjustment:
    """ Struct holding parameters and applying image color transformation.

    Args
        contrast_factor:   A factor for adjusting contrast. Should be between 0 and 3.
        brightness_delta:  Brightness offset between -1 and 1 added to the pixel values.
        hue_delta:         Hue offset between -1 and 1 added to the hue channel.
        saturation_factor: A factor multiplying the saturation values of each pixel.
    """

    def __init__(
        self,
        contrast_factor,
        brightness_delta,
        hue_delta,
        saturation_factor,
    ):
        self.contrast_factor = contrast_factor
        self.brightness_delta = brightness_delta
        self.hue_delta = hue_delta
        self.saturation_factor = saturation_factor

    def __call__(self, image):
        """ Apply a visual effect on the image.

        Args
            image: Image to adjust
        """

        num_channels = image.shape[-1]
        
        if self.contrast_factor or self.brightness_delta:
            
            lookup_table = self.create_lookup(num_channels)
            
            if self.contrast_factor:
                lookup_table = self.adjust_contrast_lookup(image, lookup_table)  
            if self.brightness_delta:
                lookup_table = self.adjust_brightness_lookup(lookup_table)
                
            image = cv2.LUT(image, lookup_table)

        if self.hue_delta or self.saturation_factor:

            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            lookup_table = self.create_lookup(num_channels)

            if self.hue_delta:
                lookup_table = self.adjust_hue_lookup(lookup_table)
            if self.saturation_factor:
                lookup_table = self.adjust_saturation_lookup(lookup_table)

            image = cv2.LUT(image, lookup_table)
            image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

        return image
    
    def create_lookup(self, channels):
        max_value = 255
        
        uint_range = np.arange(0, max_value + 1)
        return np.dstack(
            np.tile(uint_range, (channels, 1))
        )
    
    
    def adjust_contrast_lookup(self, image, lookup_table):
        lookup_table = lookup_table.astype('float32')
        
        mean = image.mean(axis=0).mean(axis=0)
        lookup_table -= mean
        lookup_table *= self.contrast_factor
        lookup_table += mean

        lookup_table = _clip(lookup_table)
        return lookup_table
    
    def adjust_brightness_lookup(self, lookup_table):
        lookup_table = lookup_table.astype('float32')
        
        lookup_table += self.brightness_delta * 255
        lookup_table = _clip(lookup_table)
        return lookup_table
    
    def adjust_hue_lookup(self, lookup_table):
        lookup_table = lookup_table.astype('float32')
        lookup_table[..., 0] += self.hue_delta * 180
        lookup_table[..., 0] = np.mod(lookup_table[..., 0], 180)
        lookup_table = _clip(lookup_table)
        return lookup_table

    def adjust_saturation_lookup(self, lookup_table):
        lookup_table = lookup_table.astype('float32')
        lookup_table[..., 1] *= self.saturation_factor
        lookup_table = _clip(lookup_table)
        return lookup_table
    
    
    
def random_adjustment_generator(
    contrast_range=(0.9, 1.1),
    brightness_range=(-.1, .1),
    hue_range=(-0.05, 0.05),
    saturation_range=(0.95, 1.05)
):
    """ Generate visual effect parameters uniformly sampled from the given intervals.

    Args
        contrast_factor:   A factor interval for adjusting contrast. Should be between 0 and 3.
        brightness_delta:  An interval between -1 and 1 for the amount added to the pixels.
        hue_delta:         An interval between -1 and 1 for the amount added to the hue channel.
                           The values are rotated if they exceed 180.
        saturation_factor: An interval for the factor multiplying the saturation values of each
                           pixel.
    """
    _check_range(contrast_range, 0)
    _check_range(brightness_range, -1, 1)
    _check_range(hue_range, -1, 1)
    _check_range(saturation_range, 0)

    def _generate():
        while True:
            yield ImageAdjustment(
                contrast_factor=_uniform(contrast_range),
                brightness_delta=_uniform(brightness_range),
                hue_delta=_uniform(hue_range),
                saturation_factor=_uniform(saturation_range),
            )

    return _generate()

if __name__ == "__main__":
    from keras_retinanet.utils.image import VisualEffect, random_visual_effect_generator
    
    effect_generator = random_visual_effect_generator()
    effect = next(effect_generator)
    
    # Test contrast
    contrast_effect = VisualEffect(effect.contrast_factor, None, None, None)
    image = np.random.randint(0, 255, size=(3, 3, 2), dtype=np.uint8)
    contrast_old = contrast_effect(image)
    contrast_adjustment = ImageAdjustment(effect.contrast_factor, None, None, None)
    contrast_new = contrast_adjustment(image)
    if np.array_equal(contrast_old, contrast_new):
        print("[OK] Contrast backward compatibility.")
    else:
        print("[FAILED] Contrast backward compatibility.")
        print("Old:")
        print(contrast_old)
        print("New:")
        print(contrast_new)
        
    # Test brighntness
    brighntness_effect = VisualEffect(None, effect.brightness_delta, None, None)
    image = np.random.randint(0, 255, size=(3, 3, 2), dtype=np.uint8)
    brighntness_old = brighntness_effect(image)
    brighntness_adjustment = ImageAdjustment(None, effect.brightness_delta, None, None)
    brighntness_new = brighntness_adjustment(image)
    if np.array_equal(brighntness_old, brighntness_new):
        print("[OK] Brighntness backward compatibility.")
    else:
        print("[FAILED] Brighntness backward compatibility.")
        print("Old:")
        print(brighntness_old)
        print("New:")
        print(brighntness_new)
        
    # Test hue
    hue_effect = VisualEffect(None, None, effect.hue_delta, None)
    hue_old = np.random.randint(0, 255, size=(5, 5, 3), dtype=np.uint8)
    hue_new = hue_old.copy()
    hue_effect(hue_old)
    hue_adjustment = ImageAdjustment(None, None, effect.hue_delta, None)
    hue_adjustment(hue_new)
    if np.array_equal(hue_old, hue_new):
        print("[OK] Hue backward compatibility.")
    else:
        print("[FAILED] Hue backward compatibility.")
        print("Old:")
        print(hue_old)
        print("New:")
        print(hue_new)
        
    # Test saturation
    saturation_effect = VisualEffect(None, None, None, effect.saturation_factor)
    saturation_old = np.random.randint(0, 255, size=(5, 5, 3), dtype=np.uint8)
    saturation_new = saturation_old.copy()
    saturation_effect(saturation_old)
    saturation_adjustment = ImageAdjustment(None, None, None, effect.saturation_factor)
    saturation_adjustment(saturation_new)
    if np.array_equal(saturation_old, saturation_new):
        print("[OK] Saturation backward compatibility.")
    else:
        print("[FAILED] Saturation backward compatibility.")
        print("Old:")
        print(saturation_old)
        print("New:")
        print(saturation_new)
        
    # Test all in one 
    adjustment = ImageAdjustment(
        effect.contrast_factor,
        effect.brightness_delta,
        effect.hue_delta,
        effect.saturation_factor)
    image_old = np.random.randint(0, 255, size=(7, 7, 3), dtype=np.uint8)
    image_new = image_old.copy()
    image_old = effect(image_old)
    image_new = adjustment(image_new)
    if np.array_equal(image_old, image_new):
        print("[OK] All effects at once.")
    else:
        print("[FAILED] All effects at once.")
        print("Old:")
        print(image_old)
        print("New:")
        print(image_new)
        
    # Time tests
    print("\nTime tests:")
    import time
    
    effect = next(effect_generator)
    
    
    image = np.random.randint(0, 255, size=(800, 1333, 3), dtype=np.uint8) 
    
    def compare_versions(effect, image, characteristic):
        adjustment = ImageAdjustment(
            effect.contrast_factor,
            effect.brightness_delta,
            effect.hue_delta,
            effect.saturation_factor)
        
        start = time.process_time()
        image = effect(image)    
        old_time = time.process_time() - start
    
        start = time.process_time()
        image = adjustment(image)
        new_time = time.process_time() - start
        
        print(characteristic + ": old time - {0:.4f}s, new time - {1:.4f}s".format(old_time, new_time))
    
    # Contrast
    contrast_effect = VisualEffect(effect.contrast_factor, None, None, None)
    compare_versions(contrast_effect, image, "Contrast")
    
    # Brightness
    brighntness_effect = VisualEffect(None, effect.brightness_delta, None, None)
    compare_versions(brighntness_effect, image, "Brightness")
    
    # Hue
    hue_effect = VisualEffect(None, None, effect.hue_delta, None)
    compare_versions(hue_effect, image, "Hue")
    
    # Saturation
    saturation_effect = VisualEffect(None, None, None, effect.saturation_factor)
    compare_versions(saturation_effect, image, "Saturation")

    # All effects   
    compare_versions(effect, image, "All effects")