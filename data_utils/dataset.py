"""
Работа с датасетом Liza Alert Drone Dataset ((чтение и запись в формате Pascal VOC)

Используйте класс LaddDataset
"""
import shutil
import xml.etree.ElementTree as et
from pathlib import Path
from typing import List, Optional, NamedTuple


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

    def __repr(self) -> str:
        return f'Rectangle(x1={self.xmin},y1={self.ymin},x2={self.xmax},y2={self.ymax})'


class Annotation(NamedTuple):
    """Аннотация к изображению - bbox + класс объекта"""
    label: str
    bbox: Rectangle


class AnnotationFileReader:
    """Чтение файла с аннотациями из LADD (Pascal VOC)"""

    def __init__(self, filepath: str) -> None:
        self.filepath: Path = Path(filepath)

    def read_annotations(self) -> List[Annotation]:
        annotations = []
        root = et.parse(str(self.filepath)).getroot()
        for obj in root.iter('object'):
            bndbox = obj.find('bndbox')
            assert bndbox is not None
            annotation = Annotation(
                label=self._text(obj.find('name'), default=''),
                bbox=Rectangle(
                    xmin=int(self._text(bndbox.find('xmin'), default='0')),
                    ymin=int(self._text(bndbox.find('ymin'), default='0')),
                    xmax=int(self._text(bndbox.find('xmax'), default='0')),
                    ymax=int(self._text(bndbox.find('ymax'), default='0')),
                )
            )
            annotations.append(annotation)
        return annotations

    def _text(self, element: Optional[et.Element], default: str) -> str:
        if element is None:
            return default
        text = element.text
        if text is None:
            return default
        return text

    def __repr__(self) -> str:
        path = str(self.filepath)
        return f"AnnotationFile('{path}')"


class AnnotationFileWriter:
    """Запись аннотаций в файл"""

    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def write(self, annotations: List[Annotation]) -> None:
        content = self._gen_file_content(annotations)
        self.filepath.write_text(content)

    def _gen_file_content(self, boxes: List[Annotation]) -> str:
        boxes_content_list = [self._gen_bbox_content(box) for box in boxes]
        boxes_content_joined = ''.join(boxes_content_list)
        return (
            '<?xml version="1.0"?>\n'
            '<annotation xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
            '  <folder>Unknown</folder>\n'
            '  <filename>Unknown</filename>\n'
            '  <source>\n'
            '    <database>Unknown</database>\n'
            '  </source>\n'
            '  <size>\n'
            '    <height></height>\n'
            '    <width></width>\n'
            '    <depth></depth>\n'
            '  </size>\n'
            '  <segmented>0</segmented>\n'
            f'{boxes_content_joined}'
            '</annotation>'
        )

    def _gen_bbox_content(self, annotation: Annotation) -> str:
        return (
            '  <object>\n'
            f'    <name>{annotation.label}</name>\n'
            '    <pose>Unspecified</pose>\n'
            '    <truncated>0</truncated>\n'
            '    <difficult>0</difficult>\n'
            '    <bndbox>\n'
            f'      <ymin>{annotation.bbox.ymin}</ymin>\n'
            f'      <xmin>{annotation.bbox.xmin}</xmin>\n'
            f'      <ymax>{annotation.bbox.ymax}</ymax>\n'
            f'      <xmax>{annotation.bbox.xmax}</xmax>\n'
            '    </bndbox>\n'
            '  </object>\n'
        )


class ImageSetFileWriter:
    """Запись файлов со списком train, val, trainval, test"""

    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def write_samples(self, samples: List[str]) -> None:
        lines = [str(s) + '\n' for s in samples]
        content = ''.join(lines)
        self.filepath.write_text(content)


ImageIdType = str  # тип для id изображения в датасете


class LaddDataset:
    """Работа с датасетом LADD"""

    def __init__(self, path: str):
        self.path = Path(path)

    def ids(self) -> List[ImageIdType]:
        """Список ID изображений. По ID можно получить файл аннотаций или файл картинки"""
        return [f.stem for f in self.path.glob('Annotations/*.xml')]

    def image_filename(self, image_id: ImageIdType) -> str:
        """Файл, в котором хранится изображение"""
        return str(self.images_dir() / f'{image_id}.jpg')

    def annotations(self, image_id: ImageIdType) -> List[Annotation]:
        """Список аннотаций для изображения"""
        filename = str(self.annotations_dir() / f'{image_id}.xml')
        return AnnotationFileReader(filename).read_annotations()

    def add(self, image_id: ImageIdType, source_image_path: str, annotations: List[Annotation]) -> None:
        """Добавляет изображение в датасет

        :param image_id: id добавляемого изображения
                         если такой id существует, то данные будут заменены на новые
        :param annotations: список bbox и меток классов
        :param source_image_path: исходный файл изображения, будет скопирован в датасет
        """
        self.images_dir().mkdir(parents=True, exist_ok=True)
        self.annotations_dir().mkdir(parents=True, exist_ok=True)

        image_filename = self.image_filename(image_id)
        shutil.copyfile(src=source_image_path, dst=image_filename)

        annotations_filename = self.annotations_filename(image_id)
        writer = AnnotationFileWriter(filepath=annotations_filename)
        writer.write(annotations=annotations)

    def remove(self, image_id: ImageIdType) -> None:
        """Удаляет изображение из датасета"""
        image_filename = self.image_filename(image_id)
        Path(image_filename).unlink()

        annotations_filename = self.annotations_filename(image_id)
        Path(annotations_filename).unlink()

    def write_image_sets(self, train_set: List[ImageIdType], val_set: List[ImageIdType],
                         test_set: List[ImageIdType]) -> None:
        self.images_sets_dir().mkdir(parents=True, exist_ok=True)

        train_filename = str(self.images_sets_dir() / 'train.txt')
        ImageSetFileWriter(train_filename).write_samples(train_set)

        trainval_filename = str(self.images_sets_dir() / 'trainval.txt')
        ImageSetFileWriter(trainval_filename).write_samples(train_set + val_set)

        val_filename = str(self.images_sets_dir() / 'val.txt')
        ImageSetFileWriter(val_filename).write_samples(val_set)

        test_filename = str(self.images_sets_dir() / 'test.txt')
        ImageSetFileWriter(test_filename).write_samples(test_set)

    def images_dir(self) -> Path:
        return self.path / 'JPEGImages'

    def annotations_dir(self) -> Path:
        return self.path / 'Annotations'

    def annotations_filename(self, image_id: ImageIdType) -> str:
        return str(self.annotations_dir() / f'{image_id}.xml')

    def images_sets_dir(self) -> Path:
        return self.path / f'ImageSets/Main'

    def __repr__(self) -> str:
        path = str(self.path)
        return f"LaddDataset('{path}')"
