"""This module contains the helper classes for game controllers.

This module has the button mapping of the following controllers:

* PS4
  * PS4 Controller
  * DualSense Wireless Controller
* PS5
  * Sony Interactive Entertainment Wireless Controller
* Xbox
  * Xbox Series X Controller
  * Xbox One Series X Controller

The exported classes of this module are:

* EauAction
* EauCtrl
* EauCtrlMapping
* EauXboxCtrlMapping
* EauPS4CtrlMapping
* EauPS5CtrlMapping
"""

from __future__ import annotations
import pygame
from enum import IntEnum, auto
from abc import abstractmethod, ABCMeta
from typing import overload, final

__all__: list[str] = [
  "EauAction",
  "EauCtrl",
  "EauCtrlMapping",
  "EauXboxCtrlMapping",
  "EauPS4CtrlMapping",
  "EauPS5CtrlMapping",
]


@final
class EauAction(IntEnum):
  """Enumeration that contains all mappeable buttons as members of the enum."""
  START = auto()
  SELECT = auto()
  GUIDE = auto()
  A = auto()
  B = auto()
  X = auto()
  Y = auto()
  LB = auto()
  RB = auto()
  LT = auto()
  RT = auto()
  LS = auto()
  RS = auto()
  L_UP = auto()
  L_RIGHT = auto()
  L_DOWN = auto()
  L_LEFT = auto()
  R_UP = auto()
  R_RIGHT = auto()
  R_DOWN = auto()
  R_LEFT = auto()
  DPAD_UP = auto()
  DPAD_RIGHT = auto()
  DPAD_DOWN = auto()
  DPAD_LEFT = auto()


class EauCtrlMappingMeta(ABCMeta):
  _instances_: dict = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances_:
      instance = super().__call__(*args, **kwargs)
      cls._instances_[cls] = instance
    return cls._instances_[cls]


class EauCtrlMapping(metaclass=EauCtrlMappingMeta):
  """A mapping between the buttons of a controller to the button id of a
  pygame.event.Event. This class implements the Singleton pattern."""
  __slots__: tuple = ()

  @staticmethod
  def get(name: str) -> EauXboxCtrlMapping | EauPS4CtrlMapping | EauPS5CtrlMapping:
    """Get the mapping instance of a certain controller given the name of that
    controller.

    Args:
      name:
        The name of the controller as described in the pygame.joystick
        documentation.

    Raises:
      ValueError:
        The name is not a valid controller name or it has not been mapped yet.

    Returns:
      The instance of the corresponding controller mapping.
    """
    if name in ["Xbox Series X Controller", "Xbox One Series X Controller"]:
      return EauXboxCtrlMapping()
    elif name in ["PS4 Controller", "DualSense Wireless Controller"]:
      return EauPS4CtrlMapping()
    elif name in ["Sony Interactive Entertainment Wireless Controller"]:
      return EauPS5CtrlMapping()
    raise ValueError(f"Controller not defined: '{name}'")

  @abstractmethod
  def __getitem__(self, key: int) -> EauAction:
    """Gets a scpup.EauAction member given a key (which would be the button id
    of a pygame.event.Event).

    Args:
      key:
        The button that is received from a pygame.event.Event instance when a
        JOYBUTTONUP or JOYBUTTONDOWN event is received.

    Returns:
      EauAction:
        The button that the received key maps to.

    Raises:
      KeyError:
        The key is a integer but does not correspond to a button
      TypeError:
        It could be that the key is not an integer or any other unexpected
        error.
    """


@final
class EauXboxCtrlMapping(EauCtrlMapping):
  __slots__: tuple = ()

  def __getitem__(self, key: int) -> EauAction:
    if key < 0 or key > 10:
      raise KeyError(f'No mapping for button {key}')
    elif key == 0:
      return EauAction.A
    elif key == 1:
      return EauAction.B
    elif key == 2:
      return EauAction.X
    elif key == 3:
      return EauAction.Y
    elif key == 4:
      return EauAction.LB
    elif key == 5:
      return EauAction.RB
    elif key == 6:
      return EauAction.SELECT
    elif key == 7:
      return EauAction.START
    elif key == 8:
      return EauAction.LS
    elif key == 9:
      return EauAction.RS
    elif key == 10:
      return EauAction.GUIDE
    raise TypeError('Unexpected Error')


