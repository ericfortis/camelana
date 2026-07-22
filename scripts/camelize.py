import string
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

# This script was used for the spacing modifications. On the other hand,
# I used Inkscape and FontForge for drawing and configuring the ligatures.

OUT_DIR = Path('v2_camelana')
FONT_NAME = 'Camelana'
SPACE_MULT = 4
LEFT_PAD_FACTOR = 0.33
CUSTOM_GLYPHS_EXT = '.lpad'

# Download NotoSans
WEIGHTS = ['Regular', 'SemiBold', 'Italic', 'SemiBoldItalic']
def font_to_modify(w): return Path(f'Noto_Sans/static/NotoSans-{w}.ttf')

# Acronyms:
#  HMTX: Horizontal Metrics Table https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx
#  LSB: Left Side Bearing
#  calt: Contextual Alternates https://learn.microsoft.com/en-us/typography/opentype/spec/features_ae#tag-calt

def main():
	for weight in WEIGHTS:
		out_file = str(OUT_DIR / f'{FONT_NAME}-{weight}.ttf')
		font = TTFont(font_to_modify(weight))

		new_space_width = widen_space(font, SPACE_MULT)
		new_glyphs = inject_new_left_padded_caps_glyphs(font, int(new_space_width * LEFT_PAD_FACTOR))
		fea = generate_feature_spec_for_using_padded_cap_when_preceding_glyph_is_lowercase(font, new_glyphs)
		addOpenTypeFeaturesFromString(font, fea)

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


def widen_space(font, factor) -> float:
	horizontal_metrics = font['hmtx'].metrics
	width, lsb = horizontal_metrics['space']
	new_width = width * factor
	horizontal_metrics['space'] = (new_width, lsb)
	return new_width


def inject_new_left_padded_caps_glyphs(font, padding: int):
	horizontal_metrics = font['hmtx'].metrics
	glyf_table = font['glyf']
	cmap = font.getBestCmap() # char -> glyph map

	new_glyphs = {}  # original glyph name -> padded glyph name
	for c in string.ascii_uppercase:
		glyph_name = cmap.get(ord(c))
		if not glyph_name or glyph_name not in horizontal_metrics:
			continue
		new_name = glyph_name + CUSTOM_GLYPHS_EXT
		width, lsb = horizontal_metrics[glyph_name]
		horizontal_metrics[new_name] = (width + padding, lsb + padding)
		glyf_table[new_name] = glyf_table[glyph_name]
		new_glyphs[glyph_name] = new_name

	font.setGlyphOrder(glyf_table.glyphOrder)
	return new_glyphs


def generate_feature_spec_for_using_padded_cap_when_preceding_glyph_is_lowercase(font, new_glyphs) -> str:
	originals = sorted(new_glyphs.keys())
	padded = [new_glyphs[g] for g in originals]

	cmap = font.getBestCmap()
	lower_names = [cmap[ord(c)] for c in string.ascii_lowercase if ord(c) in cmap]

	lower_class = ' '.join(lower_names)
	target_class = ' '.join(originals)
	sub_class = ' '.join(padded)

	return f"""
	feature calt {{
		sub [{lower_class}] [{target_class}]' by [{sub_class}];
	}} calt;
	"""


if __name__ == '__main__':
	main()
