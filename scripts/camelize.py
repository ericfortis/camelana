import string
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

# This script was used for the spacing modifications. On the other hand,
# I used Inkscape and FontForge for drawing and configuring the ligatures.

FONT_NAME = 'Camelana'
SPACE_MULT = 4
LEFT_PAD_FACTOR = 0.33

# Download NotoSans: https://fonts.google.com/noto/specimen/Noto+Sans
WEIGHTS = ['Regular', 'SemiBold', 'Italic', 'SemiBoldItalic']
def font_to_modify(w): return Path(f'Noto_Sans/static/NotoSans-{w}.ttf')

# Acronyms:
#  HMTX: Horizontal Metrics Table https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx
#  LSB: Left Side Bearing
#  calt: Contextual Alternates https://learn.microsoft.com/en-us/typography/opentype/spec/features_ae#tag-calt

def main():
	for weight in WEIGHTS:
		out_file = f'{FONT_NAME}-{weight}.ttf'
		font = TTFont(font_to_modify(weight))

		new_space_width = widen_space(font, SPACE_MULT)
		new_glyphs = inject_new_left_padded_caps_glyphs(font, int(new_space_width * LEFT_PAD_FACTOR))
		use_padded_cap_when_preceding_glyph_is_lowercase(font, new_glyphs)

		names = {
			1: FONT_NAME,
			16: FONT_NAME,
			3: f'{FONT_NAME}-{weight}',
			6: f'{FONT_NAME}-{weight}',
			4: f'{FONT_NAME} {weight}',
			2: weight,
		}
		for record in font['name'].names:
			if record.nameID in names:
				record.string = names[record.nameID].encode(record.getEncoding())

		font.save(out_file)
		print(out_file)


def widen_space(font, factor):
	horizontal_metrics = font['hmtx'].metrics
	width, lsb = horizontal_metrics['space']
	new_width = width * factor
	horizontal_metrics['space'] = (new_width, lsb)
	return new_width


def inject_new_left_padded_caps_glyphs(font, padding):
	horizontal_metrics = font['hmtx'].metrics
	glyf_table = font['glyf']
	cmap = font.getBestCmap()  # char -> glyph map

	new_glyphs = {}  # original glyph name -> padded glyph name
	for c in string.ascii_uppercase:
		glyph_name = cmap.get(ord(c))
		if not glyph_name or glyph_name not in horizontal_metrics:
			continue
		new_name = glyph_name + '.lpad'
		width, lsb = horizontal_metrics[glyph_name]
		horizontal_metrics[new_name] = (width + padding, lsb + padding)
		glyf_table[new_name] = glyf_table[glyph_name]
		new_glyphs[glyph_name] = new_name

	font.setGlyphOrder(glyf_table.glyphOrder)
	return new_glyphs


def use_padded_cap_when_preceding_glyph_is_lowercase(font, new_glyphs):
	# Keep both classes in the same order so positions line up 1:1
	ordered_originals = sorted(new_glyphs.keys())
	ordered_padded = [new_glyphs[g] for g in ordered_originals]

	cmap = font.getBestCmap()
	lower_names = [cmap[ord(c)] for c in string.ascii_lowercase if ord(c) in cmap]

	lower_class = ' '.join(lower_names)
	target_class = ' '.join(ordered_originals)
	sub_class = ' '.join(ordered_padded)

	addOpenTypeFeaturesFromString(font, f"""
	feature calt {{
		sub [{lower_class}] [{target_class}]' by [{sub_class}];
	}} calt;
	""")


if __name__ == '__main__':
	main()
