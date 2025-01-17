# pyright: reportMissingImports=false

import sys
import ast
from os.path import join, basename, splitext
from typing import Final, TypedDict
from collections.abc import Callable
import fontforge
import psMat
import util
import properties as P

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

GLYPHS_PATH = sys.argv[1]
BUILD_FILE = sys.argv[2]

#  {
#      path: string
#          Path to the ttf/otf files.
#      ranges: list<(int, int)>
#          Locations in nerd font.
#      remaps: list<(int, int)>
#          Locations of source font.
#          If glyph is not found in some codepoint and len(ranges[i]) > len(remaps[i]), it will be skipped.
#          This list length must be same as `ranges`, so if you want to use same codepoint as `ranges` you should specify `None`.
#      scale: (float, float)
#          Scale to (x, y) before merging.
#      translate: (int, int)
#          Translate to (x, y) before merging.
#      modify: string
#          The script of glyph transforming
#  }
class SourceInfoRequiredKeys(TypedDict):
    path: str
    ranges: list[tuple[int, ...]]
    remaps: list[tuple[int, ...] | None]
    scale: tuple[float, float]
    translate: tuple[int, int]


class SourceInfoOptionalKeys(TypedDict, total=False):
    modify: str


class SourceInfo(SourceInfoRequiredKeys, SourceInfoOptionalKeys):
    pass


