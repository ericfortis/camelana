from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

FEA = './Camelana-Regular.fea'
TTF = '../v2_camelana/Camelana-Regular.ttf'

# Wipes out any existing feature
font = TTFont(TTF)
addOpenTypeFeaturesFromString(font, open(FEA).read())
font.save(TTF)
