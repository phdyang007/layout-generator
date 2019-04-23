KLAYOUT = klayout -zz -e -j . -r
VPATH = ./layouts

all: via_test.oas


m2_%.oas: configs/m2_%.csv ./src/m2.py
	mkdir -p layouts
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=1/0


via_%.oas: configs/via_%.csv ./src/via1.py
	$(KLAYOUT) $(word 2,$+) -rd csv_file=$< -rd dest=./layouts -rd outOAS=$@ -rd outLayer=2/0
	zip -r ./layouts/via.zip ./layouts


clean:
	rm -rf layouts/*