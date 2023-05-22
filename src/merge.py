import sys
import fontforge
import util
import properties as P
from datetime import datetime

if len(sys.argv) != 6:
    raise ValueError("Invalid argument")

FONT_EN_TTF = sys.argv[1]
FONT_JP_TTF = sys.argv[2]
FONT_NF_TTF = sys.argv[3]
FONT_STYLE = sys.argv[4]
BUILD_FILE = sys.argv[5]


def main():
    font = new_font()

    merge_en(font)
    merge_jp(font)
    merge_nf(font)

    font.selection.all()
    font.autoHint()
    font.autoInstr()
    font.selection.none()

    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


def merge_en(font):
    en_font = fontforge.open(FONT_EN_TTF)
    en_font.encoding = P.ENCODING
    font.mergeFonts(en_font)
    util.log("Merged:", FONT_EN_TTF, "->", BUILD_FILE)


def merge_jp(font):
    jp_font = fontforge.open(FONT_JP_TTF)
    for glyph in jp_font.glyphs():
        unicode = glyph.unicode
        if unicode == -1:
            continue
        jp_font.selection.select(unicode)
        jp_font.copy()
        font.selection.select(unicode)
        font.paste()
        font[unicode].glyphname = glyph.glyphname
        if glyph.altuni is not None:
            font[unicode].altuni = glyph.altuni
        font[unicode].unicode = unicode
    font.mergeFonts(jp_font)
    font.selection.none()
    jp_font.close()
    util.log("Merged:", FONT_JP_TTF, "->", BUILD_FILE)


def merge_nf(font):
    font.mergeFonts(FONT_NF_TTF)
    util.log("Merged:", FONT_NF_TTF, "->", BUILD_FILE)


def new_font():
    style_prop = P.STYLE_PROPERTY[FONT_STYLE]
    font = fontforge.font()
    font.ascent = P.ASCENT
    font.descent = P.DESCENT
    font.italicangle = P.ITALICANGLE if "Italic" in FONT_STYLE else 0
    font.upos = P.UNDERLINE_POS
    font.uwidth = P.UNDERLINE_HEIGHT
    font.familyname = P.FAMILY
    font.copyright = P.COPYRIGHT
    font.encoding = P.ENCODING
    font.fontname = P.FAMILY + "-" + FONT_STYLE
    font.fullname = P.FAMILY + " " + FONT_STYLE
    font.version = P.VERSION
    font.appendSFNTName('English (US)', 'SubFamily', FONT_STYLE)
    font.appendSFNTName(
        "English (US)",
        "UniqueID",
        "; ".join(
            [
                f"FontForge {fontforge.version()}",
                P.FAMILY + " " + FONT_STYLE,
                P.VERSION,
                datetime.today().strftime("%F"),
            ]
        ),
    )

    font.weight = style_prop["weight"]
    font.os2_weight = style_prop["os2_weight"]
    font.os2_width = 5  # Medium (100%)
    font.os2_stylemap = style_prop["os2_stylemap"]
    font.os2_vendor = "2357"  # Me
    font.os2_panose = (  # https://monotype.github.io/panose/pan1.htm
        2,                            # Family Kind = 2-Latin: Text and Display
        11,                           # Serif Style = Nomal Sans
        style_prop["panose_weight"],  # Weight
        9,                            # Proportion = 9-Monospaced
        3,                            # Contrast = 3-Very Low
        2,                            # Stroke Variation = 2-No Variation
        2,                            # Arm Style = 2-Straight Arms/Horizontal
        style_prop['panose_letterform'],  # Letterform
        2,                            # Midline = 2-Standard/Trimmed
        4,                            # X-height = 4-Constant/Large
    )

    # typoascent, typodescent is generic version for above.
    # the `_add` version is for setting offsets.
    font.os2_typoascent = P.ASCENT
    font.os2_typodescent = -P.DESCENT
    font.os2_typoascent_add = 0
    font.os2_typodescent_add = 0

    # winascentwindescent is typoascent/typodescent for Windows.
    font.os2_winascent = P.ASCENT
    font.os2_windescent = P.DESCENT
    font.os2_winascent_add = 0
    font.os2_windescent_add = 0

    # winascentwindescent is typoascent/typodescent for macOS.
    font.hhea_ascent = P.ASCENT
    font.hhea_descent = -P.DESCENT
    font.hhea_ascent_add = 0
    font.hhea_descent_add = 0

    # linegap is for gap between lines.  The `hhea_` version is for macOS.
    font.os2_typolinegap = 0
    font.hhea_linegap = 0

    return font


if __name__ == "__main__":
    main()
