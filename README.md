# Documentation for David A. Hooper's module_data_object python software for handling scientific metadata

This python software has been made openly available (under the GNU
General Public License) in support of the [National Centre for
Atmospheric Science (NCAS)](https://www.ncas.ac.uk/en/) data
project. The aim of the software is to separate the descriptive task of
defining/composing metadata - following the [Climate and Forecast (CF)
metadata conventions](http://cfconventions.org/) - from the technical
tasks of processing data and writing them to a netCDF file. This makes
it very easy to modify the metadata – even adding and removing entire
fields - without having to make changes to the processing
software. The software allows you to:

* Extract the contents of a netCDF file in the form of a python
  dictionary based "data object"
* Create an "empty" data object from a template file that allows
  substitution fields. This data object will contain all of the
  necessary metadata. The arrays for its variable values will be of
  the appropriate size, shape, and data type, but will need to be
  populated with actual data.
* Write a data object to a netCDF file.

The template files are written using [YAML syntax](<http://yaml.org/spec/1.2/spec.html>), which is more straight-forward than the 
Common Data form Language (CDL) used by the netCDF ncgen/ncdump
software. [An example template file has been included with the software](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml).

This documentation covers the following topics:

* [Software dependencies](#software_dependencies)
* [Usage](#usage)
* [Data object structure](#data_object_structure)
* [Permissible data types](#data_types)
* [Template file syntax](#template_syntax)
* [Template file structure](#template_structure)
* [Template file substitution fields](#template_substitution)
* [Template file requirements](#template_requirements)

<a name="software_dependencies">

## Software dependencies

The *module_data_object* software is designed for use within a python
2.7 environment and relies on the following modules. All of these are
available on the [Centre for Environmental Data Analysis (CEDA) JASMIN
platform](http://www.jasmin.ac.uk/).

* PyYAML (imported as yaml)
* netcdf4-python (imported as netCDF4)
* numpy
* datetime
* os
* platform
* string

<a name="usage">

## Usage
The *module_data_object* module provides the following methods:

<dl>
  <dt>module_data_object.<b>extract_from_netcdf_file</b>(<em>path</em>)</dt>
  <dd>Returns a [data object in the form of a python
  dictionary](#data_object_structure) that
  contains the contents of the netCDF file whose path is given by
  <em>path</em>. It returns an empty dictionary, i.e. {}, if <em>path</em> does
  not correspond to a netCDF file.<br><br></dd>

  <dt>module_data_object.<b>write_to_netcdf_file</b>(<em>data_object,
  path[, automatically_update_history]</em>)</dt>
  <dd>Returns an exit code of 0 if the [data
  object](#data_object_structure) <em>data_object</em> is successfully
  written to a netCDF file whose path is given by
  <em>path</em>. Otherwise it returns an exit code of 1. If the value
  of optional input argument <em>automatically_update_history</em> is
  set to <em>True</em> (its default value is <em>False</em>), the
  <em>history</em> global attribute of the netCDF file will be
  automatically updated with the UTC date/time of creation and the
  name of the computer on which this was done in the format <em>"File
  created YYYY-MM-DD HH:MM:SS +00:00 on computer
  computer-name"</em>. The computer name is automatically read from
  the operating system.  If the data object does not contain a
  <em>history</em> global attribute, one will be added. Note that the
  [example data object template
  file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
  contains an empty <em>history</em> global attribute as a way of
  defining its order amongst the other global attributes. Otherwise
  it will be added to the end of the list. </dd> </dl>

The module also provides a class for creating "empty"
<em>data_objects</em>. These contain all of the necessary
metadata. The arrays for its variable values will be of the
appropriate size, shape, and [data type](#data_types), but
will need to be populated by actual data.

<dl>
  <dt><em>class</em> module_data_object.<b>Creator</b>(<em>[verbosity_level]</em>)</dt>
  <dd>The optional input argument <em>verbosity_level</em> has a
  default value of 1. Changing this to 2 or 3 will increase the amount
  of information shown when instance methods are called. Changing it
  to 0 will prevent error and warning messages from being
  shown.<br>

  <b>Creator</b> objects have the following public methods:

  <dl>
    <dt><b>load_a_template</b>(<em>path</em>)</dt>
    <dd>returns the data object type, i.e. a unique identifying
    string that is defined within the template file
    (<em>nerc-mstrf-radar-mst_st_cardinal_v4-0</em> in the case of the
    [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)), if the template loads
    successfully from the file whose path is given by
    <em>path</em>. An empty string, i.e. "", is returned if it does
    not load successfully. More than one template can be loaded by a
    single <b>Creator</b> object.<br><br></dd>
    <dt><b>show_templates_available</b>()</dt>
    <dd>shows the data object types (and the names of the files that
    they were loaded from) for all templates that have been
    loaded.<br><br></dd> 
    <dt><b>show_details_for_template</b>(<em>data_object_type</em>)</dt>
    <dd>shows the details of a template whose data object type
    is given by <em>data_object_type</em>. This method is intended to
    check that the yaml-based template has been interpreted
    correctly. Substitution fields are highlighted in bold
    text. <br><br></dd> 
    <dt><b>show_requirements_for_template</b>(<em>data_object_type</em>)</dt>
    <dd>shows the substitution fields and dimension lengths that must
    be supplied in order to generate a data object from the template
    of type <em>data_object_type</em>. The keys for the substitution
    fields are shown together with their expected [data
    types](#data_types). <br><br></dd>
    <dt><b>create_from_template</b>(<em>data_object_type, lengths_of_dimensions[, substitutions, add_fill_value]</em>)</dt>
    <dd>returns an "empty" data object based on the template of type
    <em>data_object_type</em>. This contains all of the appropriate
    metadata, but the values arrays for variables will either be
    filled with zeros or with a missing datum value if either a
    <em>missing_value</em> or <em>\_FillValue</em> attribute has been
    specified for it. A python dictionary
    <em>lengths_of_dimensions</em> whose keys are the names of
    coordinate variables and whose values are the required lengths must
    be submitted as an input argument. Unlimited dimensions are not
    currently permitted. Coordinate variables that have a single value
    defined in the template file, e.g. <em>latitude</em> and
    <em>longitude</em> in the [example template
    file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml),
    do not need to be included. If any substitution fields have been
    included within the template, a python dictionary
    <em>substitutions</em> must be submitted as an optional input
    argument. Its keys must be those used to indicate substitution
    fields in the template file - [see substitution field section for
    more details](#template_substitution) - and its values must be
    those that will be substituted into the template. If the value of
    optional input argument <em>add_fill_value</em> is set to
    <em>True</em> (its default value is <em>False</em>), a
    <em>\_FillValue</em> variable attribute will automatically be
    duplicated for any variable that has a <em>missing_value</em>
    attribute defined. </dd>

  </dl></dd> 
</dl>

The following code shows how the module can be used to create
a netCDF file from the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml).

````python
import module_data_object
creator = module_data_object.Creator()
#
data_object_type = creator.load_a_template("module_data_object_example_template.yaml")
#
lengths_of_dimensions= {
    "time": 280,
    "altitude": 130}
#
substitutions = {
    "observation_date": datetime.datetime(2017,8,1),
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
#
data_object = creator.create_from_template(data_object_type,lengths_of_dimensions,substitutions)
#
# The "values" array for each variable must now be populated with the 
# required data. These arrays can be accessed by
#
# for variable_name in data_object["names_of_variables"]
#    data_object["variables"][variable_name]["values"]
#
exit_code = module_data_object.write_to_netcdf_file(data_object,"example_netcdf_file.nc")
````

<a name="data_object_structure">

## Data object structure 

The data objects used by this module emulate the structure of a netCDF
file in a series of nested python dictionaries and lists. The best way
to understand this is to extract a data object from a netCDF file
using the
module_data_object.<b>extract_from_netcdf_file</b>(<em>path</em>)
method described in the [usage section above](#usage). A generalised,
example of a data object is shown below.

````
data_object = {
    "names_of_global_attributes": [
        "global_attribute_1_name", "global_attribute_2_name"],
    "global_attributes": {
        "global_attribute_1_name": {
            "data_type": global_attribute_1_data_type,
            "value": global_attribute_1_value},
        "global_attribute_2_name": {
            "data_type": global_attribute_2_data_type,
            "value": global_attribute_2_value}},
    "names_of_dimensions": [
        "dimension_variable_1_name", "dimension_variable_2_name"],
    "dimensions": {
        "dimension_variable_1_name": length_of_dimension_variable_1,
        "dimension_variable_2_name": length_of_dimension_variable_2},
    "names_of_variables": [
        "variable_1_name", "variable_2_name"],
    "variables": {
        "variable_1_name" : {
            "dimensions": [list of relevant coordinate variable names],
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
            "dimensions": [list of relevant coordinate variable names],
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

The values corresponding to the 3 dictionary keys
<em>names_of_global_attributes</em>, <em>names_of_dimensions</em>, and
<em>names_of_variables</em> at the top level of the data object are
python lists. These are primarily used to record the order in which
global attributes, dimensions, and variables have been read from or
should be written to a netCDF file. They can also be useful for
navigating the data object. The values corresponding to the 3
dictionary keys <em>global_attributes</em>, <em>dimensions</em>, and
<em>variables</em> at the top level of the data object are lower-level
dictionaries. 

The keys in the <em>data_object["global_attributes"]</em> dictionary
correspond to the names of the global attributes. The values are lower-level
dictionaries, each of which contains a <em>data_type</em> key, whose
value corresponds to its [data type](#data_types), and a
<em>value</em> key, whose value corresponds to the value of the global
attribute. The latter can be accessed as
<em>data_object["global_attributes"][global_attribute_name]["value"]</em>.

The keys in the <em>data_object["dimensions"]</em> dictionary
correspond to the names of coordinate variables. The values are the
lengths of those coordinate variables. 

The keys in the <em>data_object["variables"]</em> dictionary
correspond to the names of the variables. The values are lower-level
dictionaries each of which
contains at least 4 keys. The value corresponding to the
<em>values</em> key is a numpy array. The size/shape of the array is
represented by the <em>dimensions</em> key, whose value is a python
list of the relevant coordinate variable names in the appropriate
order. The [data type](#data_types) of the array is represented by the
value of the <em>data_type</em> key. The value corresponding to the
<em>names_of_attributes</em> key is a python dictionary, which records
the order in which variable attributes have been read from or should
be written to a netCDF file. It is analogous to the
<em>names_of_global_attributes</em> entry in the top level of the data
object. The values of the variable can be accessed as
<em>data_object["variables"][variable_name]["values"]</em>.  

There is an additional key in each
<em>data_object["variables"][variable_name]</em> dictionary
corresponding to the name of each variable attribute. Its value is a
lower-level dictionary, which contains a <em>data_type</em> key, whose
value corresponds to its [data type](#data_types), and a
<em>value</em> key, whose value corresponds to the value of the
attribute. The latter can be access as
<em>data_object["variables"][variable_name][attribute_name]["value"]</em>.
Note that the variable attribute dictionaries are analogous to the
global attribute dictionaries, but nested at a deeper level in the
data object. Also note that the values of variable attributes are
nested one level deeper than the values of the variable. Finally, note
use of the plural word <em>values</em> for a variable's data array
contrasting with use of the singular word *value* for a global or
variable attribute.

<a name="data_types">

## Permissible data types

In keeping with the [CF metadata
conventions](http://cfconventions.org/), this software only allows you
to use data types that are available to netCDF3 files (new files are
created in the netCDF 3 'classic' mode, albeit through the netCDF4
interface). They are referenced (in both
template files and data objects) using a string that closely resembles
the corresponding numpy data type (see the left-hand column of the table
below) rather than the netCDF data type names (central column). A template
error will be raised if an attempt is made to use any other data type.

Template | netCDF | Description
---------|--------|------------
<em>str</em> | CHAR | string, including unicode characters - see below
<em>int8</em> | BYTE | 8 bit signed integer
<em>int16</em> | SHORT | 16 bit signed integer
<em>int32</em> | INT | 32 bit signed integer
<em>float32</em> | FLOAT | 32 bit floating point number
<em>float64</em> | DOUBLE | 64 bit floating point number

In the case of <em>int8</em>, <em>int16</em>, and <em>int32</em>
attributes, no check is made to ensure that the corresponding value
falls within permissible limits.

NetCDF files allow the use of unicode characters within <em>str</em>
attribute values. In fact, the netCDF4 python interface (which the
module uses) returns <em>str</em> values as unicode, irrespective of whether
or not they need to be. Unicode characters may only be included in a
template file in the form of a symbol, e.g. a degrees symbol should be
represented as ° rather than as a python code of u"\u00B0". The 
[example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
also makes use of Greek characters such as θ, ω, and φ.

<a name="template_syntax">

## Template file syntax
This and the following section should be read with reference to the
[example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml),
which is written using [YAML
syntax](<http://yaml.org/spec/1.2/spec.html>). This relies on a
mixture of indentations and context-specific special characters in
order to denote structure. If the special characters are found outside
of their expected context, the YAML parser will typically interpret
them as ordinary characters. Entries that require the same level of
nesting within a data object structure are written with the same level
of indentation within a template file. The more deeply that an entry
needs to be nested within a data object, the larger its level of
indentation. The [example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
uses an increase of 2 spaces per level of nesting, although this
length is arbitrary. Empty lines can be used for visual formatting and
will not affect the implied structure.

Symbol | Meaning 
-------|---------
# | indicates that everything that follows on the line is a comment and will be ignored by the YAML parser.
\: | a colon (followed by one or more white spaces) separates a key: value pair. These are referred to as 'mappings' in YAML-speak and correspond to dictionary entries in python. The value part will typically appear on the same line, unless it is a 'literal' or 'folded' entry as described below. In some cases, the value part of the pair corresponds to a nested dictionary or list, rather than to a single value. In such cases, the dictionary/list entries begin on the following line with an additional level of indentation.
\| | this indicates that the (<em>str</em> rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'literal' style, i.e. with line breaks being preserved (it is not necessary to include a "\\n" at the end of each line). In the template files, this construction is used for defining multi-line (global or variable) attribute values. If any of the lines uses more indentation than the first line, the additional white spaces are interpreted as being part of the value. This can be used to create paragraph indentations (albeit not on the first line) or to align equations - see e.g. global attribute <em>comment_horizontal_wind</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml). A parsing error will occur if any line uses less indentation than the first line. 
\> | this indicates that the (<em>str</em> rather than numerical) value component of a key: value pair begins on the following line (with an additional level of indentation) and that it should be interpreted in the 'folded' style, i.e. collapsed into a single line by replacing line breaks with single spaces. Since line breaks are recommended for improving the readability of verbose metadata entries in netCDF files, it is not anticipated that this option will be used often if at all.
\- | a hyphen (followed by one or more white spaces) indicates that the following entry belongs to a 'sequence' (in YAML-speak) or list (in python-speak). Such entries are used in the template files wherever order is important, i.e. for the names of (both global and variable) attributes and for the names of variables. 
\[ \] | where the value part of a key: value pair is series of comma-separated elements enclosed within square brackets, those elements are interpreted as belonging to a list or a one-dimensional array. In the template files, this construction is mainly used for specifying a variable's _dimensions_ (an empty pair of square brackets should be used to indicate that the variable has no dimensions). It can also be used for specifying the _values_ of a coordinate variable (i.e. a variable whose single dimension has the same name as the variable - see e.g. variables <em>latitude</em> and <em>longitude</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)) or of a scalar variable (i.e. a variable which has no dimensions and only a single value). It can also be used for specifying the <em>value</em> of an attribute such as <em>flag_values</em>, which has multiple values rather than a single one - see, for example, variable <em>tropopause_sharpness</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml). 
" " | where the value part of a key: value pair is enclosed within inverted commas, the value is interpreted as having a <em>str</em> data type. This construction is only needed where the YAML parser would otherwise interpret the value differently, e.g. where the <em>units</em> attribute of a variable (which must be interpreted as a string) has a value of <em>"1"</em>. This would otherwise be interpreted as an integer. Another example is where the value begins with an opening curly bracket \{ in order to indicate a string substitution field. See, for example, global attribute <em>observation_start_time</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml). The YAML parser would otherwise interpret this as indicating the beginning of a mapping/dictionary entry.
\{ \} | in wider YAML syntax, curly brackets are used to enclose key: value pairs for a 'mapping'/dictionary. However, in the context of template files, their use is reserved to indicate <em>str</em> [substitution fields](#template_substitution). If an opening bracket occurs at the beginning of an entry, the whole entry must be enclosed within inverted commas (see above) in order to ensure that the YAML parser interprets it appropriately.

<a name="template_structure">

## Template file structure

This section should be read with reference to the [example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
and to the [syntax section above](#template_syntax). A
generalised example is shown below. 

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
    - dimensions: [list of relevant coordinate variable names]
    - data_type: variable_1_data_type
    - variable_1_attribute_1_name:
        data_type: variable_1_attribute_1_data_type
        value: variable_1_attribute_1_value
    - variable_1_attribute_2_name:
        data_type: variable_1_attribute_2_data_type
        value: variable_1_attribute_2_value
- variable_2_name:
    - dimensions: [list of relevant coordinate variable names]
    - data_type: variable_2_data_type
    - variable_2_attribute_1_name:
        data_type: variable_2_attribute_1_data_type
        value: variable_2_attribute_1_value
    - variable_2_attribute_2_name:
        data_type: variable_2_attribute_2_data_type
        value: variable_2_attribute_2_value
````

A template file must have 3 entries at its top level:
<em>data_object_type</em>, <em>global_attributes</em>, and
<em>variables</em>. Each one acts as the key in a key: value
pair. They can appear in any order (and so are not preceded by a
hyphen), they must have zero indentation, and they must be followed
(without any intervening white spaces) by a colon. The style of the
value in the key: value pair depends on the key.

* The value of <em>data_object_type</em>
(<em>nerc-mstrf-radar-mst_st_cardinal_v4-0</em> in the [example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)) should appear on the same line as
its key, separated by one or more white spaces (after the colon). It
must be a string that uniquely identifies the data object type from
the perspective of the Creator class (which can store template details
for several data object types simultaneously). It may be composed of
characters in the ranges "a-z" and "A-Z" and may use underscores "_"
and hyphens "-", but no whitespaces.

* The value of <em>global_attributes</em> must be a nested list of
global attribute names. Each of these begins on a new line, has no
(explicit) indentation, is preceded by a hyphen (which adds an
implicit level of indentation) and one or more white spaces, and is
followed (with no intervening white spaces) by a colon but no other
characters.

  * Each global attribute name acts as the key in a key: value pair,
  whose value will be a nested dictionary containing keys
  <em>data_type</em> and <em>value</em>. These can appear in either
  order. Each one begins on a new line, shares the same level of
  indentation (which must be greater than that used for the global
  attribute name), and is followed (with no intervening white spaces)
  by a colon and one or more white spaces.

    * The value of <em>data_type</em> must be one of the [permissible
      data types](#data_types) and should be given on the same line as
      the key.

    * The value of <em>value</em> is the value of the global attribute. It
      must be written in a way that is consistent with the specified
      <em>data_type</em>. For example, if the specified data type is
      <em>float32</em> or <em>float64</em>, the value must be written
      including a decimal point (e.g. <em>4.0</em> rather than
      <em>4</em>), but for <em>int8</em>, <em>int16</em>, or
      <em>int32</em>, the value may not include one. Numerical values
      should be written on the same line as the key. If the specified
      data type is <em>str</em>, but the value only consists of 
      digits, it must be enclosed within inverted commas in order to
      be interpreted correctly. Multi-line <em>str</em> values should be
      written in 'literal' style - see [template file syntax section
      above](#template_syntax) - i.e. starting with a "|" on the same
      line as the key and with the text starting on the following line
      with an increased level of indentation. 

* The value of <em>variables</em> must be a nested list of variable
  names. Each of these begins on a new line, has no explicit
  indentation, is preceded by a hyphen and one or more white spaces,
  and is followed (with no intervening white spaces) by a colon but
  no other characters.

  * Each variable name acts as the key in a key: value pair, whose
    value will be a nested list whose entries are the names of its
    attributes and of its 'features', i.e. <em>dimensions</em>,
    <em>data_type</em>, and <em>values</em>. Each one begins on a new
    line, shares the same level of indentation (which must be greater
    than that used for the variable name), is preceded by a hyphen and
    one or more white spaces, and is followed (with no intervening
    white spaces) by a colon. Each 'feature' name acts as the key in a
    key: value pair, whose value follows on the same line after one or
    more white spaces. The order in which they are included is
    arbitrary (despite the fact that they belong to a list). The order
    in which attributes are defined determines the order in which they
    will appear when written to a netCDF file.

    * The value of <em>dimensions</em> must be a comma-separated list of
      coordinate variable names enclosed within square brackets, <em>[
      ]</em>. If the variable has no dimensions, an empty set of
      square brackets must be used.

    * The value of <em>data_type</em> must be one of the [permissible
      data types](#data_types).

    * The value of <em>values</em> must be a comma-separated list of
      values within square brackets. This 'feature' may only be
      defined in the case of a coordinate variable (i.e. a variable
      whose single dimension has the same name as the variable) - see
      variables <em>latitude</em> and <em>longitude</em> in the
      [example template
      file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
      - or of a scalar variable (i.e. a variable which has no
      dimensions and only a single value). Consequently, in most
      cases, the <em>values</em> feature is not specified.

  * Each attribute name acts as the key in a key: value pair, whose
    value will be a nested dictionary containing keys <em>data_type</em> and
    <em>value</em>. Consequently, variable attributes are treated in an
    identical way to global attributes - see above - except that they
    have an additional level of indentation.


<a name="template_substitution">

## Template substitution fields
Substitutions may only be made into the <em>value</em> of a global or
variable attribute. If the corresponding <em>data_type</em> is numerical -
i.e. anything other than <em>str</em> - the substitution field is indicated by
a substitution key immediately preceded (i.e. with no intervening
white spaces) by a dollar symbol, <em>$</em>. See e.g. global attribute
<em>observation_year</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml). It's definition is
given as follows:

````
data_type: int16
value: $observation_year
````

Substitution keys, whether they are for <em>str</em> or numerical attributes,
may be composed of any characters except whitespaces. The leading <em>$</em>
in the case of a numerical attribute is simply an indicator and not
not part of the substitution key. Although the substitution key is the
same as the global attribute name in this case, it does not have to
be.

If the attribute's <em>data_type</em> is <em>str</em>, the
<em>value</em> may contain 
multiple substitution fields. Each one is represented by the following
syntax, which is used by the python str.format() method and Formatter
class:
````
{substitution_key[:format_specification]}
````

The curly brackets are part of the syntax whereas the the square
brackets, which indicate an optional format specification, are
not. The colon separating the format specification from the
substitution key is part of the syntax. There should be no white
spaces between substitution key and the colon and any white spaces
following the colon will be interpreted as part of the format
specification. The format specification may be omitted where the value
associated with the substitution key is a string or if you are happy
for python to format a numerical value as it sees fit, i.e. using the
minimum number of digits necessary. For example, if the value of the
substitution key is given as 3.1416 and no format specification is
given, it will be formatted as <em>3.1416</em> (although the number of
decimal places might be truncated if more are specified for the
value). Alternatively a format specification, such as <em>4.2f</em>
can be supplied, which will lead to the value being formatted as
<em>3.14</em>. Note that the format specification should not be
preceded by a % as it would be in a print <em>"%4.2f" %
value</em> python construction. Refer to the python
documentation on common string operations for more details of format
specifications.

The format specification is particularly useful where the substitution
key corresponds to a python date or datetime object. For example, the
<em>units</em> attribute of variable <em>time</em> in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml) is
defined as follows: 

````
data_type: str
value: seconds since {observation_date:%Y-%m-%d} 00:00:00 +00:00
````

If the <em>value</em> of a <em>str</em> attribute begins with a
substitution field, the whole value must be enclosed within inverted
commas. Refer to the [template file syntax section
above](#template_syntax) and to global attribute
<em>observation_start_time</em> in the [example template
file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml).

Note that the value of substitution key <em>observation_year</em> at the
beginning of this section is the same as the value of
<em>observation_date.year</em> in the example immediately
above. Nevertheless, the construction <em>{observation_date:%Y}</em> may not
be used in the first example since it is expecting a numerical rather
than a str value. Similarly, the <em>$substitution_key</em> construction may
not be used for a <em>str</em> attribute.

<a name="template_requirements">

## Template requirements
Templates that do not conform to a number of expectations will be
rejected by the Creator class. The major ones are as follows.

* <em>attributes</em>, both global and variable.

  * The <em>value</em> must be written in a way that is consistent
    with its data_type. For example, if the specified data_type is
    <em>float32</em> or <em>float64</em>, the value must be written
    including a decimal point (e.g. <em>4.0</em> rather than
    <em>4</em>), but for <em>int8</em>, <em>int16</em>, or
    <em>int32</em>, the value may not include one. If the specified
    data_type is <em>str</em>, but the value only consists of digits, it must
    be enclosed within inverted commas in order to be interpreted
    correctly.

* <em>global_attributes</em>

  * Entries must be included for <em>str</em> data type global attributes
    <em>Conventions</em> and <em>title</em>. The values may be empty strings,
    i.e. indicated by <em>""</em>. However, the whole point of requiring
    their inclusion is that they represent minimal requirements for
    making the associated data object self-describing. Consequently it
    is recommended that useful values are specified.

* variables

  * Each variable must include <em>data_type</em> and
    </em>dimensions</em>. The <em>values</em> 'feature' is optional
    and may only be included in the case of a coordinate variable
    (i.e. a variable whose single dimension has the same name as the
    variable, such as <em>latitude</em> and <em>longitude</em> in the
    [example template
    file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml))
    or of a scalar variable (i.e. a variable which has no dimensions
    and only a single value).

  * Each variable must include either a <em>standard_name</em> or
    <em>long_name</em> <em>str</em> attribute. Both may be
    included. In cases where of standard_name is included, no attempt
    is made to ensure that its <em>value</em> is valid.

  * Each variable must include a <em>units</em> <em>str</em>
    attribute. Where a <em>standard_name</em> attribute is available,
    use should be made of its canonical units or an accepted
    alternative form. No attempt is made to check that the value is
    correct. A value of <em>"1"</em> - see e.g. variable
    </em>tropopause_sharpness</em> in the [example template
    file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml)
    - must be enclosed within inverted commas in order to ensure that
    it is not interpreted as an integer.

  * If a <em>missing_value</em> attribute is specified for a variable, it
    must be of the same _data_type_ as the variable. An additional
    attribute <em>\_FillValue</em> will automatically be created with the same
    value. Although use of the <em>\_FillValue</em> attribute is deprecated,
    the netCDF recommendations suggest that it should be included for
    backwards compatibility. Moreover, when an "empty" data object is
    created, the variable's values array will be filled with the value
    of <em>missing_value</em> rather than with zeros. There are no examples
    of the use of the <em>missing_value</em> attribute in the [example template file](https://github.com/dahooper/metadata-from-template/blob/master/module_data_object_example_template.yaml).
  
The Creator class will produce error messages to indicate any reasons
for a template failing conformity tests. Appropriate changes will need
to be made before the template can be used. 