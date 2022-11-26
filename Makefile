.PHONEY: build

build:
	docker build . -f Dockerfile -t mental_math_gym:0.1