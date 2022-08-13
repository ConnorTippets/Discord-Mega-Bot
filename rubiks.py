import random

class NewList(list):
    def __init__(self, *args, **kwargs):
        self.color = kwargs.pop('color', None)
        super().__init__(*args, **kwargs)

class DottedDict(dict):
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__
  @property
  def all(self):
    return self.values()

current_side = None
colors = DottedDict(white=':white_large_square:', yellow=':yellow_square:', red=':red_square:', green=':green_square:', blue=':blue_square:', orange=':orange_square:')
sides = DottedDict(top=NewList([[':white_large_square:']*3 for _ in range(3)], color=colors.white), bottom=NewList([[':yellow_square:']*3 for _ in range(3)], color=colors.yellow), front=NewList([[':red_square:']*3 for _ in range(3)], color=colors.red), left=NewList([[':green_square:']*3 for _ in range(3)], color=colors.green), right=NewList([[':blue_square:']*3 for _ in range(3)], color=colors.blue), back=NewList([[':orange_square:']*3 for _ in range(3)], color=colors.orange))
middles = sides.top, sides.front, sides.bottom

def sides_colors():
    return [lst.color for lst in sides.values()]

def side_from_color(color):
    for side, lst in sides.items():
        if lst.color == color:
            return lst
    return None

def display_side(side, *, row=None):
  if not row:
    return '\n'.join([''.join(rower) for rower in side])
  return ''.join(side[row-1])

def display(sides):
  return f'_                   _{display_side(sides.top, row=1)}                   \n                   {display_side(sides.top, row=2)}                   \n                   {display_side(sides.top, row=3)}                \n{display_side(sides.left, row=1)}{display_side(sides.front, row=1)}{display_side(sides.right, row=1)}\n{display_side(sides.left, row=2)}{display_side(sides.front, row=2)}{display_side(sides.right, row=2)}\n{display_side(sides.left, row=3)}{display_side(sides.front, row=3)}{display_side(sides.right, row=3)}\n                   {display_side(sides.bottom, row=1)}                   \n                   {display_side(sides.bottom, row=2)}                   \n                   {display_side(sides.bottom, row=3)}                   \n                   {display_side(sides.back, row=1)}                   \n                   {display_side(sides.back, row=2)}                   \n                   {display_side(sides.back, row=3)}                   '

def scramble_side(side, sides):
  origin = sides[side][0][0]
  new_side = NewList([[], [], []], color=origin)
  colorser = [':white_large_square:', ':yellow_square:', ':red_square:', ':green_square:', ':blue_square:', ':orange_square:']
  for k in range(3):
      for v in range(3):
          color = random.choice(colorser)
          other_side = side_from_color(color)
          try:
              other_side[v][k] = origin
          except:
              side_colors = sides_colors()
              for i, l in enumerate(colors.items()):
                  short, emoji = l[0], l[1]
                  if not emoji in side_colors:
                      for lst in sides[list(sides)[i]]:
                          for ie, emojier in enumerate(lst):
                              if emojier == side_colors[i]:
                                  lst[ie] = emoji
          new_side[v].append(color)
  sides[side] = new_side

def select(side):
    current_side = side

def turn(axis, row, times):
    pass

def reset():
    sides = DottedDict(top=NewList([[':white_large_square:']*3 for _ in range(3)], color=colors.white), bottom=NewList([[':yellow_square:']*3 for _ in range(3)], color=colors.yellow), front=NewList([[':red_square:']*3 for _ in range(3)], color=colors.red), left=NewList([[':green_square:']*3 for _ in range(3)], color=colors.green), right=NewList([[':blue_square:']*3 for _ in range(3)], color=colors.blue), back=NewList([[':orange_square:']*3 for _ in range(3)], color=colors.orange))
