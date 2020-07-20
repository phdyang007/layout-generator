KLAYOUT = klayout -zz -e -j . -r
VPATH = ./layouts

all: via_test.oas


m2_%.oas: configs/m2_%.csv ./src/m2.py
	mkdir -p layouts
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=1/0


via_%.oas: configs/via_%.csv ./src/via1.py
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=2/0
	zip -r ./layouts/via.zip ./layouts

m2_drc.gds: configs/m2_drcb.csv ./src/m2_drc.py
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=2/0
	# generate conflict cells images
	cd src && python gds2img.py ../layouts/ ../layouts/ 1
	cd src && python gds2img.py ../layouts/ ../layouts/ 2
	zip -r ./layouts/m2_drc.zip ./layouts 

hilbert_test: configs/hilbert_test.csv ./src/hilbert.py
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=2/0

peano_test: configs/peano_test.csv ./src/peano.py
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=2/0


m2_ww.oas: configs/m2_ww.csv configs/m2_ww_drc.csv ./src/m2.py
	mkdir -p layouts
	$(KLAYOUT) $(word 3,$+) -rd csv_file=$< -rd drc_file=$(word 2,$+) -rd dest=./layouts -rd outOAS=$@ -rd outLayer=1/0

clean:
	rm -rf layouts/*