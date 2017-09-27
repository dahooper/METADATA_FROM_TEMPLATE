# METADATA_FROM_TEMPLATE
A web-based version of this documentation is available at http://mst.nerc.ac.uk/data/module_data_object.html .

This page provides documentation for David Hooper's module_data_object.py python software, which can be used to:

* Create data objects, populated with metadata, from template files that allow substitutions - see example template file named module_data_object_example_template.yaml
* Write such data objects to netCDF files
* Extract data objects from netCDF files

The template files are written using YAML syntax - http://yaml.org/spec/1.2/spec.html - , which is easier to write than the Common Data form Language (CDL) used by the netCDF ncgen/ncdump software. The contents of the page are as follows:

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

Each attribute, whether global or for a variable, has a _data_type_ (see Permissible Data Types section below) and a _value_.

Each variable additionally has _values_. These are stored in a numpy array of an appropriate size and shape (determined by its _dimensions_) and _data_type_. Entries for these three 'features' - i.e. _values_, _dimensions_, and _data_type_ - occur alongside those for the variable's attributes. However, their contents require one level less of nesting since they only have values.
* Note the use of the plural word _values_ used for the variable 'feature' rather then the singular word _value_ used for an attribute. This reflects the fact that variables typically have multiple values whereas attributes typically have just the one. However, as can be seen from the example template file, there are exceptions to both of these generalisations.
* _dimensions_ is a python list of names of the variable's dimension variables. The lengths of these are available through the top-level dictionary _dimensions_.
* _data_type_ as a variable 'feature' is described in the same way as the _data_type_ for an attribute - see Permissible Data Types section below.

## Permissible data types
The data object module currently only supports the data types that may be used for the netCDF3/classic standard. They are referenced (in both template files and data objects) using a string that closely resembles the corresponding numpy data type (left-hand column of the table below) rather than the netCDF data type (central column). A template error will be raised if an attempt is made to use any other data type.

Template | netCDF | Description
---------|--------|------------
_str_ | CHAR | string, including unicode characters - see below
_int8_ | BYTE | 8 bit signed integer
_int16_ | SHORT | 16 bit signed integer
_int32_ | INT | 32 bit signed integer
_float32_ | FLOAT | 32 bit floating point
_float64_ | DOUBLE | 64 bit floating point

In the case of _int8_, _int16_, and _int32_ attributes, no check is made to ensure that the corresponding value falls within permissible limits.

NetCDF files allow the use of unicode characters within _str_ attribute values. In fact, the netCDF4 python interface (which the module uses) returns _str_ values as unicode, irrespective of whether or not they need to be. Unicode characters may only be included in a template file in the form of a symbol, e.g. a degrees symbol should be included as ° rather than as a python code of u"\u00B0". The example template file also makes use of Greek characters such as θ, ω, and φ.

## Template file syntax
This and the following section should be read with reference to the example template file. The template files are written using YAML syntax - http://yaml.org/spec/1.2/spec.html . This uses a mixture of indentations and context-specific special characters in order to denote structure. If the special characters are found outside of their expected context, the YAML parser will typically interpret them as ordinary characters. Entries that require the same level of nesting within a data object structure are written with the same level of indentation within a template file. The more deeply that an entry needs to be nested within a data object, the larger its level of indentation. The example template file uses an increase of 2 spaces per level of nesting, although this length is arbitrary. Empty lines can be used for visual formatting and will not affect the implied structure.

