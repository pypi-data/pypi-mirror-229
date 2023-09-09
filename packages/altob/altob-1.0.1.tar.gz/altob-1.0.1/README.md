# Altob

Abundance learning for ToBRFV variants. The primary purpose of the tool is:

* Estimating abundace of clades of ToBRFV from sequencing data

You can read more about how Altob works in the Alcov preprint as it was originally developed for predicting abundances of variants of concern of SARS-CoV-2 in wastewater sequencing data, __[Alcov: Estimating Variant of Concern Abundance from SARS-CoV-2 Wastewater Sequencing Data](https://www.medrxiv.org/content/10.1101/2021.06.03.21258306v1)__

The tool can also be used for:

* Converting between nucleotide and amino acid mutations for ToBRFV 
* Determining the frequency of mutations of interest in BAM files
* Plotting the depth for each tiled amplicon for ToBRFV, designed based on the ARTIC protocol (https://github.com/artic-network/artic-ncov2019/tree/master/primer\_schemes/nCoV-2019/V3)
* Comparing amplicon GC content with its read depth (as a measure of degredation)

The tool is under active development. If you have questions or issues, please open an issue on GitHub or email me (email in setup.py).

## Installing

The latest release can be downloaded from PyPI

`pip install altob`

This will install the Python library and the CLI.

To install the development version, clone the repository and run

`pip install .`

## Usage example

### Preprocessing

Altob expects a BAM file of reads aligned to the ToBRFV reference genome. For an example of how to process Illumina reads, check the `prep` directory for a script called "prep.py".

### Estimating relative abundance of lineages/clades:

```
altob find_lineages reads.bam
```

Finding lineages in BAM files for multiple samples:

```
altob find_lineages samples.txt
```

Where `samples.txt` looks like:

```
path/to/reads1.bam	Sample 1 name
path/to/reads2.bam	Sample 2 name
...
```

Optionally specify which clades to look for

```
altob find_lineages reads.bam lineages.txt
```

Where `lineages.txt` looks like:

```
clade_1
clade_3
...
```

Optionally change minimum read depth (default 40)

```
altob find_lineages --min_depth=5 reads.bam
```

Optionally show how predicted mutation rates agree with observed mutation rates

```
altob find_lineages --show_stacked=True reads.bam
```

Use mutations which are found in multiple VOCs (can help for low coverage samples). Note: this is now the defaut behaviour.

```
altob find_lineages --unique=False reads.bam
```

Plotting changes in clade distributions over time for multiple sites

```
altob find_lineages --ts samples.txt
```

Where `samples.txt` looks like:

```
path/to/reads1.bam	SITE1_2021-09-10
path/to/reads2.bam	SITE1_2021-09-12
...
path/to/reads3.bam	SITE2_2021-09-10
path/to/reads4.bam	SITE2_2021-09-12
...
```

### Converting mutation names: 
(Note: These examples are from SARS-CoV-2 genomic sequences)
```
$ altob nt A23063T
A23063T causes S:N501Y
$ altob aa S:E484K
G23012A causes S:E484K
```

### Finding mutations in BAM file:

```
altob find_mutants reads.bam
```

Finding mutations in BAM files for multiple samples:

```
altob find_mutants samples.txt
```

Where `samples.txt` looks like:

```
path/to/reads1.bam	Sample 1 name
path/to/reads2.bam	Sample 2 name
...
```

Running `find_mutants` will print the number of reads with and without each mutation in each sample and then generate a heatmap showing the frequencies for all samples.

You can also specify a custom mutations file:

```
altob find_mutants samples.txt mutations.txt
```

Where `mutations.txt` looks like:
(Note: these examples are from SARS-CoV-2 genomic sequences)

```
S:N501Y
G23012A
...
```

### Getting the read depth for each amplicon

```
altob amplicon_coverage reads.bam
```

or

```
altob amplicon_coverage samples.txt
```

### Plotting amplicon GC content against amplicon depth

```
altob gc_depth reads.bam
```

or

```
altob gc_depth samples.txt
```
