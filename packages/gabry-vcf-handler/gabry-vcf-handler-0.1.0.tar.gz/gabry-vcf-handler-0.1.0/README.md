# vcf-handler

This repo is an installable python package and command line tool built for creating .csv files of annotated variants from VCF files. 
Currently the main process annotates variants with the following information either found within the VCF or pulled from external sources:
1. Depth of sequence coverage at the site of variation.
2. Number of reads supporting the variant.
3. Percentage of reads supporting the variant versus those supporting reference reads.
4. Gene ID of the variant, type of variation (substitution,
insertion, CNV, etc.) and their effect (missense, silent, intergenic, etc.) using 
the [VEP hgvs API](https://rest.ensembl.org/#VEP)
5. The minor allele frequency of the variant if available.
6. ***TBD***

This package is publicly installable from [PyPI](https://pypi.org/project/gabry-vcf-handler/), 
and can also be executed from the command line w

## Developing

This repo uses [PDM](https://pdm.fming.dev/latest/). Install PDM and then install dependencies with `pdm install`.

Running test suite: `pdm run test`
Running auto-linter: `pdm run lint-fix`

## Releases

This package is published on [PyPI](https://pypi.org/project/gabry-vcf-handler/). In order to create a new release, bump the version in the [pyproject.toml](pyproject.toml) file, create a PR, and merge that change into master. When that change is merged into master, the new version will be automatically recognized and published.