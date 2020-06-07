from typing import NamedTuple, List, Optional, Dict
import numpy as np

class Rectangle(NamedTuple):
    """Хранит координаты прямоугольника (xmin, ymin) - (xmax, ymax)"""

    xmin: int
    ymin: int
    xmax: int
    ymax: int

    @property
    def w(self) -> int:
        """Ширина"""
        return self.xmax - self.xmin

    @property
    def h(self) -> int:
        """Высота"""
        return self.ymax - self.ymin

    @property
    def square(self) -> float:
        """Площадь"""
        return self.w * self.h

    def __repr__(self) -> str:
        return f'Rectangle(x1={self.xmin},y1={self.ymin},x2={self.xmax},y2={self.ymax})'

    def _eq_members(self):
        return self.xmin, self.xmax, self.xmin, self.ymin

    def __eq__(self, other):
        if type(other) is type(self):
            return self._eq_members() == other._eq_members()
        else:
            return False

    def __hash__(self):
        return hash(self._eq_members())


class Annotation(NamedTuple):
    """Аннотация к изображению - bbox + класс объекта"""
    label: str
    bbox: Rectangle


class ImageGridCropper:
    """Режет изображение на фрагменты, по сетке

    window_w и window_h - размеры итоговых изображений
    overlap_w и overlap_h - нахлест изображений при формировании сетки
    """

    def __init__(self,
                 window_w: int, window_h: int,
                 overlap_w: int, overlap_h: int,
                 min_cropped_bbox_square: float) -> None:
        self.window_w = window_w
        self.window_h = window_h
        self.overlap_w = overlap_w
        self.overlap_h = overlap_h
        self.min_cropped_bbox_square = min_cropped_bbox_square

    def get_image_grid(self, image_width: int, image_height: int) -> List[Rectangle]:
        """Рассчитывает координаты прямоугольников для разбиения изображения на блоки

        :param image_width: ширина изображения
        :param image_height: высота изображения
        """
        rectangles = []

        # комбинируем вертикальный и горизонтальные разрезы, чтобы получить прямоугольники
        for x_min in self._cut_points(image=image_width, window=self.window_w, overlap=self.overlap_w):
            for y_min in self._cut_points(image=image_height, window=self.window_h, overlap=self.overlap_h):
                rect = Rectangle(xmin=x_min, ymin=y_min, xmax=x_min + self.window_w, ymax=y_min + self.window_h)
                rectangles.append(rect)

        return rectangles

    @classmethod
    def _cut_points(cls, image: int, window: int, overlap: int) -> List[int]:
        """Точки разрезов изображения (направляющие)"""
        offset = window - overlap
        points = [v for v in range(0, image - window, offset)]

        # справа и снизу остается неполный прямоугольник
        # добавим его, отсутпив справа ширину окна и сделаем еще один разрез
        points.append(max(image - window, 0))
        return points

    # pre-calculates amount of fragments in grid, without actual cutting
    def calc_crops_count(self, image_w: int, image_h: int) -> int:
        count_w = len(self._cut_points(image_w, self.window_w, self.overlap_w))
        count_h = len(self._cut_points(image_h, self.window_h, self.overlap_h))
        return count_w * count_h

    def calc_annotations(self, source_labels, source_bboxes, crop: Rectangle) -> Dict[str, list]:
        """Вычисляет координаты аннотаций, которые попали в обрезаный фрагмент.
        """
        crop_labels = []
        crop_bboxes = []
        for label, coordinates in zip(source_labels, source_bboxes):
            source_bbox = Rectangle(*coordinates)
            new_bbox = self._crop_bbox(bbox=source_bbox, crop=crop)
            if new_bbox is None:
                continue
            if new_bbox.square / source_bbox.square >= self.min_cropped_bbox_square:
                crop_labels.append(label)
                crop_bboxes.append([new_bbox.xmin, new_bbox.ymin, new_bbox.xmax, new_bbox.ymax])

        crop_bboxes = crop_bboxes or np.empty((0, 4))

        return {'labels': np.array(crop_labels), 'bboxes': np.array(crop_bboxes)}

    @classmethod
    def _crop_bbox(cls, bbox: Rectangle, crop: Rectangle) -> Optional[Rectangle]:
        """Новый `bbox` после обрезания картинки по прямоугольнику `crop`"""
        xmin = max(bbox.xmin, crop.xmin) - crop.xmin
        ymin = max(bbox.ymin, crop.ymin) - crop.ymin
        xmax = min(bbox.xmax, crop.xmax) - crop.xmin
        ymax = min(bbox.ymax, crop.ymax) - crop.ymin

        if xmin < xmax and ymin < ymax:
            return Rectangle(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        else:
            return None


if __name__ == "__main__":
    import sys
    cropper = ImageGridCropper(800, 1333, 200, 200, 0.75)

    # Test image crops
    image_w = 4511
    image_h = 3289
    grid = cropper.get_image_grid(image_w, image_h)
    if len(grid) != cropper.calc_crops_count(image_w, image_h):
        sys.exit("[FAILED] ImageGridCropper image crops count")
    else:
        print("[OK] ImageGridCropper image crops count")

    # Test annotations
    labels = np.array(['full', 'out_of', 'cut', 'too_small_crop'])
    bboxes = np.array([[0, 0, 10, 20], [200, 200, 200, 200], [30, 30, 110, 110], [99, 0, 130, 20]])

    crop_rectangle = Rectangle(0, 0, 100, 100)
    cropped_annotations = cropper.calc_annotations(crop=crop_rectangle, source_labels=labels, source_bboxes=bboxes)
    if len(cropped_annotations['labels']) != 2:
        sys.exit("[FAILED] Wrong amount of cropped annotations")
    else:
        print("[OK] Amount of cropped annotations")

    cropped_labels = cropped_annotations['labels']
    cropped_bboxes = cropped_annotations['bboxes']
    if (cropped_labels[0] != 'full') or (Rectangle(*cropped_bboxes[0]) != Rectangle(*bboxes[0])):
        sys.exit("[FAILED] Full bbox annotation crop")
    else:
        print("[OK] Full bbox annotation crop")

    croped_bbox = Rectangle(
        bboxes[2][0],
        bboxes[2][0],
        crop_rectangle.xmax,
        crop_rectangle.ymax)
    if (cropped_labels[1] != 'cut') or (Rectangle(*cropped_bboxes[1]) != croped_bbox):
        print("[FAILED] Cut bbox annotation crop")
        print("Actual:", cropped_labels[1], cropped_bboxes[1])
        print("Expected:", 'cut', croped_bbox)
        sys.exit(1)
    else:
        print("[OK] Cut bbox annotation crop")

    # Test bounding box dimensions
    if cropped_bboxes.shape != (len(cropped_labels), 4):
        sys.exit("[FAILED] Non-empty bboxes list shape")
    else:
        print("[OK] Non-empty bboxes list shape")

    skip_labels = labels[[1, 3]]
    skip_bboxes = bboxes[[1, 3], :]
    skipped_annotations = cropper.calc_annotations(
        crop=crop_rectangle, source_labels=skip_labels, source_bboxes=skip_bboxes)
    bbox_shape = skipped_annotations['bboxes'].shape
    if (len(bbox_shape) != 2) or (bbox_shape[1] != 4):
        sys.exit("[FAILED] Empty bboxes list shape")
    else:
        print("[OK] Empty bboxes list shape")

    print("Done")
