from random import random
from bhv.abstract import AbstractBHV, DIMENSION
from typing import Generic, TypeVar, Type, Optional, Iterable

T = TypeVar('T')


class Embedding(Generic[T]):
    def forward(self, x: T) -> AbstractBHV:
        raise NotImplementedError()

    def back(self, x: AbstractBHV) -> Optional[T]:
        raise NotImplementedError()


class Random(Embedding[T]):
    def __init__(self, hvt: Type[AbstractBHV]):
        self.hvt = hvt
        self.hvs = {}

    def forward(self, x: T) -> AbstractBHV:
        if x in self.hvs:
            return self.hvs[x]
        else:
            hv = self.hvt.rand()
            self.hvs[x] = hv
            return hv

    def back(self, input_hv: AbstractBHV, threshold=.1) -> Optional[T]:
        best_x = None
        best_score = DIMENSION
        for x, hv in self.hvs.items():
            score = input_hv.hamming(hv)
            if score < best_score and score < threshold:
                best_score = score
                best_x = x
        return best_x


class InterpolateBetween(Embedding[float]):
    def __init__(self, hvt: Type[AbstractBHV], begin: AbstractBHV = None, end: AbstractBHV = None):
        self.hvt = hvt
        self.begin = hvt.rand() if begin is None else begin
        self.end = hvt.rand() if end is None else end

    def forward(self, x: float) -> AbstractBHV:
        return self.hvt.random(x).select(self.end, self.begin)

    def back(self, input_hv: AbstractBHV, threshold=.1) -> Optional[float]:
        beginh = self.begin.hamming(input_hv)
        endh = self.end.hamming(input_hv)
        totalh = endh + beginh
        if abs(totalh - .5) < threshold:
            return beginh/totalh


class Collapse(Embedding[Iterable[float]]):
    def __init__(self, hvt: Type[AbstractBHV]):
        self.hvt = hvt

    def forward(self, x: Iterable[float]) -> AbstractBHV:
        return self.hvt.from_bitstream(random() < v for v in x)

    def back(self, input_hv: AbstractBHV, soft=.1) -> Optional[Iterable[float]]:
        i = 1. - soft
        o = soft
        return (i if b else o for b in input_hv.bits())
