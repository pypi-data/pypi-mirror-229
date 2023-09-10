"""This module contains base sprite classes used in SCPUP.

The exported classes of this module are:

* EauAnimatedSprite
* EauMaskedSprite
* EauSecuence
* EauSecuenceStep
* EauSprite
"""

from __future__ import annotations
from typing import overload
import scpup
import pygame

__all__: list[str] = [
  "EauAnimatedSprite",
  "EauMaskedSprite",
  "EauSecuence",
  "EauSecuenceStep",
  "EauSprite",
]


class EauSprite:
  """A static and basic sprite.

  This sprite class can be used for any static sprite, as it does not implement
  any complex logic and it is the base clase for all the other sprite classes.
  This class is basically a copy of the pygame.sprite.Sprite class just with
  __slots__ added for optimization.

  Attributes:
    image:
      The pygame.Surface image that will be rendered.
    rect:
      The pygame.Rect around the image.
    __g:
      A private dict used to store the groups that this sprite belongs to.
  """
  __slots__: tuple = (
    "__g",
    "image",
    "rect"
  )

  @classmethod
  def using(cls, surface: pygame.Surface, **rectargs) -> EauSprite:
    """Creates a sprite from a given surface and sets its position.

    Args:
      surface:
        The surface that will be used as the sprite's image.

    Returns:
      EauSprite:
        The new sprite
    """
    instance = cls()
    instance.image = surface
    instance.rect = surface.get_rect(**rectargs)
    return instance

  def __init__(self, *paths: str, **rectargs):
    """Initializes a sprite with an image and the position.

    Args:
      *paths:
        Path segmente of where the image is stored. It should exists under
        `<root>/assets/images`.
      **rectargs:
        Any arguments that are going to be passed to the `image.get_rect()`
        method. This is used for positioning the sprite.
    """
    self.__g = {}
    if len(paths) > 0:
      self.image, self.rect = scpup.load_image(*paths, **rectargs)

  @property
  def position(self) -> tuple[int, int]:
    """Get the topleft attribute of this sprite's rect.

    Returns:
      tuple[int, int]:
        The topleft coordinates. Index 0 is the left (or x) coordinate and index
        1 is the top (or y) coordinate.
    """
    return self.rect.topleft

  @position.setter
  def position(self, value: tuple[int, int]) -> None:
    """Sets the topleft attribute of this sprite's rect.

    Args:
      value:
        The topleft value to be assigned where the index 0 is the left (or x)
        coordinate and the index 1 is the top (or y) coordinate.
    """
    self.rect.topleft = value

  @property
  def center(self) -> tuple[int, int]:
    """Get the center attribute of this sprite's rect.

    Returns:
      tuple[int, int]:
        The center coordinates. Index 0 is the center x coordinate and index
        1 is the center y coordinate.
    """
    return self.rect.center

  @center.setter
  def center(self, value: tuple[int, int]) -> None:
    """Sets the center attribute of this sprite's rect.

    Args:
      value:
        The center value to be assigned where the index 0 is the center x
        coordinate and the index 1 is the center y coordinate.
    """
    self.rect.center = value

  def add(self, *groups) -> None:
    """Add this sprite to groups.

    Args:
      *groups:
        The groups to be added to. These can be either pygame.srite.Group or
        scpup.EauGroup.
    """
    for g in groups:
      if hasattr(g, "_spritegroup") and g not in self.__g:
        g.add_internal(self)
        self.add_internal(g)

  def remove(self, *groups) -> None:
    """Remove this sprite from groups.

    Args:
      *groups:
        The groups to be removed from. These can be either pygame.srite.Group or
        scpup.EauGroup.
    """
    for g in groups:
      if g in self.__g:
        g.remove_internal(self)
        self.remove_internal(g)

  def add_internal(self, group) -> None:
    """Private method used to register a group that this sprite belongs to.

    Args:
      group:
        The group to register.
    """
    self.__g[group] = 0

  def remove_internal(self, group) -> None:
    """Private method used to remove a registered group.

    Args:
      group:
        The group to remove.
    """
    del self.__g[group]

  def update(self, *_, **__) -> None:
    """Update method placeholder so that all subclasses have it."""
    pass

  def kill(self) -> None:
    """Removes this sprite from all the groups that it belongs to."""
    for g in self.__g:
      g.remove_internal(self)
    self.__g.clear()

  def groups(self) -> list:
    """List all groups that this sprite belongs to."""
    return list(self.__g)

  def alive(self) -> bool:
    """Whether this sprite belongs to any group or not."""
    return bool(self.__g)


class EauMaskedSprite(EauSprite):
  """A Sprite with a 2D bitmask for perfect colition detection.

  This is a subclass of the EauSprite class which has a mask of bits so that it
  can detect colitions perfectly.

  Attributes:
    mask:
      A pygame.mask created from this sprite's image.
  """
  __slots__: tuple = (
    "mask",
  )

  @classmethod
  def using(cls, surface: pygame.Surface, **rectargs) -> EauMaskedSprite:
    instance: EauMaskedSprite = EauMaskedSprite.using(surface, **rectargs)
    instance.mask = pygame.mask.from_surface(surface)
    return instance

  def __init__(self, *paths: str, **rectargs):
    super().__init__(*paths, **rectargs)
    if self.image:
      self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)


