from fontTools.ttLib import TTFont

font = TTFont("../v2_camelana/Camelana-Regular.ttf")

gsub = font["GSUB"].table

print("=== Features ===")
for rec in gsub.FeatureList.FeatureRecord:
	print(f"\nFeature: {rec.FeatureTag}")
	for idx in rec.Feature.LookupListIndex:
		print(f"  Lookup #{idx}")

print("\n=== Lookups ===")

for i, lookup in enumerate(gsub.LookupList.Lookup):
	print(f"\nLookup {i}")
	print(f"  Type : {lookup.LookupType}")
	print(f"  Flags: {lookup.LookupFlag}")

	for j, sub in enumerate(lookup.SubTable):
		print(f"\n  Subtable {j}: {type(sub).__name__}")

		# Single substitutions
		if hasattr(sub, "mapping"):
			print("    Mapping:")
			for src, dst in sub.mapping.items():
				print(f"      {src} -> {dst}")

		# Ligatures
		if hasattr(sub, "ligatures"):
			print("    Ligatures:")
			for first, ligs in sub.ligatures.items():
				for lig in ligs:
					seq = " ".join([first] + lig.Component)
					print(f"      {seq} -> {lig.LigGlyph}")

		# Chain contextual substitutions
		if type(sub).__name__ == "ChainContextSubst":
			print("    Backtrack:")
			if getattr(sub, "BacktrackCoverage", None):
				for cov in sub.BacktrackCoverage:
					print("      ", cov.glyphs)
			else:
				print("       (none)")

			print("    Input:")
			if getattr(sub, "InputCoverage", None):
				for cov in sub.InputCoverage:
					print("      ", cov.glyphs)
			else:
				print("       (none)")

			print("    LookAhead:")
			if getattr(sub, "LookAheadCoverage", None):
				for cov in sub.LookAheadCoverage:
					print("      ", cov.glyphs)
			else:
				print("       (none)")

			print("    SubstLookupRecords:")
			if getattr(sub, "SubstLookupRecord", None):
				for rec in sub.SubstLookupRecord:
					print(
						f"      SequenceIndex={rec.SequenceIndex}, "
						f"LookupIndex={rec.LookupListIndex}"
					)
			else:
				print("       (none)")