@final
class EauPS4CtrlMapping(EauCtrlMapping):
  __slots__: tuple = ()

  def __getitem__(self, key: int) -> EauAction:
    if key < 0 or key > 14:
      raise KeyError(f'No mapping for button {key}')
    elif key == 0:
      return EauAction.A
    elif key == 1:
      return EauAction.B
    elif key == 2:
      return EauAction.X
    elif key == 3:
      return EauAction.Y
    elif key == 4:
      return EauAction.SELECT
    elif key == 5:
      return EauAction.GUIDE
    elif key == 6:
      return EauAction.START
    elif key == 7:
      return EauAction.LS
    elif key == 8:
      return EauAction.RS
    elif key == 9:
      return EauAction.LB
    elif key == 10:
      return EauAction.RB
    elif key == 11:
      return EauAction.DPAD_UP
    elif key == 12:
      return EauAction.DPAD_DOWN
    elif key == 13:
      return EauAction.DPAD_LEFT
    elif key == 14:
      return EauAction.DPAD_RIGHT
    raise TypeError('Unexpected Error')


@final
class EauPS5CtrlMapping(EauCtrlMapping):
  __slots__: tuple = ()

  def __getitem__(self, key: int) -> EauAction:
    if key < 0 or key > 12:
      raise KeyError(f'No mapping for button {key}')
    elif key == 0:
      return EauAction.A
    elif key == 1:
      return EauAction.B
    elif key == 2:
      return EauAction.X
    elif key == 3:
      return EauAction.Y
    elif key == 4:
      return EauAction.LB
    elif key == 5:
      return EauAction.RB
    elif key == 6:
      return EauAction.LT
    elif key == 7:
      return EauAction.RT
    elif key == 8:
      return EauAction.SELECT
    elif key == 9:
      return EauAction.START
    elif key == 10:
      return EauAction.GUIDE
    elif key == 11:
      return EauAction.LS
    elif key == 12:
      return EauAction.RS
    raise TypeError('Unexpected Error')


class EauCtrlMeta(type):
  _instances: dict[int, EauCtrl] = {}

  @overload
  def __call__(cls, iid: int) -> EauCtrl:
    """"""
  @overload
  def __call__(cls, joystick: pygame.joystick.JoystickType) -> EauCtrl:
    """"""
  def __call__(cls, val: pygame.joystick.JoystickType | int) -> EauCtrl:  # type: ignore
    if isinstance(val, int):
      return next(ctrl for iid, ctrl in cls._instances.items() if iid == val)
    iid = val.get_instance_id()
    if iid not in cls._instances:
      instance = super().__call__(val)
      cls._instances[iid] = instance
    return cls._instances[iid]


@final
class EauCtrl(metaclass=EauCtrlMeta):
  """A wrapper around a pygame.joystick object that also has its mapping.

  Attributes:
    joystick:
      The wrapped pygame.joystick object.
    mapping:
      The corresponding EauCtrlMapping object.
  """
  __slots__: tuple = (
    "joystick",
    "mapping",
  )

  def __init__(self, joystick: pygame.joystick.JoystickType) -> None:
    """Initializes a controller wrapper for a given joystick.

    Args:
      joystick:
        The pygame.joystick that will be wrapped.
    """
    self.mapping: EauXboxCtrlMapping | EauPS4CtrlMapping | EauPS5CtrlMapping = EauCtrlMapping.get(joystick.get_name())
    self.joystick: pygame.joystick.JoystickType = joystick

  @property
  def iid(self) -> int:
    """Gets the instance id of the wrapped joystick."""
    return self.joystick.get_instance_id()