class EauSecuence:
  """A sprite's animation secuence.

  Attributes:
    name:
      A string that labels this secuence. It must match the key in the host's
      images dict where the images of this secuence live.
    steps:
      A list of the steps of this secuence.
    frame_count:
      The counter storing information about the current frame.
    step_count:
      The counter storing information about the current step.
  """
  __slots__: tuple = (
    "name",
    "steps",
    "frame_count",
    "step_count"
  )

  def __init__(self, name: str, *steps: EauSecuenceStep | tuple[int, int]):
    """Initializes a secuence given a name and the corresponding steps.

    Args:
      name:
        The name of this secuence.
      *steps:
        The steps of this secuence. This can be either a EauSecuenceStep object
        or a tuple of 2 ints, where the first is the indeof the image and the
        second the number of frames.
    """
    self.name: str = name
    self.steps = tuple(EauSecuenceStep(s[0], s[1]) if isinstance(s, tuple) else s for s in steps)
    self.frame_count: int = 0
    self.step_count: int = 0

  def __iter__(self) -> "EauSecuence":
    """Return itself because this class is basically an Iterable/Iterator."""
    return self

  def __next__(self) -> "EauSecuenceStep":
    """Retrieves the next step of the animation secuence.

    When you call the next() on this object and it raises a StopIteration, the
    object restarts itself so that you can call next() again without raising an
    exception.

    Raises:
      StopIteration:
        The secuence has finished iterating over its steps.

    Returns:
      EauSecuenceStep:
        The current step of the animation secuence.
    """
    if self.frame_count == self.steps[self.step_count].frames:
      self.frame_count = 0
      self.step_count += 1
    self.frame_count = self.frame_count + 1
    if self.step_count >= len(self.steps):
      self.frame_count = 0
      self.step_count = 0
      raise StopIteration
    return self.steps[self.step_count]

  def add_step(self, idx: int, frames: int) -> None:
    """Add a step to this secuence.

    Args:
      idx:
        The index of the image of this step.
      frames:
        The amount of frames of this step.
    """
    self.steps = self.steps + (EauSecuenceStep(idx, frames),)


class EauSecuenceStep:
  """A step or frame of an animation secuence.

  Attributes:
    idx:
      The index of the image on the host images attribute.
    frames:
      An integer representing the number of frames that this step will live for.
  """
  __slots__: tuple = (
    "idx",
    "frames"
  )

  def __init__(self, idx: int, frames: int):
    self.idx: int = idx
    self.frames: int = frames


class EauAnimatedSprite(EauSprite):
  """An animated sprite.

  This is a subclass of the EauSprite which stores the information and images
  needed to create an animation.

  Attributes:
    images:
      A dict where each key is the name of an animation and each value is a
      list of the images of that animation.
    default:
      A pygame.Surface holding the default image. The default image is the
      image rendered when no animation is active.
    secuences:
      A list of EauSecuence objects.
    current_secuence:
      The current secuence of an active animation or None if no animation is
      active.
  """
  __slots__: tuple = (
    "images",
    "default",
    "secuences",
    "current_secuence"
  )

  def __init__(self, *defaultpath: str, **rectargs):
    """Initializes the sprite loading its default image and initial position.

    Args:
      *defaultpath:
        Path segments of where the default image of this sprite exists.
      **rectargs:
        Arguments to pass to the get_rect() method of the default image (to set
        its initial position).
    """
    super().__init__(*defaultpath, **rectargs)
    self.default: pygame.Surface = self.image
    self.images: dict[str, list[pygame.Surface]] = {}
    self.secuences: list[EauSecuence] = []
    self.current_secuence: EauSecuence | None = None

  def add_image(self, name: str, *path: str) -> None:
    """Adds an image to an animation of this sprite.

    Args:
      name:
        The name of the animation that this image belongs to.
      *path:
        Path segments of where the image exists. It should be a file in
        `<root>/assets/images/`.
    """
    img: pygame.Surface = scpup.load_image(*path)[0]
    if name in self.images:
      self.images[name].append(img)
    else:
      self.images[name] = [img]

  @overload
  def set_secuence(self, name: str, *steps: EauSecuenceStep | tuple[int, int]) -> None:
    """Sets an animation secuence.

    Args:
      name:
        The name of the secuence. This has to match the key in this sprite's
        images from when the animation secuence will be taking its images.
      *steps:
        The steps of the secuence or a tuple where the index 0 is the idx of
        the image and the index 1 is the number of frames of that step.
    """
  @overload
  def set_secuence(self, secuence: EauSecuence) -> None:
    """Sets an animation secuence.

    Args:
      secuence:
        The secuence to set.
    """
  def set_secuence(self,  # type: ignore
                   name_or_secuence: str | EauSecuence,
                   *steps: EauSecuenceStep | tuple[int, int]) -> None:
    if isinstance(name_or_secuence, EauSecuence):
      self.secuences.append(name_or_secuence)
    else:
      self.secuences.append(EauSecuence(name_or_secuence, *steps))

  def reset(self) -> None:
    """Reset the sprite to its default state"""
    self.image = self.default
    # Not sure if I have to do self.rect = self.image.get_rect(**rectargs)
    self.current_secuence = None

  def update(self, *args, **kwargs) -> None:
    """Updates the sprite image based on the current secuence.

    Args:
      *args:
        Positional arguments to pass to the super().update() call.
      *kwargs:
        Keyword arguments to pass to the super().update() call.
    """
    super().update(*args, **kwargs)
    if self.current_secuence is not None:
      try:
        step: EauSecuenceStep = next(self.current_secuence)
        self.image = self.images[self.current_secuence.name][step.idx]
      except StopIteration:
        self.reset()

  def trigger(self, name: str) -> None:
    """Start an animation secuence.

    Args:
      name:
        The name of the secuence.
    """
    for s in self.secuences:
      if s.name == name:
        self.current_secuence = s
        break
