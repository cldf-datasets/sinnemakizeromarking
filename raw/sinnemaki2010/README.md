# Zero marking and word order of core arguments

Kaius Sinnemäki & Noora Ahola, University of Helsinki

***

This repository contains the supplementary data for the following article; please cite it when using the data:

Sinnemäki, Kaius 2010. Word order in zero-marking languages. *Studies in Language* 34(4): 869–912. https://doi.org/10.1075/sl.34.4.04sin.


The data is available as an electronic supplement of the original article. Here we provide the data and all metadata in a computer-readable form, roughly following the practices of the *AUTOTYP* database (Bickel et al. 2017. The original article contained data on 848 languages, but here we have added data on 47 more languages, also fixing some errors in the original data. This dataset thus contains data on 895 languages, from 469 genera. This repository has been created by Kaius Sinnemäki with the assistance of Noora Ahola. We are also grateful to Viljami Haakana for assistance with the bibliography.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7693339.svg)](https://doi.org/10.5281/zenodo.7693339)

***

## Contents

### [Bibliography](https://version.helsinki.fi/hals/sinnemaki/sinnemaki2010/-/tree/main/bibliography)

The sources for all entries are listed in the file References_ZeroMarking.bib.


### [Data](https://version.helsinki.fi/hals/sinnemaki/sinnemaki2010/-/tree/main/data)

Comma-separated text-files (csv) containing the data in the directory data/.
- **`LingVariables`**: Data on word order and morphological marking of lexical subject and object of a transitive verb, as defined in Sinnemäki (2010).
- **`Register`**: Genealogical, geographical and other information on the languages in the database, with three subtypes:
    * IDs: Three codes are provided, the Glottolog code, ISO639.3 code, and the WALS code.
    * Genealogical information:
        * The genealogy subset contains information on the genealogical classification of each language. We provide three pieces of information on genealogical classification: 1. language name (as in the [WALS](https://wals.info/languoid/genealogy), Dryer & Haspelmath 2013, or if not there, then as in the [Glottolog] version 3.2 (https://glottolog.org/), Hammarström et al. 2018), 2. genus, which is an intermediate level in the genealogical classification of the [WALS](https://wals.info/languoid/genealogy), and 3. family, which is the highest level in the genealogical classification of the [WALS](https://wals.info/languoid/genealogy). See more details about these classifications via the links.
    * Geographical information:
        * The geography subset contains information on the geographical location of each language, namely the longitudes and latitudes (from the [WALS](https://wals.info/languoid/genealogy), or if not there, then as in the [Glottolog] version 3.2 (https://glottolog.org/)). In addition, this subset contains six classifications of languages into areas: 1. a fine-grained classification of languages into 24 areas (as in the [AUTOTYP](https://github.com/autotyp/autotyp-data/blob/0.1.0/figures/areas.jpg), Bickel et al. 2017), 2. a more coarse-grained classification of languages into ten continents or subcontinents (as in the [AUTOTYP](https://github.com/autotyp/autotyp-data/blob/0.1.0/figures/continents.jpg)), 3. a coarse-grained classification of languages into the six macroareas (as in the [WALS](https://wals.info/languoid)), 4. a very broad classification of languages into the three macrocontinents (as in Nichols 1992), 5. same as the three macrocontinents but splitting the Old World into Africa and Eurasia, and 6. grouping languages into those used in the Circum-Pacific area or outside, as defined in [Bickel & Nichols (2006)](https://doi.org/10.3765/bls.v32i2.3488). See more details about these areas from the metadata files or by following the links provided.


### [Metadata](https://version.helsinki.fi/hals/sinnemaki/sinnemaki2010/-/tree/main/metadata)

The data files are associated with metadata files that describe the definitions of each feature and feature value in the data file. The metadata files are provided in YAML format in the directory metadata/.

The following fields are provided for each feature:
- **`Feature`**: the name of the feature
- **`Description`**: the definition of the feature
- **`FeatureType`**: the type of the feature:
    * data = the entries are based on the analysis of linguistic data
    * register = the entries contain geographical, genealogical and other information about each language
    * quality = the entries contain information about data sources
- **`DataType`**: whether the feature values are of the type categorical, ratio, count or logical
- **`N_entries`**: the number of entries for the feature, excluding blank cells (or 'NA')
- **`N_languages`**: the number of languages in the database with non-blank('NA') feature values
- **`N_missing`**: the number of languages with missing information for the feature
- **`N_Levels`**: where applicable, the number of distinct levels that a categorical feature may have
- **`Levels`**: where applicable, the levels of a categorical feature used in the data file


***

This research has received funding from Academy of Finland (project _Grammatical Complexity of Natural Languages_, 2003-2006), Langnet - the Finnish Doctoral Programme in Language Studies (2006-2008), Finnish Cultural Foundation (2009), and from the Faculty of Arts, University of Helsinki (Associate Professor Starting Grant).


***

# References

Bickel, Balthasar & Johanna Nichols. 2006. Oceania, the Pacific Rim, and the Theory of Linguistic Areas. _Berkeley Linguistic Society_ 32: 3-15. Available online at https://doi.org/10.3765/bls.v32i2.3488.

Bickel, Balthasar, Johanna Nichols, Taras Zakharko, Alena Witzlack-Makarevich, Kristine Hildebrandt, Michael Rießler, Lennart Bierkandt, Fernando Zúñiga & John B. Lowe. 2017. The AUTOTYP typological databases, version 0.1.0. https://github.com/autotyp/autotyp-data/tree/0.1.0.

Dryer, Matthew. 2013. Determining dominant word order. In Matthew Dryer & Martin Haspelmath (eds.), The World Atlas of Language Structures Online. Leipzig: Max Planck Institute for Evolutionary Anthropology. (http://wals.info/chapter/s6).

Dryer, Matthew S. & Martin Haspelmath (eds.). 2013. _The World Atlas of Language Structures Online_. Leipzig: Max Planck Institute for Evolutionary Anthropology. Available online at http://wals.info.

Hammarström, Harald, Sebastian Bank, Robert Forkel & Martin Haspelmath. 2018. _Glottolog 3.2_. Jena: Max Planck Institute for the Science of Human History. Available online at http://glottolog.org.

Nichols, Johanna. 1992. _Linguistic Diversity in Space and Time_. Chicago: University of Chicago Press. 

Simons, Gary F. & Charles D. Fennig. 2018. Ethnologue: Languages of the World, 21st edition. Dallas, TX: SIL International. http://www.ethnologue.com.
