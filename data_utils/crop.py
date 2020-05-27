"""
Генератор датасета на основе разрезания изображений из другого датасета LADD

Используйте DatasetGridCropper
Или запустите файл как скрипт (python data_utils/crop.py -h)
"""

import random
import tempfile
from typing import Optional, List, Callable

import click
import cv2
import tqdm
from joblib import Parallel, delayed

from dataset import Annotation, Rectangle, LaddDataset, ImageIdType


class GridFragment:
    """Вырезанный фрагмент исходного изображения

    Когда изображение разбивается на части, формируется большое количество его фрагментов.
    Большинство из этих фрагментов не будут включать людей и поэтому в датасет добавлены не будут.
    Вместо записи их на диск будем хранить путь к исходному изображению и координаты выреза, который нужно сделать.
    В дальнейшем сможем сохранить фрагмент в файл.

    Кода изображение разбивается на части, некоторые из аннтоаций могут обрезанными.
    Оставшийся кусок аннотации может быть достаточно большим, и его можно использовать в обучении,
    но может оказаться и достаточно маленьким. Будем сравнивать площадь аннотации из исходной картинки
    и площадь получившейся аннотации. Если отношение площадей > `min_cropped_bbox_square`,
    то будем считать такую аннотацию большой, иначе маленькой.
    Можно получить отдельно списки `big_annotations()` и `small_annotations()`
    """

    def __init__(self,
                 image_path: str,
                 annotations: List[Annotation],
                 crop: Rectangle,
                 min_cropped_bbox_square: float = 0.75) -> None:
        """
        :param image_path: путь к исходному изображению
        :param annotations: список аннотаций исходного изображения
        :param crop: координаты фрагмента
        :param min_cropped_bbox_square: минимальная площадь bbox, чтобы он определялся как изображение с человеком
        """
        self.source_image_path = image_path
        self.source_annotations = annotations
        self.crop_rectangle = crop
        self.min_cropped_bbox_square = min_cropped_bbox_square
        self._big_annotations = None
        self._small_annotations = None

    def save_file(self, filepath: str) -> None:
        """Сохраняет вырезанный фрагмент в файл"""
        img = cv2.imread(self.source_image_path)
        r = self.crop_rectangle
        crop_img = img[r.ymin:r.ymax, r.xmin:r.xmax]
        cv2.imwrite(filepath, crop_img)

    def _calc_annotations(self) -> None:
        """Вычисляет координаты аннотаций, которые попали в обрезаный фрагмент.

        Разбивает аннотации на большие и маленькие в соответствии с `min_cropped_bbox_square`
        """
        if self._big_annotations is not None and self._small_annotations is not None:
            return
        big_annotations = []
        small_annotations = []
        for annot in self.source_annotations:
            new_bbox = self._crop_bbox(bbox=annot.bbox, crop=self.crop_rectangle)
            if new_bbox is None:
                continue
            new_annotation = Annotation(label=annot.label, bbox=new_bbox)
            if new_bbox.square / annot.bbox.square >= self.min_cropped_bbox_square:
                big_annotations.append(new_annotation)
            else:
                small_annotations.append(new_annotation)
        self._big_annotations = big_annotations
        self._small_annotations = small_annotations

    def big_annotations(self) -> List[Annotation]:
        self._calc_annotations()
        assert self._big_annotations is not None
        return self._big_annotations

    def small_annotations(self) -> List[Annotation]:
        # noinspection Mypy
        self._calc_annotations()
        assert self._small_annotations is not None
        return self._small_annotations

    def annotations(self) -> List[Annotation]:
        return self.big_annotations() + self.big_annotations()

    @classmethod
    def _crop_bbox(cls, bbox: Rectangle, crop: Rectangle) -> Optional[Rectangle]:
        """Новый `bbox` после обрезания картинки по прямоугольнику `crop`"""
        xmin = max(bbox.xmin, crop.xmin) - crop.xmin + 1
        ymin = max(bbox.ymin, crop.ymin) - crop.ymin + 1
        xmax = min(bbox.xmax, crop.xmax) - crop.xmin
        ymax = min(bbox.ymax, crop.ymax) - crop.ymin

        if xmin < xmax and ymin < ymax:
            return Rectangle(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        else:
            return None


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

    def crop_image(self, image_path: str, annotations: List[Annotation]) -> List[GridFragment]:
        """Разбивает изображений из файла на фрагменты"""
        img = cv2.imread(image_path)
        image_h, image_w, _channels = img.shape
        rects = self._image_grid(
            image_w=image_w, image_h=image_h,
            window_w=self.window_w, window_h=self.window_h,
            overlap_w=self.overlap_w, overlap_h=self.overlap_h,
        )
        return [GridFragment(image_path=image_path, annotations=annotations, crop=r,
                             min_cropped_bbox_square=self.min_cropped_bbox_square) for r in rects]

    @classmethod
    def _image_grid(cls,
                    image_w: int, image_h: int,
                    window_w: int, window_h: int,
                    overlap_w: int, overlap_h: int) -> List[Rectangle]:
        """Рассчитывает координаты прямоугольников для разбиения изображения на блоки

        :param image_w: ширина изображения
        :param image_h: высота изображения
        :param window_w: ширина прямоугольника
        :param window_h: высота прямоугольника
        :param overlap_w: перекрытие прямоугольников по горизонтали
        :param overlap_h: перекрытие прямоугольников по вертикали
        """
        rectangles = []

        # комбинируем вертикальный и горизонтальные разрезы, чтобы получить прямоугольники
        for xmin in cls._cut_points(image=image_w, window=window_w, overlap=overlap_w):
            for ymin in cls._cut_points(image=image_h, window=window_h, overlap=overlap_h):
                rect = Rectangle(xmin=xmin, ymin=ymin, xmax=xmin + window_w, ymax=ymin + window_h)
                rectangles.append(rect)

        # избавляемся от повторов
        return list(set(rectangles))

    @classmethod
    def _cut_points(cls, image: int, window: int, overlap: int) -> List[int]:
        """Точки разрезов изображения (направляющие)"""
        points = []
        offset = window - overlap
        for v in range(0, image - window, offset):
            points.append(v)
        # справа и снизу остается неполный прямоугольник
        # добавим его, отсутпив справа ширину окна и сделаем еще один разрез
        points.append(image - window)
        return points


class DatasetGridCropper:
    """Формирование нового датасета, разрезая изображения из старого"""

    # noinspection Mypy
    def __init__(self,
                 source_dataset: LaddDataset,
                 target_dataset: LaddDataset,
                 image_cropper: ImageGridCropper,
                 iter_callback: Callable = None):
        self.source_dataset = source_dataset
        self.target_dataset = target_dataset
        self.image_cropper = image_cropper
        self.iter_callback = iter_callback or (lambda x: x)
        self.executor = Parallel(n_jobs=-1, prefer='threads')

    def generate_dataset(self) -> None:
        print('Reading source dataset...')
        ids = list(self.source_dataset.ids())

        print('Generate fragments...')
        fragments = self._generate_fragments_parallel(ids)

        print('Filter fragments...')
        fragments = self._filter_fragments(fragments)

        print('Saving fragments...')
        ids = self._write_fragments(fragments)

        print('Saving image sets...')
        self._write_image_sets(ids)

    def _generate_fragments_parallel(self, ids: List[ImageIdType]) -> List[GridFragment]:
        """Генерируем фрагменты из картинок с номерами ids из старого датасета"""

        def f(image_id: str) -> List[GridFragment]:
            image_filename = self.source_dataset.image_filename(image_id)
            image_annotations = self.source_dataset.annotations(image_id)
            fs = self.image_cropper.crop_image(image_path=image_filename, annotations=image_annotations)
            return list(fs)

        return sum(self.executor(delayed(f)(image_id)
                                 for image_id in self.iter_callback(ids)), [])

    def _filter_fragments(self, fragments: List[GridFragment]) -> List[GridFragment]:
        """Отбираем фрагменты для датасета

        Возьмем все фрагменты с людьми и затем отберем такое же количество фрагментов без людей
        """
        with_human = [f for f in fragments if f.big_annotations()]
        without_human = [f for f in fragments if not f.big_annotations() and not f.small_annotations()]
        without_human = random.choices(without_human, k=len(with_human))
        return with_human + without_human

    def _write_fragments(self, fragments: List[GridFragment]) -> List[ImageIdType]:
        def save_one_fragment(index: int, frag: GridFragment) -> None:
            with tempfile.NamedTemporaryFile(suffix='.jpg') as t:
                filename = t.name
                frag.save_file(filename)
                image_id = str(index)
                self.target_dataset.add(image_id=image_id, source_image_path=filename, annotations=frag.annotations())

        image_ids = [str(i) for i in range(len(fragments))]
        self.executor(delayed(save_one_fragment)(index, f)
                      for index, f in self.iter_callback(list(zip(image_ids, fragments))))

        return image_ids

    def _write_image_sets(self, ids: List[ImageIdType]) -> None:
        train_count = int(len(ids) * 0.8)
        random.shuffle(ids)
        train_set = ids[:train_count]
        val_set = ids[train_count:]
        test_set = val_set
        self.target_dataset.write_image_sets(train_set=train_set, val_set=val_set, test_set=test_set)


@click.command()
@click.option('--source-path', required=True, type=click.Path(exists=True),
              help='Путь к исходному датасету в формате Pascal VOC')
@click.option('--target-path', required=True, type=click.Path(),
              help='Путь, по которому будет сформирован новый датасет')
@click.option('--image-width', type=int, help='Ширина итоговых изображений (default 250)', default=250)
@click.option('--image-height', type=int, help='Высота итоговых изображений (default 250)', default=250)
@click.option('--overlap-width', type=int, help='Перехлест по горизонтали (default 125)', default=125)
@click.option('--overlap-height', type=int, help='Перехлест по вертикали (default 125)', default=125)
@click.option('--min-cropped-bbox-square', type=float, help='Минимальная площадь нового bbox по отношению к исходному (default 0.8)', default=0.8)
def run_crop(source_path: click.Path,
             target_path: click.Path,
             image_width: int,
             image_height: int,
             overlap_width: int,
             overlap_height: int,
             min_cropped_bbox_square: int) -> None:
    """Разрезание изображений из датасета и формирование нового датасета (формат Pascal VOC)"""
    cropper = DatasetGridCropper(
        source_dataset=LaddDataset(path=str(source_path)),
        target_dataset=LaddDataset(path=str(target_path)),
        image_cropper=ImageGridCropper(
            window_w=image_width,
            window_h=image_height,
            overlap_w=overlap_width,
            overlap_h=overlap_height,
            min_cropped_bbox_square=min_cropped_bbox_square
        ),
        iter_callback=tqdm.tqdm
    )
    cropper.generate_dataset()


if __name__ == '__main__':
    run_crop()
