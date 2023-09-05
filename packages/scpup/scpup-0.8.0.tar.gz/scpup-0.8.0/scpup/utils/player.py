from __future__ import annotations
import scpup
from typing import final, overload
from typing import Literal

__all__ = [
  "PlayerIdType",
  "EauPlayer"
]

PlayerIdType = Literal["p1", "p2", "p3", "p4"]

class PlayerMeta(type):
  _instances: dict[str, EauPlayer] = {}

  @overload
  def __call__(cls) -> list[EauPlayer]: ...
  @overload
  def __call__(cls, iid: int) -> EauPlayer | None: ...
  @overload
  def __call__(cls, pid: str) -> EauPlayer: ...
  def __call__(cls, pid_iid: int|str|None) -> list[EauPlayer] | EauPlayer | None: # type: ignore
    if pid_iid is None:
      return list(cls._instances.values())
    elif isinstance(pid_iid, int):
      return next((p for p in cls._instances.values() if p.iid == pid_iid), None)
    else:
      if pid_iid not in cls._instances:
        instance = super().__call__(pid_iid)
        cls._instances[pid_iid] = instance
      return cls._instances[pid_iid]
  
  def __len__(cls):
    return len(cls._instances)
  
  def __next__(cls):
    if len(cls._instances) < 4:
      return super().__call__(f"p{len(cls._instances) + 1}")
    raise StopIteration
  
  def remove(cls, player: EauPlayer):
    if player in cls._instances.values():
      player.unassign_ctrl()
      cls._instances.pop(player.pid)
      players = list(cls._instances.values())
      cls._instances = {}
      for i in range(len(players)):
        players[i].pid = f"p{i + 1}"
        cls._instances[players[i].pid] = players[i]


@final
class EauPlayer(metaclass=PlayerMeta):
  __slots__ = (
    "pid",
    "iid",
    "sprites"
  )

  def __init__(self, player_id: PlayerIdType) -> None:
    super().__init__()
    self.pid = player_id
    self.iid: int | None = None
    self.sprites = scpup.EauNamedGroup()

  @property
  def ctrl(self):
    return None if self.iid is None else scpup.EauCtrl(self.iid)

  def assign_ctrl(self, ctrl: scpup.EauCtrl):
    self.iid = ctrl.iid

  def unassign_ctrl(self):
    self.iid = None

