import pygame
import scpup
from abc import ABCMeta
from typing import final


__all__ = [
  "DisplayService"
]


class EauServiceMeta(ABCMeta):
  _instances_ = {}

  def __call__(cls, *args, **kwds):
    if cls not in cls._instances_:
      instance = super().__call__(*args, **kwds)
      cls._instances_[cls] = instance
    return cls._instances_[cls]


class EauService(metaclass=EauServiceMeta):
  __slots__ = ()


@final
class DisplayService(EauService):
  __slots__ = (
    "_display",
    "view"
  )

  def __init__(self) -> None:
    self._display = pygame.display.set_mode((1920, 1080), pygame.NOFRAME | pygame.FULLSCREEN)

  def set_view(self, view: scpup.EauView):
    self.clear()
    self.view: scpup.EauView = view

  @property
  def size(self):
    return self._display.get_size()
  
  def draw(self):
    self.view.sprites.draw(self._display)
    pygame.display.flip()

  def clear(self):
    self.view.sprites.clear(self._display, self.view.background)

  def update(self, *args, **kwargs):
    self.view.sprites.update(*args, display_rect=self.size, **kwargs)
