# Host build of the hardware-independent firmware modules and their tests.
CC ?= cc
CFLAGS ?= -std=c99 -O2 -Wall -Wextra -Werror -Ilib
LDLIBS = -lm

.PHONY: test clean
test: build/test_beam
	./build/test_beam

build/test_beam: test/test_beam.c lib/beam.c lib/beam.h | build
	$(CC) $(CFLAGS) -o $@ test/test_beam.c lib/beam.c $(LDLIBS)

build:
	mkdir -p build

clean:
	rm -rf build
