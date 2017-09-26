# METADATA_FROM_TEMPLATE
This page provides documentation for David Hooper's module_data_object.py python software, which can be used to:

* Create data objects, populated with metadata, from template files that allow substitutions - see example template file named module_data_object_example_template.yaml
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


## Basic Usage
This software has be written for use under python 2.7.

In order to create an "empty" data object - i.e. one that contains all of the necessary metadata and that has variable arrays of the appropriate size, shape, and data type, albeit filled with values of zero - the following code must be used:

````python
import module_data_object
creator = module_data_object.Creator()
data_object_type = creator.load_a_template(template_file_path)
data_object = creator.create_from_template(data_object_type,lengths_of_dimensions,substitutions)
````
where _template_file_path_ is the path of the template file, _data_object_type_ is a unique identification string (which is recorded within the template file), _lengths_of_dimensions_ is a dictionary specifying the lengths of the required (netCDF) dimensions, and _substitutions_ is a dictionary containing the specific values that must be substituted into the template. Further details are given in the template requirements section below. The user must subsequently populate the "empty" arrays with appropriate variable values.

The Creator class methods section below gives details of additional functionality.

In order to write such a data object to a netCDF data file:
````python
import module_data_object
exit_code = module_data_object.write_to_netcdf_file(data_object,netcdf_file_path)
````
where _netcdf_file_path_ is the path of the netCDF file and _exit_code_ indicates the success (with a value of 0) or failure (with a value of 1) of the operation.

In order to extract a data object from a netCDF data file:
````python
import module_data_object
data_object = module_data_object.extract_from_netcdf_file(netcdf_file_path)
````
An empty dictionary will be returned if the netCDF file path is invalid or if any other errors are encountered.

## Data object structure
The data objects used by this module emulate the structure of a netCDF file in a series of nested python dictionaries. The best way to understand this is to extract a data object from a netCDF file, as described in the usage section above. A generalised example of a data object is shown below.
````
data_object = {
    "names_of_global_attributes": [
        "global_attribute_1_name", "global_attribute_1_name"],
    "global_attributes": {
        "global_attribute_1_name": {
            "data_type": global_attribute_1_data_type,
            "value": global_attribute_1_value},
        "global_attribute_2_name": {
            "data_type": global_attribute_2_data_type,
            "value": global_attribute_2_value}},
    "names_of_dimensions": [
        "dimension_1_variable_name", "dimension_2_variable_name"],
    "dimensions": {
        "dimension_1_variable_name": length_of_dimension_1_variable_values,
        "dimension_2_variable_name": length_of_dimension_2_variable_values},
    "names_of_variables": [
        "variable_1_name", "variable_2_name"],
    "variables": {
        "variable_1_name" : {
            "dimensions": [list of dimension names],
            "data_type": variable_1_data_type,
            "values": [numpy array of suitable size/shape and data type],
            "names_of_attributes": [
                "variable_1_attribute_1_name", "variable_1_attribute_2_name"],
            "variable_1_attribute_1_name": {
                "data_type": variable_1_attribute_1_data_type,
                "value": variable_1_attribute_1_value},
            "variable_1_attribute_2_name": {
                "data_type": variable_1_attribute_2_data_type,
                "value": variable_1_attribute_2_value}},
        "variable_2_name" : {
            "dimensions": [list of dimension names],
            "data_type": variable_2_data_type,
            "values": [numpy array of suitable size/shape and data type],
            "names_of_attributes": [
                "variable_2_attribute_1_name", "variable_2_attribute_2_name"],
            "variable_2_attribute_1_name": {
                "data_type": variable_2_attribute_1_data_type,
                "value": variable_2_attribute_1_value},
             "variable_2_attribute_2_name": {
                 "data_type": variable_2_attribute_2_data_type,
                 "value": variable_2_attribute_2_value}}}}
````
The python lists _names_of_global_attributes_, _names_of_dimensions_, and _names_of_variables_ in the top-level dictionary indicate the order in which global attributes, variables, and dimensions have been read from (or should be written to) a netCDF file. Similarly, each variable contains a _names_of_attributes_ list.

Each attribute, whether global or for a variable, has a data_type (see permissible data types section below) and a value.

Each variable additionally has values. These are stored in a numpy array of an appropriate size and shape (determined by its _dimensions_) and _data_type_. Entries for these three 'features' - i.e. values, dimensions, and data_type - occur alongside those for the variable's attributes. However, their contents require one level less of nesting since they only have values.
* Note the use of the plural word _values_ used for the variable 'feature' rather then the singular word _value_ used for an attribute. This reflects the fact that variables typically have multiple values whereas attributes typically have just the one. However, as can be seen from the example template file, there are exceptions to both of these generalisations.
* _dimensions_ is a python list of names of the variable's dimension variables. The lengths of these are available through the top-level dictionary _dimensions_.
* _data_type_ as a variable 'feature' is described in the same way as the _data_type_ for an attribute - see permissible data types section below.

