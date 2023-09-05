import os
import pygame
import pygame.mixer
import pygame.freetype

__all__ = [
  "load_image",
  "load_sound",
  "load_font"
]

BASE_PATH = os.path.join(os.getcwd(), "assets")

def load_image(*paths: str, alpha = True, **rectargs) -> tuple[pygame.Surface, pygame.Rect]:
  path = os.path.join(BASE_PATH, "images", *paths)
  if not os.path.exists(path):
    raise ValueError(f"Path: '{path}' does not exist")
  image = pygame.image.load(path)
  if alpha:
    image = image.convert_alpha()
  else:
    image = image.convert()
  rect = image.get_rect(**rectargs)
  return image, rect

def load_sound(*paths: str):
  path = os.path.join(BASE_PATH, "sounds", *paths)
  sound = pygame.mixer.Sound(path)
  return sound

def load_font(*paths: str):
  path = os.path.join(BASE_PATH, "fonts", *paths)
  font = pygame.freetype.Font(path)
  font.origin = True
  return font