SOURCES_INFO: Final[list[SourceInfo]] = [
    {   # Seti-UI + Custom
        "path": join(GLYPHS_PATH, "original-source.otf"),
        "ranges": [(0xe5fa, 0xe6ad)],
        "remaps": [(0xe4fa, 0xe5ad)],
        "scale": (0.83, 0.83),
        "translate": (-310, -140)
    },
    {   # Devicons (https://vorillaz.github.io/devicons/)
        "path": join(GLYPHS_PATH, "devicons.ttf"),
        "ranges": [(0xe700, 0xe7c5)],
        "remaps": [(0xe600, 0xe6c5)],
        "scale": (0.9, 0.9),
        "translate": (-405, -145),
        "modify": """
                0xe739 (0.9, 0.9) (0, 0) # 
                0xe7bd (1, 1) (-570, 0)  # 
                0xe7be (1, 1) (280, 0)   # 
                0xe7bf (1, 1) (360, 0)   # 
                0xe7c0 (1, 1) (-40, 0)   # 
                0xe7c1 (1, 1) (-490, 0)  # 
                0xe7c2 (1, 1) (-270, 0)  # 
                0xe7c3 (1, 1) (290, 0)   # 
                """
    },
    {   # Font Awesome (https://github.com/FortAwesome/Font-Awesome)
        "path": join(GLYPHS_PATH, "font-awesome", "FontAwesome.otf"),
        "ranges": [(0xf000, 0xf2e0)],
        "remaps": [None],
        "scale": (0.8, 0.8),
        "translate": (-100, 80),
        "modify": """
                [0xf0d7, 0xf0da] (1, 1) (45, 0)   #  ~ 
                [0xf0dd, 0xf0de] (1, 1) (45, 0)   #  ~ 
                [0xf100, 0xf103] (1, 1) (60, 0)   #  ~ 
                [0xf104, 0xf105] (1, 1) (240, 0)  #  ~ 
                [0xf106, 0xf107] (1, 1) (55, 0)   #  ~ 
                [0xf175, 0xf176] (1, 1) (160, 0)  #  ~ 
                0xf276           (1, 1) (45, 0)   # 
                0xf294           (1, 1) (100, 0)  # 
                [0xf2c7, 0xf2cb] (1, 1) (40, 0)   #  ~ 
                """
    },
    {   # Font Awesome Extension (https://github.com/AndreLZGava/font-awesome-extension)
        "path": join(GLYPHS_PATH, "font-awesome-extension.ttf"),
        "ranges": [(0xe200, 0xe2a9)],
        "remaps": [(0xe000, 0xe0a9)],
        "scale": (0.8, 0.8),
        "translate": (-310, -80)
    },
    {   # Material Design Icons (https://github.com/Templarian/MaterialDesign)
        "path": join(GLYPHS_PATH, "materialdesign", "MaterialDesignIconsDesktop.ttf"),
        "ranges": [(0xf0001, 0xf1af0)],
        "remaps": [None],
        "scale": (0.9, 0.9),
        "translate": (-410, 0)
    },
    {   # Weather (https://github.com/erikflowers/weather-icons)
        "path": join(GLYPHS_PATH, "weather-icons", "weathericons-regular-webfont.ttf"),
        "ranges": [(0xe300, 0xe3e3)],
        "remaps": [(0xf000, 0xf0eb)],
        "scale": (0.9, 0.9),
        "translate": (0, 0),
        "modify": """
                [0xe300, 0xe338] (0.8, 0.8) (0, 0)      #  ~ 
                0xe339           (1, 1)     (0, -300)   # 
                0xe341           (1, 1)     (0, -300)   # 
                0xe34e           (0.9, 0.9) (75, -110)  # 
                0xe34f           (1, 1)     (270, 0)    # 
                0xe350           (0.9, 0.9) (75, -110)  # 
                [0xe35e, 0xe367] (0.9, 0.9) (0, 0)      #  ~ 
                [0xe3aa, 0xe3ad] (0.8, 0.8) (0, 0)      #  ~ 
                """
    },
    {   # Octicons (https://github.com/primer/octicons)
        "path": join(GLYPHS_PATH, "octicons", "octicons.ttf"),
        "ranges": [(0xf400, 0xf532), (0x2665,), (0x26a1,)],
        "remaps": [(0xf000, 0xf305), None, None],
        "scale": (0.695, 0.695),
        "translate": (-200, 230),
        "modify": """
                0xf480 (1, 1) (0, -250)  # 
                """
    },
    {   # Powerline Symbols
        "path": join(GLYPHS_PATH, "powerline-symbols", "PowerlineSymbols.otf"),
        "ranges": [(0xe0a0, 0xe0a2), (0xe0b0, 0xe0b3)],
        "remaps": [None, None],
        "scale": (0.97, 0.887),
        "translate": (0, -109),
        "modify": """
                0xe0a0 (1, 1) (-60, 0)  # 
                """
    },
    {   # Powerline Extra Symbols (https://github.com/ryanoasis/powerline-extra-symbols)
        "path": join(GLYPHS_PATH, "PowerlineExtraSymbols.otf"),
        "ranges": [(0xe0a3,), (0xe0b4, 0xe0c8), (0xe0ca,), (0xe0cc, 0xe0d4)],
        "remaps": [None, None, None, None],
        "scale": (1, 1),
        "translate": (0, 0),
        "modify": """
                0xe0a3           (0.85, 0.85) (0, 0)   # 
                [0xe0b4, 0xe0b7] (0.84, 0.84) (0, 23)  #  ~ 
                [0xe0b8, 0xe0bf] (0.41, 0.82) (0, 0)   #  ~ 
                [0xe0c0, 0xe0c3] (0.87, 0.87) (0, 0)   #  ~ 
                [0xe0c4, 0xe0c7] (0.81, 0.81) (0, 40)  #  ~ 
                0xe0c8           (0.88, 0.88) (0, 50)  # 
                0xe0ca           (0.88, 0.88) (0, 50)  # 
                [0xe0cc, 0xe0d2] (0.82, 0.82) (0, 0)   #  ~ 
                0xe0d4           (0.82, 0.82) (0, 0)   # 
                """
    },
    {   # IEC Power Symbols (https://unicodepowersymbol.com/)
        "path": join(GLYPHS_PATH, "Unicode_IEC_symbol_font.otf"),
        "ranges": [(0x23fb, 0x23fe), (0x2b58,)],
        "remaps": [None, None],
        "scale": (0.8, 0.8),
        "translate": (-280, -100),
    },
    {   # Font Logos (https://github.com/Lukas-W/font-logos)
        "path": join(GLYPHS_PATH, "font-logos.ttf"),
        "ranges": [(0xf300, 0xf32f)],
        "remaps": [None],
        "scale": (0.73, 0.73),
        "translate": (0, 150)
    },
    {   # Pomicons (https://github.com/gabrielelana/pomicons)
        "path": join(GLYPHS_PATH, "Pomicons.otf"),
        "ranges": [(0xe000, 0xe00a)],
        "remaps": [None],
        "scale": (0.87, 0.87),
        "translate": (-300, 0),
        "modify": """
                0xe009 (1, 1) (330, 0)  # 
                0xe00a (1, 1) (170, 0)  # 
                """
    },
    {   # Codicons (https://github.com/microsoft/vscode-codicons)
        "path": join(GLYPHS_PATH, "codicons", "codicon.ttf"),
        "ranges": [(0xea60, 0xebeb)],
        "remaps": [None],
        "scale": (0.8, 0.8),
        "translate": (-350, -220),
        "modify": """
                [0xea9d, 0xeaa0] (1, 1) (50, 0)  #  ~ 
                [0xeaa6, 0xeaa9] (1, 1) (40, 0)  #  ~ 
                """
    }
]


def main() -> None:
    font = new_font()
    for info in SOURCES_INFO:
        source = fontforge.open(info["path"])
        source.em = P.EM
        transform_all(source, info["scale"], info["translate"])

        ranges = info["ranges"]
        remaps = info["remaps"]
        if len(ranges) != len(remaps):
            raise ValueError("len(ranges):", len(ranges), "len(remaps):", len(remaps))

        for i in range(len(ranges)):
            remap_range(source, remaps[i], ranges[i])
        if "modify" in info:
            modify(source, info["modify"])
        for i in range(len(ranges)):
            copy_range(font, source, ranges[i])

        source.close()
        util.log("Bundled:", info["path"], "->", BUILD_FILE)

    util.fix_all_glyph_points(font, round=True, addExtrema=True)
    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