## Permissible data types
The data object module currently only supports the data types that may be used for the netCDF3/classic standard. They are referenced (in both template files and data objects) using a string that closely resembles the corresponding numpy data type (left-hand column of the table below) rather than the netCDF data type (central column). A template error will be raised if an attempt is made to use any other data type.

Template | netCDF | Description
---------|--------|------------
str | CHAR | string, including unicode characters - see below
int8 | BYTE | 8 bit signed integer
int16 | SHORT | 16 bit signed integer
int32 | INT | 32 bit signed integer
float32 | FLOAT | 32 bit floating point
float64 | DOUBLE | 64 bit floating point

In the case of _int8_, _int16_, and _int32_ attributes, no check is made to ensure that the corresponding value falls within permissible limits.

NetCDF files allow the use of unicode characters within _str_ attribute values. In fact, the netCDF4 python interface (which the module uses) returns _str_ values as unicode, irrespective of whether or not they need to be. Unicode characters may only be included in a template file in the form of a symbol, e.g. a degrees symbol should be included as ° rather than as a python code of u"\u00B0". The example template file also makes use of Greek characters such as θ, ω, and φ.

## Template file syntax
This and the following section should be read with reference to the example template file. The template files are written using YAML syntax. This uses a mixture of indentations and context-specific special characters in order to denote structure. If the special characters are found outside of their expected context, the YAML parser will typically interpret them as ordinary characters. Entries that require the same level of nesting within a data object structure are written with the same level of indentation within a template file. The more deeply that an entry needs to be nested within a data object, the larger its level of indentation. The example template file uses an increase of 2 spaces per level of nesting, although this length is arbitrary. Empty lines can be used for visual formatting and will not affect the implied structure.

Symbol | Meaning
-------|--------
# | indicates that everything that follows on the line is a comment and will be ignored by the YAML parser.
: | a colon (followed by one or more white spaces) separates a key: value pair. These are referred to as 'mappings' in YAML-speak and correspond to dictionary entries in python. The value part will typically appear on the same line, unless it is a 'literal' or 'folded' entry as described below. In some cases, the value part of the pair corresponds to a nested dictionary or list, rather than to a single value. In such cases, the dictionary/list entries begin on the following line with an additional level of indentation.
\| | this indicates that the (string rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'literal' style, i.e. with line breaks being preserved (it is not necessary to include a "\n" at the end of each line). In the template files, this construction is used for defining multi-line (global or variable) attribute values. If any of the lines uses more indentation than the first line, the additional white spaces are interpreted as being part of the value. This can be used to create paragraph indentations (albeit not on the first line) or to align equations - see e.g. global attribute comment_horizontal_wind in the example template file. A parsing error will occur if any lines uses less indentation than the first line.
\> | this indicates that the (string rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'folded' style, i.e. collapsed into a single line by replacing line breaks with single spaces. Since line breaks are recommended for improving the readability of verbose metadata entries in netCDF files, it is not anticipated that this option will be used often if at all.
\- | a hyphen (followed by one or more white spaces) indicates that the following entry belongs to a 'sequence' (in YAML-speak) or list (in python-speak). Such entries are used in the template files wherever order is important, i.e. for the names of (both global and variable) attributes and for the names of variables.
\[ \] | where the value part of a key: value pair is series of comma-separated elements enclosed within square brackets, those elements are interpreted as belonging to a list or a one-dimensional array. In the template files, this construction is mainly used for specifying a variable's dimensions (an empty pair of square brackets should be used to indicate that the variable has no dimensions). It can also be used for specifying the values of a coordinate variable (i.e. a variable whose single dimension has the same name as the variable - see e.g. variables latitude and longitude in the example template file) or of a scalar variable (i.e. a variable which has no dimensions and only a single value). It can also be used for specifying the value of an attribute such as flag_values, which has multiple values rather than a single one - see, for example, variable tropopause_sharpness in the example template file.
" " | where the value part of a key: value pair is enclosed within inverted commas, the value is interpreted as having a string data type. This construction is only needed where the YAML parser would otherwise interpret the value differently, e.g. where the units attribute of a variable (which must be interpreted as a string) has a value of "1". This would otherwise be interpreted as an integer. Another example is where the value begins with an opening curly bracket { in order to indicate a string substitution field. See, for example, global attribute observation_start_time in the example template file. The YAML parser would otherwise interpret this as indicating the beginning of a mapping/dictionary entry.
\{ \} | in wider YAML syntax, curly brackets are used to enclose key: value pairs for a 'mapping'/dictionary. However, in the context of template files, their use is reserved to indicate string substitution fields - see template substitution fields section below. If an opening bracket occurs at the beginning of an entry, the whole entry must be enclosed within inverted commas (see above) in order to ensure that the YAML parser interprets it appropriately.

