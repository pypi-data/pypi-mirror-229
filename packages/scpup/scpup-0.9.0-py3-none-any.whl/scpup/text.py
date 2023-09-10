from __future__ import annotations
import re
import pygame
import scpup


class EauTextMeta(type):
  def init(cls, *, fontpath: str, spacing: int = 4) -> None:
    cls.font = scpup.load_font(fontpath)
    cls.spacing = spacing


class EauText(metaclass=EauTextMeta):

  __slots__ = (
    "_value_",
    "updateable",
    "updatedict",
    "updated",
    "margin",
    "fontsize",
    "color",
    "maxwidth",
    "background_color",
    "position",
    "renders",
    "bgrender",
    "showing",
    "subgroup"
  )

  def __init__(self, value: str, *,
               fontsize: int,
               position: tuple[int, int],
               margin: tuple[int, int] | None = None,
               color: pygame.Color | tuple[int, int, int] | None = None,
               background_color: pygame.Color | tuple[int, int, int] | None = None,
               maxwidth: int = 0,
               subgroup: str | None = None,
               **subs):
    if not hasattr(self.__class__, "font"):
      raise RuntimeError(f"Font needs to be initialized by calling: '{self.__class__.__name__}.init(...)'.")
    self.fontsize = fontsize
    self.position = position
    self.margin: tuple[int, int] = margin or (0, 0)
    self.showing = True
    self.subgroup = subgroup
    self.renders
    self.bgrender = None
    self.color = color if isinstance(color, pygame.Color) else \
      pygame.Color(0, 0, 0) if color is None else \
      pygame.Color(color[0], color[1], color[2])
    self.background_color = background_color if isinstance(background_color, pygame.Color) \
      else pygame.Color(0, 0, 0) if background_color is None \
      else pygame.Color(background_color[0], background_color[1], background_color[2])
    self.maxwidth = maxwidth
    self.text = value
    self.replace(update=False, **subs)

  def __eq__(self, other: object) -> bool:
    if isinstance(other, EauText):
      return self._value_ == other._value_
    elif isinstance(other, str):
      return self._value_ == other
    return False

  @property
  def size(self) -> tuple[int, int]:
    return (
      sum([render[1].height for render in self.renders]),
      sum([render[1].width for render in self.renders])
    )

  @property
  def text(self):
    return self._value_

  @text.setter
  def text(self, text):
    self._value_ = text
    self.updateable = self._value_.find("{") > -1
    if self.updateable:
        updatekeys = re.findall("{(.+?)}", self._value_)
        self.updatedict = dict.fromkeys(updatekeys, "")
    else:
        self.updatedict = {}

  def attrs(self, *, update=True, color=None, fontsize=None):
      if (color or fontsize) is None:
        return
      self.updated = False
      self.color = color or self.color
      self.fontsize = fontsize or self.fontsize
      if update:
        self.update_renders()

  def replace(self, *, update=True, **subs):
    if self.updateable and not self.updatedict.keys().isdisjoint(subs):
      for key, value in subs.items():
        if key in self.updatedict and value != self.updatedict[key]:
          self.updatedict[key] = value
          self.updated = False
      if update:
        self.update_renders()

  def update_renders(self):
    if not self.updated:
      tab_space = "   "
      if self.updateable:
        updatedictvalues = list(self.updatedict.values())
        if type(updatedictvalues[0]) in (list, tuple):
          updatedict = dict.fromkeys(self.updatedict)
          text = ""
          for idx in range(len(updatedictvalues[0])):
            for key, value in self.updatedict.items():
              updatedict.update({key: value[idx]})
            text += self._value_.format(**updatedict) + "\n"
          text = text[:-1]
        else:
          text = self._value_.format(**self.updatedict)
      else:
        text = self._value_
      self._get_render(re.sub(
        r"\[t([0-9]+)\]",
        lambda matchobj: tab_space * int(matchobj.group(1)),
        text
      ))
      self.updated = True

  def _get_render(self, text):
    if self.__class__.font is None:
      return
    rowheight = self.__class__.font.get_sized_height(self.fontsize) + self.__class__.spacing
    lines = text.splitlines()
    renders = []
    currrows = 0
    adjustment = 0
    for line in lines:
      if self.maxwidth:
        surfheight = getattr(self, "maxheight", scpup.EauDisplayService().size[1] - self.position[1])
        image = pygame.Surface((self.maxwidth, surfheight), pygame.SRCALPHA)
        image.fill(pygame.Color(0, 0, 0, 0))
        image = image.convert_alpha()
        rows = self.word_wrap(image, line, rowheight)
        adjustment = 1
      else:
        image, _ = self.__class__.font.render(
          line,
          size=self.fontsize,
          fgcolor=self.color,
          bgcolor=None if self.bgrender is not None else self.background_color
        )
        rows = 1
      align = getattr(self, "align", 'left')
      valign = getattr(self, "valign", 'top')
      offset_y = rowheight * currrows
      currrows += rows
      rect_attrs = {
        align: self.position[0],
        valign: self.position[1] + offset_y,
        "height": rowheight * rows + adjustment
      }
      rect = image.get_rect(**rect_attrs)
      renders.append((image, rect))
    self.renders = renders
    if hasattr(self, "bgrender"):
      self.render_bg()

  def word_wrap(self, surf, text, line_spacing):
    if self.__class__.font is None:
      return 0
    get_rect = self.__class__.font.get_rect
    words = text.split(' ')
    rows, x, y = 1, 0, line_spacing
    # rows, x, y = 1, 0, 0
    width, height = surf.get_size()
    spacewidth = get_rect(' ', size=self.fontsize).width
    for word in words:
      bounds = get_rect(word, size=self.fontsize)
      if bounds.width > width:
        raise ValueError("word too wide for the surface")
      if x + bounds.width > width:
        x, y = 0, y + line_spacing
        rows += 1
      if y + bounds.height > height:
        raise ValueError("text to long for the surface")
      self.__class__.font.render_to(
        surf,
        (x, y),
        None,  # type: ignore
        fgcolor=self.color,
        bgcolor=self.background_color,
        size=self.fontsize)
      x += bounds.width + spacewidth
    return rows

  def render_bg(self) -> None:
      if self.bgrender is not None or len(self.renders) == 0:
        return
      totalwidth = self.size[0] + self.margin[0] * 2
      totalheight = self.size[1] + self.margin[1] * 2
      bgimage = pygame.Surface((totalwidth, totalheight), pygame.SRCALPHA)
      bgimage.fill(self.background_color)
      bgimage = bgimage.convert_alpha()
      topleft = self.renders[0][1].topleft
      bgrect = bgimage.get_rect(
        topleft=(
          topleft[0] - self.margin[0],
          topleft[1] - (self.margin[1] + (self.__class__.spacing // 2))
        )
      )
      self.bgrender = (bgimage, bgrect)

  def is_colliding(self, position) -> bool:
    if self.bgrender is not None and self.bgrender[1].collidepoint(position):
      return True
    elif len(self.renders) > 0:
      for _, rect in self.renders:
        if rect.collidepoint(position):
          return True
    return False


class EauTextsGroup:
  __slots__ = (
    "_texts",
    "_drawn"
  )

  def __init__(self) -> None:
    self._texts: list[EauText] = []
    self._drawn = []

  def __iter__(self):
    return self._texts.__iter__()

  def __next__(self):
    return self.texts.__next__()

  def __contains__(self, text) -> bool:
    return text in [t.text for t in self._texts] if isinstance(text, str) else text in self._texts

  def draw(self, dest) -> None:
    self._drawn.clear()
    for text in self._texts:
      if text.showing:
        if text.bgrender is not None:
          dest.blit(text.bgrender[0], text.bgrender[1])
          self._drawn.append(text.bgrender[1])
        for render in text.renders:
          dest.blit(render[0], render[1])
          self._drawn.append(render[1])

  def clear(self, dest, background) -> None:
    for rect in self._drawn:
      dest.blit(background, rect, rect)
    self._drawn.clear()

  def empty(self) -> None:
    self._texts.clear()
    self._drawn.clear()

  def add(self, text) -> None:
    self._texts.append(text)

  def remove(self, text) -> None:
    if text in self._texts:
      self._texts.remove(text)

  def texts(self, subgroup=None):
    if subgroup is None:
      return self._texts
    return [
      txt for txt in self._texts if subgroup is None or str(txt.subgroup) in subgroup
    ]

  def text(self, value: str | EauText, subgroup=None) -> None | EauText:
    return next((txt for txt in self.texts(subgroup) if txt == value), None)

  def update(self, **new_data) -> None:
    for text in self._texts:
      text.replace(**new_data)

  def attrs(self, subgroup=None, *, color=None, fontsize=None):
    for text in self.texts(subgroup):
      text.attrs(color=color, fontsize=fontsize)

  def showing(self, showing, *, subgroup=None):
      for text in self._texts:
          if subgroup is None or str(text.subgroup) in subgroup:
              text.showing = showing

  def get_collition(self, position, subgroup=None) -> EauText | None:
      if len(self._texts) > 0:
          clicked_texts = [
            txt for txt in self.texts(subgroup)
            if isinstance(txt, EauText) and txt.is_colliding(position)
          ]
          return clicked_texts[0] if len(clicked_texts) > 0 else None