def remap_range(font, from_range: tuple[int, int] | None, to_range: tuple[int, int]) -> None:
    if from_range is None:
        return
    next_to_codepoint, next_from_codepoint = _remap_util(
        font, from_range, to_range
    )

    to_codepoint = next_to_codepoint()
    from_codepoint = next_from_codepoint()
    while to_codepoint and from_codepoint:
        font.selection.select(from_codepoint)
        font.copy()
        font.selection.select(to_codepoint)
        font.paste()
        try:
            font[to_codepoint].glyphname = font[from_codepoint].glyphname
        except TypeError as e:
            if str(e) != "No such glyph":
                raise
        to_codepoint = next_to_codepoint()
        from_codepoint = next_from_codepoint()

    if to_codepoint:
        raise ValueError("Invalid range or remap (range is smaller than remap)")
    if from_codepoint:
        raise ValueError("Invalid range or remap (remap is smaller than range)")


def _remap_util(font, from_range: tuple[int, int], to_range: tuple[int, int]) -> tuple[Callable[[], int | None], Callable[[], int | None]]:
    fixed_from = _tuple_to_range(from_range or to_range)
    fixed_to = _tuple_to_range(to_range)
    remain_skip_count = len(fixed_from) - len(fixed_to)
    from_iter = iter(fixed_from)
    to_iter = iter(fixed_to)

    if remain_skip_count > 0:
        def next_from_codepoint():
            nonlocal remain_skip_count, from_iter
            ret = next(from_iter, None)
            while ret and remain_skip_count >= 0:
                try:
                    _ = font[ret]
                    break
                except TypeError:  # No such glyph
                    remain_skip_count -= 1
                    ret = next(from_iter, None)
                    continue
            return ret
    elif remain_skip_count == 0:
        def next_from_codepoint():
            return next(from_iter, None)
    else:
        raise ValueError("from_range is smaller than to_range: ",
                         "from_range:", len(fixed_from),
                         "to_range:", len(fixed_to))

    def next_to_codepoint():
        return next(to_iter, None)

    return next_to_codepoint, next_from_codepoint


def transform_all(font, scale: tuple[float, float], translate: tuple[int, int]) -> None:
    scale = psMat.scale(*scale)
    translate = psMat.translate(*translate)
    transform = psMat.compose(scale, translate)
    font.selection.all()
    font.transform(transform)
    for glyph in list(font.selection.byGlyphs):
        if glyph.width != 0:
            glyph.left_side_bearing = int(max(glyph.left_side_bearing, 0))
            glyph.right_side_bearing = int(max(glyph.right_side_bearing, 0))
        glyph.width = P.EM // 2
    font.selection.none()


def modify(font, script: str) -> None:
    for line in script.split(sep="\n"):
        line = line.strip().replace(" ", "").replace("(", ",(")  # )) <- nvim の自動インデントがおかしくなるので
        if len(line) < 1 or line.startswith("#"):
            continue
        try:
            ops = ast.literal_eval(line)
        except SyntaxError:
            util.log("invalid syntax:", line)
            continue
        if type(ops[0]) is int:
            codepoints = range(ops[0], ops[0] + 1)
        else:
            codepoints = range(ops[0][0], ops[0][1] + 1)
        scale = psMat.scale(*ops[1])
        translate = psMat.translate(*ops[2])
        transform_mat = psMat.compose(scale, translate)
        for codepoint in codepoints:
            font[codepoint].transform(transform_mat)
            font[codepoint].width = P.EM // 2


def new_font():
    familyname = splitext(basename(BUILD_FILE))[0]
    font = fontforge.font()
    font.ascent = P.ASCENT
    font.descent = P.DESCENT
    font.italicangle = 0
    font.upos = P.UNDERLINE_POS
    font.uwidth = P.UNDERLINE_HEIGHT
    font.familyname = familyname
    font.encoding = P.ENCODING
    font.fontname = familyname
    font.fullname = familyname
    return font


def copy_range(font, source, range_: tuple[int, int | None]) -> None:
    range_iter = iter(_tuple_to_range(range_))
    codepoint = next(range_iter, None)
    while codepoint:
        source.selection.select(codepoint)
        source.copy()
        font.selection.select(codepoint)
        font.paste()
        try:
            new_glyphname = font[codepoint].glyphname + "#nf"
            font[codepoint].glyphname = new_glyphname
        except TypeError as e:
            if str(e) != "No such glyph":
                raise
        codepoint = next(range_iter, None)


def _tuple_to_range(tuple_: tuple[int, int | None]) -> range:
    fixed = (*tuple_, None)
    start = fixed[0]
    stop = (fixed[1] or fixed[0]) + 1
    return range(start, stop)


if __name__ == "__main__":
    main()
