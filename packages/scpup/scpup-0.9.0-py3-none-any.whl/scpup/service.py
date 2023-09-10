from __future__ import annotations

import pygame
import scpup
from typing import Any, final


__all__ = [
  "EauDisplayService"
]


class EauDisplayServiceMeta(type):
  _instances_: dict[Any, EauDisplayService] = {}

  def __call__(cls, *args, **kwds) -> EauDisplayService:
    if cls not in cls._instances_:
      instance = super().__call__(*args, **kwds)
      cls._instances_[cls] = instance
    return cls._instances_[cls]


@final
class EauDisplayService(metaclass=EauDisplayServiceMeta):
  __slots__ = (
    "_display",
    "view"
  )

  def __init__(self, size: tuple[int, int] | None = None) -> None:
    self._display: pygame.Surface = pygame.display.set_mode(size or (1920, 1080))

  def set_view(self, view: scpup.EauView):
    self.view.sprites.clear(self._display, self.view.background)
    self.view: scpup.EauView = view

  @property
  def size(self) -> tuple[int, int]:
    return self._display.get_size()

  def render_view_frame(self, *args, **kwargs):
    self.view.sprites.clear(self._display, self.view.background)
    self.view.sprites.update(*args, display_rect=self.size, **kwargs)
    self.view.sprites.draw(self._display)
    pygame.display.flip()
