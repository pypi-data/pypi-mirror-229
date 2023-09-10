from __future__ import annotations
import scpup
import pygame
from abc import ABC, abstractmethod

__all__: list[str] = [
  "EauView",
]


class EauView(ABC):
  __slots__: tuple = (
    "background",
    "sprites"
  )

  def __init__(self, background_path: str) -> None:
    self.background: pygame.Surface = scpup.load_image(background_path)[0]
    self.sprites = scpup.EauGroup()
    self.sprites.add(*[scpup.EauSprite(p) for p in self.images])

  @property
  @abstractmethod
  def images(self) -> list[str]:
    ...

  @abstractmethod
  def handle(self, action: scpup.EauAction):
    ...