Symbol | Meaning
-------|--------
# | indicates that everything that follows on the line is a comment and will be ignored by the YAML parser.
: | a colon (followed by one or more white spaces) separates a key: value pair. These are referred to as 'mappings' in YAML-speak and correspond to dictionary entries in python. The value part will typically appear on the same line, unless it is a 'literal' or 'folded' entry as described below. In some cases, the value part of the pair corresponds to a nested dictionary or list, rather than to a single value. In such cases, the dictionary/list entries begin on the following line with an additional level of indentation.
\| | this indicates that the (string rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'literal' style, i.e. with line breaks being preserved (it is not necessary to include a "\n" at the end of each line). In the template files, this construction is used for defining multi-line (global or variable) attribute values. If any of the lines uses more indentation than the first line, the additional white spaces are interpreted as being part of the value. This can be used to create paragraph indentations (albeit not on the first line) or to align equations - see e.g. global attribute _comment_horizontal_wind_ in the example template file. A parsing error will occur if any lines uses less indentation than the first line.
\> | this indicates that the (string rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'folded' style, i.e. collapsed into a single line by replacing line breaks with single spaces. Since line breaks are recommended for improving the readability of verbose metadata entries in netCDF files, it is not anticipated that this option will be used often if at all.
\- | a hyphen (followed by one or more white spaces) indicates that the following entry belongs to a 'sequence' (in YAML-speak) or list (in python-speak). Such entries are used in the template files wherever order is important, i.e. for the names of (both global and variable) attributes and for the names of variables.
\[ \] | where the value part of a key: value pair is series of comma-separated elements enclosed within square brackets, those elements are interpreted as belonging to a list or a one-dimensional array. In the template files, this construction is mainly used for specifying a variable's _dimensions_ (an empty pair of square brackets should be used to indicate that the variable has no dimensions). It can also be used for specifying the _values_ of a coordinate variable (i.e. a variable whose single dimension has the same name as the variable - see e.g. variables _latitude_ and _longitude_ in the example template file) or of a scalar variable (i.e. a variable which has no dimensions and only a single value). It can also be used for specifying the _value_ of an attribute such as _flag_values_, which has multiple values rather than a single one - see, for example, variable _tropopause_sharpness_ in the example template file.
" " | where the value part of a key: value pair is enclosed within inverted commas, the value is interpreted as having a string data type. This construction is only needed where the YAML parser would otherwise interpret the value differently, e.g. where the _units_ attribute of a variable (which must be interpreted as a string) has a value of _"1"_. This would otherwise be interpreted as an integer. Another example is where the value begins with an opening curly bracket \{ in order to indicate a string substitution field. See, for example, global attribute _observation_start_time_ in the example template file. The YAML parser would otherwise interpret this as indicating the beginning of a mapping/dictionary entry.
\{ \} | in wider YAML syntax, curly brackets are used to enclose key: value pairs for a 'mapping'/dictionary. However, in the context of template files, their use is reserved to indicate string substitution fields - see Template Substitution Fields section below. If an opening bracket occurs at the beginning of an entry, the whole entry must be enclosed within inverted commas (see above) in order to ensure that the YAML parser interprets it appropriately.

## Template file structure
This section should be read with reference to the example template file. A generalised example is shown below.
````
data_object_type: data_object_type_id

global_attributes:
- global_attribute_1_name:
    data_type: global_attribute_1_data_type    
    value: global_attribute_1_value
- global_attribute_2_name:
    data_type: global_attribute_2_data_type
    value: global_attribute_2_value

variables:
- variable_1_name:
    - dimensions: [list of dimension names]
    - data_type: variable_1_data_type
    - variable_1_attribute_1_name:
        data_type: variable_1_attribute_1_data_type      
        value: variable_1_attribute_1_value  
    - variable_1_attribute_2_name:
        data_type: variable_1_attribute_2_data_type
        value: variable_1_attribute_2_value
- variable_2_name:
    - dimensions: [list of dimension names]
    - data_type: variable_2_data_type
    - variable_2_attribute_1_name:
        data_type: variable_2_attribute_1_data_type
        value: variable_2_attribute_1_value
    - variable_2_attribute_2_name:
        data_type: variable_2_attribute_2_data_type
        value: variable_2_attribute_2_value
````
        
A template file must have 3 entries at its top level: _data_object_type_, _global_attributes_, and _variables_. Each one acts as the key in a key: value pair. They can appear in any order (and so are not preceded by a hyphen), they must have zero indentation, and they must be followed (without any intervening white spaces) by a colon. The style of the value in the key: value pair depends on the key.
* The value of _data_object_type_ should appear on the same line as its key, separated by one or more white spaces (after the colon :). It must be a string that uniquely identifies the data object type from the perspective of the Creator class (which can store template details for several data object types simultaneously). It may be composed of characters in the ranges "a-z" and "A-Z" and may use underscores "_" and hyphens "-", but no whitespaces.
* The value of _global_attributes_ must be a nested list of global attribute names. Each of these begins on a new line, has no (explicit) indentation, is preceded by a hyphen - (which adds an implicit level of indentation) and one or more white spaces, and is followed (with no intervening white spaces) by a colon : but no other characters.
  * Each global attribute name acts as the key in a key: value pair, whose value will be a nested dictionary containing keys _data_type_ and _value_. These can appear in either order. Each one begins on a new line, shares the same level of indentation (which must be greater than that used for the global attribute name), and is followed (with no intervening white spaces) by a colon ":" and one or more white spaces.
    * The value of _data_type_ must be one of the permissible data types and should be given on the same line as the key.
    * The value of _value_ is the value of the global attribute. It must be written in a way that is consistent with the specified _data_type_. For example, if the specified data_type is _float32_ or _float64_, the value must be written including a decimal point (e.g. _4.0_ rather than _4_), but for _int8_, _int16_, or _int32_, the value may not include one. If the specified _data_type_ is _str_, but the value only consists of digits, it must be enclosed within inverted commas in order to be interpreted correctly. Multi-line _str_ values should be written in 'literal' style - seen template file syntax section above.
* The value of _variables_ must be a nested list of variable names. Each of these begins on a new line, has no explicit indentation, is preceded by a hyphen - and one or more white spaces, and is followed (with no intervening white spaces) by a colon : but no other characters.
  * Each variable name acts as the key in a key: value pair, whose value will be a nested list whose entries are the names of its attributes and of its 'features', i.e. _dimensions_, _data_type_, and _values_. Each one begins on a new line, shares the same level of indentation (which must be greater than that used for the variable name), is preceded by a hyphen - and one or more white spaces, and is followed (with no intervening white spaces) by a colon :. Each 'feature' name acts as the key in a key: value pair, whose value follows on the same line after one or more white spaces. The order in which they are included is arbitrary (despite the fact that they belong to a list). The order in which attributes are defined determines the order in which they will appear when written to a netCDF file.
    * The value of _dimensions_ must be a comma-separated list of dimension names enclosed within square brackets, _[ ]_. If the variable has no dimensions, an empty set of square brackets must be used.
    * The value of _data_type_ must be one of the permissible data types.
    * The value of _values_ must be a comma-separated list of values within square brackets. This 'feature' may only be defined in the case of a dimension variable (i.e. a variable whose single dimension has the same name as the variable) - see variables _latitude_ and _longitude_ in the example template file - or of a scalar variable (i.e. a variable which has no dimensions and only a single value). Consequently, in most cases, the values feature is not specified.
  * Each attribute name acts as the key in a key: value pair, whose value will be a nested dictionary containing keys _data_type_ and _value_. Consequently, variable attributes are teated in an identical way to global attributes - see above - except that they have an additional level of indentation.

## Template substitution fields
Substitutions may only be made into the _value_ of a global or variable attribute. If the corresponding _data_type_ is numerical - i.e. anything other than str - the substitution field is indicated by a substitution key immediately preceded (i.e. with no intervening white spaces) by a dollar symbol, _$_. See e.g. global attribute _observation_year_ in the example template file. It's definition is given as follows:
````
data_type: int16
value: $observation_year
````
Substitution keys, whether they are for str or numerical attributes, may be composed of any characters except whitespaces. The leading _$_ in the case of a numerical attribute is simply an indicator and not not part of the substitution key. Although the substitution key is the same as the global attribute name in this case, it does not have to be.

If the attribute's _data_type_ is _str_, the _value_ may contain multiple substitution fields. Each one is represented by the following syntax, which is used by the python str.format() method and Formatter class: _{substitution_key[:format_specification]}_. The curly brackets are part of the syntax whereas the the square brackets, which indicate an optional format specification, are not. The colon separating the format specification from the substitution key is part of the syntax. There should be no white spaces between substitution key and the colon and any white spaces following the colon will be interpreted as part of the format specification. The format specification may be omitted where the value associated with the substitution key is a string or if you are happy for python to format a numerical value as it sees fit, i.e. using the minimum number of digits necessary. For example, if the value of the substitution key is given as 3.1416 and no format specification is given, it will be formatted as _3.1416_ (although the number of decimal places might be truncated if more are specified for the value). Alternatively a format specification, such as _4.2f_ can be supplied, which will lead to the value being formatted as _3.14_. Note that the format specification should not be preceded by a % as it would be in a print _"%4.2f" % substitution_key_ python construction. Refer to the python documentation on common string operations for more details of format specifications.

The format specification is particularly useful where the substitution key corresponds to a python date or datetime object. For example, the units attribute of variable time in the example template file is defined as follows: 
````
data_type: str
value: seconds since {observation_date:%Y-%m-%d} 00:00:00 +00:00
````
If the _value_ of a _str_ attribute begins with a substitution field, the whole value must be enclosed within inverted commas. Refer to the template file syntax section above and to global attribute _observation_start_time_ in the example template file.

Note that the value of substitution key _observation_year_ at the beginning of this section is the same as the value of _observation_date.year_ in the example immediately above. Nevertheless, the construction _{observation_date:%Y}_ may not be used in the first example since it is expecting a numerical rather than a str value. Similarly, the _$substitution_key_ construction may not be used for a _str_ attribute.

## Template requirements
Templates that do not conform to a number of expectations will be rejected by the Creator class. The major ones are as follows.
* _attributes_, both global and variable.
  * The _value_ must be written in a way that is consistent with its data_type. For example, if the specified data_type is _float32_ or _float64_, the value must be written including a decimal point (e.g. _4.0_ rather than _4_), but for _int8_, _int16_, or _int32_, the value may not include one. If the specified data_type is _str_, but the value only consists of digits, it must be enclosed within inverted commas in order to be interpreted correctly.
* _global_attributes_
  * Entries must be included for _str_ data type global attributes _Conventions_ and _title_. The values may be empty strings, i.e. indicated by _""_. However, the whole point of requiring their inclusion is that they represent minimal requirements for making the associated data object self-describing. Consequently it is recommended that useful values are specified.
  * When a data object is written to a netCDF file, if a _history_ global attribute has been specified, a new entry will be added to it with the following format (beginning on a new line):
  ````
  %Y-%m-%dT%H:%M:%S - netcdf file created on computer computer_name
  ````
  The Creator class derives the current (UTC) datetime and name of the computer itself and so there is no need to supply them. An empty value of _""_ has been specified in the example template file as a way of fixing its position in the order of global attributes. If no _history_ is specified, a new global attribute will be added to the end of the existing list of global attributes.
* variables
  * Each variable must include _data_type_ and _dimensions_ 'features'. The _values_ 'feature' is optional and may only be included in the case of a coordinate variable (i.e. a variable whose single dimension has the same name as the variable, such as _latitude_ and _longitude_ in the example template file) or of a scalar variable (i.e. a variable which has no dimensions and only a single value).
  * Each variable must include either a _standard_name_ or _long_name_ (_data_type: str_) attribute. Both may be included. In cases where of standard_name is included, no attempt is made to ensure that its _value_ is valid.
  * Each variable must include a _units_ (_data_type: str_) attribute. Where a standard_name attribute is available, use should be made of its canonical units (or an accepted variation). No attempt is made to check that the value is correct. A value of _"1"_ - see e.g. variable _tropopause_sharpness_ in the example template file - must be enclosed within inverted commas in order to ensure that it is not interpreted as an integer.
  * If a _missing_value_ attribute is specified for a variable, it must be of the same _data_type_ as the variable. An additional attribute __FillValue_ will automatically be created with the same value. Although use of the __FillValue_ attribute is deprecated, the netCDF recommendations suggest that it should be included for backwards compatability. Moreover, when an "empty" data object is created, the variable's values array will be filled with the value of _missing_value_ rather than with zeros. There are no examples of the use of the _missing_value_ attribute in the example template file.
  
The Creator class will produce error messages to indicate any reasons for a template failing conformity tests. Appropriate changes will need to be made before the template can be used. If the template file fails being parsed by the YAML interpreter, use the method _test_parse_a_template_, which is described in the Creator class methods section below.

The Creator class has a method _show_requirements_for_template(data_object_type)_ for displaying the names of the dimensions for which lengths must be supplied and of the substitution keys for which values must be supplied. In the example template file, values have specified for coordinate variables _latitude_ and _longitude_. Consequently it is only necessary to provide lengths for the _time_ and _altitude_ dimensions. A suitable dictionary for supplying these would look like the following (where the lengths are likely to vary on a case by case basis).
````
lengths_of_dimensions= {
    "time": 280,    
    "altitude": 130}
````
A suitable dictionary for supplying substitution values would look like the following.
````
substitutions = {
    "observation_date: datetime.datetime(2017,8,1),
    "observation_year": 2017,
    "observation_month": 8,
    "observation_day": 1,
    "observation_start_time": datetime.datetime(2017,8,1,0,3,53),
    "observation_end_time": datetime.datetime(2017,8,1,23,57,3),
    "observation_range_resolution_string": "300",
    "observation_range_resolution_number": 2,
    "observation_bottom_range_gate_number": 18,
    "observation_top_range_gate_number": 147,
    "processing_nominal_smoothing_period_minutes": 33}
````

## Creator class methods
Once an instance of the Creator class has been initialised by:
````python
import module_data_objectcreator = module_data_object.Creator()
````
the following methods are available.

````python
data_object_type = creator.load_a_template(template_file_path)
````
This method loads a data object template from the file whose location is given by _template_file_path_. If the template passes all conformity checks, the value of _data_object_type_ will be a string (defined in the template file) that uniquely identifies the data object type. If any error is encountered, the value of data_object_type will be an empty string.
````python
creator.test_parse_a_template(template_file_path)
````
If the Creator class's error messages indicate that a YAML parsing error has occurred, you will need to use the _test_parse_a_template_ method in order to see the parser's error messages, which are normally suppressed. These messages include the line number of the template file on which the first error occurs. This method will need to be used repeatedly until all YAML errors have been removed (watch out for tabs being used instead of spaces for indentations). Once this method indicates that no errors have been encountered, you will need to revert to the _load_a_template_ method in order to be able to make use of the template.
````python
creator.show_templates_available()
````
The Creator class is designed to be able to make use of several data object templates simultaneously. This method shows a list of of _data_object_type_ values for all templates that have been loaded.
````python
creator.show_details_for_template(data_object_type)
````
This method shows the contents of a data object template as it has been interpreted by the Creator class. It's main purpose is to check that the template has been interpreted appropriately. Substitution fields are highlighted with bold text.
````
creator.show_requirements_for_template(data_object_type)
````
This method shows a list, for the specified data object type, of the dimensions for which lengths must be supplied of the substitution keys for which values must be supplied. In the case of the latter, the method shows the data types of attribute values for which the substitutions are intended.
````python
data_object = creator.create_from_template(data_object_type,lengths_of_dimensions,substitutions)
````
This method returns an "empty" data object from a template, i.e. one containing all of the appropriate metadata but with variable values arrays populated with zeros (or with the value of attribute missing_value, if it has been specified). An empty dictionary will be returned if either the dictionary _lengths_of_dimensions_ does not contain entries for all of the required dimensions or dictionary _substitutions_ does not contain entries for all of the required substitutions. The programmer must populate the variable values arrays with actual data before the data object is written to a netCDF file as described in the basic usage section above.

## Software dependencies
_module_data_object.py_ is designed for use within a python 2.7 environment and relies on the following modules. All of these are available on the CEDA jasmin platform.
* PyYAML (imported as yaml)
* netcdf4-python (imported as netCDF4)
* numpy
* datetime
* os
* platform
* string
