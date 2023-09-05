from __future__ import annotations
from typing import Any, Iterator, overload
import pygame
import scpup

__all__ = [
  "EauGroup",
  "EauNamedGroup"
]


class EauGroup:
  _spritegroup = True

  __slots__ = (
    "__s",
    "_lostsprites"
  )

  def __init__(self, *sprites: scpup.EauSprite) -> None:
    self.__s:dict[scpup.EauSprite, Any] = {}
    self._lostsprites = []
    self.add(*sprites)

  def __bool__(self) -> bool:
      return len(self) > 0

  def __len__(self) -> int:
      return len(self.__s)

  def __iter__(self) -> Iterator:
      return iter(self.sprites())

  def __contains__(self, sprite: scpup.EauSprite) -> bool:
      return sprite in self.__s

  def add_internal(self, sprite: scpup.EauSprite) -> None:
    self.__s[sprite] = 0

  def remove_internal(self, sprite: scpup.EauSprite) -> None:
    lost_rect = self.__s[sprite]
    if lost_rect:
      self._lostsprites.append(lost_rect)
    del self.__s[sprite]
  
  def sprites(self) -> list[scpup.EauSprite]:
    return list(self.__s)

  def add(self, *sprites: scpup.EauSprite) -> None:
    for sprite in sprites:
      if not sprite in self.__s:
        self.add_internal(sprite)
        sprite.add_internal(self)

  def remove(self, *sprites: scpup.EauSprite) -> None:
    for sprite in sprites:
      if sprite in self.__s:
        self.remove_internal(sprite)
        sprite.remove_internal(self)

  def update(self, *args, **kwargs) -> None:
    for sprite in self.sprites():
      sprite.update(*args, **kwargs)

  def draw(self, surface: pygame.Surface) -> None:
    sprites: list[scpup.EauSprite] = self.sprites()
    self.draw_internal(surface, sprites)

  def draw_internal(self, surface: pygame.Surface, sprites: list[scpup.EauSprite]):
    if hasattr(surface, "blits"):
      self.__s.update(
        zip(
          sprites,
          surface.blits(
            (spr.image, spr.rect, None) for spr in sprites
          ) # type: ignore
        )
      )
    else:
      for spr in sprites:
        self.__s[spr] = surface.blit(spr.image, spr.rect, None)
    self._lostsprites = []

  def clear(self, surface: pygame.Surface, bg: pygame.Surface) -> None:
    for lost_clear_rect in self._lostsprites:
      surface.blit(bg, lost_clear_rect, lost_clear_rect)
    for clear_rect in self.__s.values():
      if clear_rect:
        surface.blit(bg, clear_rect, clear_rect)

  def empty(self) -> None:
    self.remove(*self.sprites())
    # for sprite in self.__s:
    #   self.remove_internal(sprite)
    #   sprite.remove_internal(self)


class EauNamedGroup(EauGroup):
  __slots__ = (
    "__n",
  )

  @overload
  def __init__(self) -> None: ...
  @overload
  def __init__(self, *sprites: scpup.EauSprite, name: str) -> None: ...
  def __init__(self, *sprites: scpup.EauSprite, name: str | None = None) -> None:
    super().__init__(*sprites)
    if name is not None:
      self.__n: dict[str, list[scpup.EauSprite]] = {
        name: list(sprites)
      }

  def group(self, name: str) -> list[scpup.EauSprite]:
    if name in self.__n:
      return self.__n[name]
    raise KeyError(f"No group called: '{name}'")

  def add(self, *sprites: scpup.EauSprite, name: str) -> None:
    super().add(*sprites)
    self.__n[name] = (self.__n[name] if name in self.__n else []) + list(sprites)

  def remove(self, *sprites: scpup.EauSprite) -> None:
    super().remove(*sprites)
    for sprite in sprites:
      for s_list in self.__n.values():
        if sprite in s_list:
          del s_list[s_list.index(sprite)]
          break

  def empty(self, name: str | None = None) -> None:
    self.remove(*self.sprites(name))
    if name is None:
      self.__n.clear()
    else:
      self.__n[name] = []

  def sprites(self, name: str | None = None) -> list[scpup.EauSprite]:
    return super().sprites() if name is None else self.__n[name] if name in self.__n else []
  
  def update(self, *args, name: str | None = None, **kwargs) -> None:
    for sprite in self.sprites(name):
      sprite.update(*args, **kwargs)

  def draw(self, surface: pygame.Surface, *, name: str | None = None) -> None:
    sprites: list[scpup.EauSprite] = self.sprites(name)
    self.draw_internal(surface, sprites)



# TODO: Fix this class...
# class EauAnimationGroup(EauNamedGroup):
#   __slots__ = (
#     "action"
#   )

#   def __init__(self) -> None:
#     super().__init__()
#     self.action = None

#   def set_current(self, sprite):
#     EauGroup.empty(self)
#     EauGroup.add(self, sprite)

#   def do(self, action: scpup.utils.Actions):
#     if action in self.__n:
#       self.set_current(self.__n[action][0])
