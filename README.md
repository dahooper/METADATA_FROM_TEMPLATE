# METADATA_FROM_TEMPLATE
This page provides documentation for David Hooper's module_data_object.py python software, which can be used to:

* Create data objects, populated with metadata, from template files that allow substitutions - see here for an example template file.
* Write such data objects to netCDF files
* Extract data objects from netCDF files

The template files are written using YAML syntax, which is easier to write than the Common Data form Language (CDL) used by the netCDF ncgen/ncdump software. The contents of the page are as follows:

* Basic usage
* Data object structure
* Permissible data types
* Template file syntax
* Template file structure
* Template file substitution fields
* Template file requirements
* Creator class methods
* Software dependencies


### Basic Usage
