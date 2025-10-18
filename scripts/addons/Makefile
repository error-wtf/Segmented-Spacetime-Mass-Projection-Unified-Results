# SSZ Add-ons Makefile
# Separat ausführbare Erweiterungen der Pipeline

.PHONY: segment-redshift help

help:
	@echo "SSZ Add-ons"
	@echo "==========="
	@echo ""
	@echo "Targets:"
	@echo "  segment-redshift    - Segment-Redshift Berechnung (proxy=N)"
	@echo "  segment-redshift-rho - Segment-Redshift mit rho-pr proxy"
	@echo "  segment-redshift-gtt - Segment-Redshift mit gtt proxy"
	@echo ""
	@echo "Alle Add-ons schreiben nach reports/ und reports/figures/"
	@echo "KEINE Änderungen an der Pipeline!"

segment-redshift:
	@echo "================================================================================"
	@echo "SSZ Segment-Redshift Add-on (proxy=N)"
	@echo "================================================================================"
	python scripts/addons/segment_redshift_addon.py \
		--segment-redshift \
		--proxy N \
		--nu-em 1.0e18 \
		--r-em 2.0 \
		--r-out 50.0 \
		--seg-plot
	@echo ""
	@echo "Output: reports/segment_redshift.csv | .md | .png"

segment-redshift-rho:
	@echo "================================================================================"
	@echo "SSZ Segment-Redshift Add-on (proxy=rho-pr)"
	@echo "================================================================================"
	python scripts/addons/segment_redshift_addon.py \
		--segment-redshift \
		--proxy rho-pr \
		--nu-em 1.0e18 \
		--r-em 2.0 \
		--r-out 50.0 \
		--seg-plot
	@echo ""
	@echo "Output: reports/segment_redshift.csv | .md | .png"

segment-redshift-gtt:
	@echo "================================================================================"
	@echo "SSZ Segment-Redshift Add-on (proxy=gtt)"
	@echo "================================================================================"
	python scripts/addons/segment_redshift_addon.py \
		--segment-redshift \
		--proxy gtt \
		--nu-em 1.0e18 \
		--r-em 2.0 \
		--r-out 50.0 \
		--seg-plot
	@echo ""
	@echo "Output: reports/segment_redshift.csv | .md | .png"
