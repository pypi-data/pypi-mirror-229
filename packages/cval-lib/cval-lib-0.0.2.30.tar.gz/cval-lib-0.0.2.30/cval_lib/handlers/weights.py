from __future__ import annotations

from io import BytesIO
from typing import List

from cval_lib.handlers._abstract_handler import AbstractHandler
from cval_lib.models.weights import WeightsBase


class Weights(AbstractHandler):
    def create(self, file):
        self._post(self.url + '/weights/blob', file=file)
        return WeightsBase.parse_obj(self.send().json())

    def get_meta_all(self) -> List['WeightsBase']:
        self._get(self.url+'/weight/meta/all')
        return [WeightsBase.parse_obj(i) for i in self.send().json()]

    def get_meta(self, weights_id: str, version: str) -> 'WeightsBase':
        self._get(self.url+f'weights/{weights_id}/version/{version}/meta')
        return WeightsBase.parse_obj(self.send().json())

    def get_blob(self, weights_id: str, version: str) -> BytesIO:
        self._get(self.url+f'/weights/{weights_id}/version/{version}/meta')
        return BytesIO(self.send().data)


