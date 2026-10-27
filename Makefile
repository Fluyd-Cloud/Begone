.PHONY: build init

build:
	begone-convert data/numbers.yaml dist/begone-fr-full.xml all
	begone-convert data/numbers.yaml dist/begone-fr-demarchage.xml spam
	begone-convert data/numbers.yaml dist/begone-fr-voip.xml voip
	begone-convert data/numbers.yaml dist/begone-fr-prepaid.xml prepaid
	begone-convert data/numbers.yaml dist/begone-fr-onoff.xml onoff
	begone-convert data/numbers.yaml dist/begone-fr-ubicentrex.xml ubicentrex
	begone-convert data/numbers.yaml dist/begone-fr-lyca.xml lyca
	begone-convert data/numbers.yaml dist/begone-fr-bjt.xml bjt
	begone-convert data/numbers.yaml dist/begone-fr-kavcom.xml kavkom
	begone-convert data/numbers.yaml dist/begone-fr-destiny.xml destiny
	begone-convert data/numbers.yaml dist/begone-fr-spartel.xml spartel
	begone-convert data/numbers.yaml dist/begone-fr-getandgo.xml getandgo

init:
	uv venv
	uv sync
