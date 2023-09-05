from pydantic import BaseModel
from requests import Session

from cval_lib.handlers._based_on_processing import BasedOnJSON
from cval_lib.models.annotation import (
    DetectionAnnotationCOCO,
    ClassificationLabels,
    LabelsResponse,
)


class AbstractAnnotation(BasedOnJSON):
    tpe = None

    def __init__(self, dataset_id: str, part_of_dataset: str, session: Session):
        super().__init__(session)
        self.dataset_id = dataset_id
        self.part_of_dataset = part_of_dataset

    def create(self, annotation: BaseModel) -> BaseModel: ...

    def get(self) -> BaseModel: ...

    def delete(self) -> BaseModel():
        return self.__processing__(
            f'/dataset/{self.dataset_id}/{self.part_of_dataset}/annotation/{self.tpe}',
            self._delete,
            None,
            None,
        )


class Detection(AbstractAnnotation):
    tpe = 'detection'

    def create(self, annotation: DetectionAnnotationCOCO):
        return self.__processing__(
            f'/dataset/{self.dataset_id}/{self.part_of_dataset}/annotation/{self.tpe}',
            self._post,
            None,
            annotation,
        )

    def get(self) -> BaseModel:
        return self.__processing__(
            f'/dataset/{self.dataset_id}/{self.part_of_dataset}/annotation/{self.tpe}',
            self._post,
            DetectionAnnotationCOCO,
            None,
        )


class Classification(AbstractAnnotation):
    tpe = 'classification'

    def create(self, annotation: ClassificationLabels):
        return self.__processing__(
            f'/dataset/{self.dataset_id}/{self.part_of_dataset}/annotation/{self.tpe}',
            self._post,
            LabelsResponse,
            annotation,
        )

    def get(self) -> BaseModel:
        return self.__processing__(
            f'/dataset/{self.dataset_id}/{self.part_of_dataset}/annotation/{self.tpe}',
            self._post,
            LabelsResponse,
            None,
        )
