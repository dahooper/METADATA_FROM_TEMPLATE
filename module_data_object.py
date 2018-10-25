# module_data_object.py
#
# Last updated 2018/10/25
#
# David Hooper's module for
# 
# 1) extracting data objects from netCDF files
# 2) creating data objects from templates 
# 3) writing data objects to netCDF files
#
# For documentation, refer to 
# https://github.com/dahooper/metadata-from-template/blob/master/README.md
#
# Changes to the code since 2017/09/18 version
# 
# Changed behaviour of function extract_from_netcdf_file().
# The previous version used to automtically return the values array for a
# variable as a masked array if any instance of _FillValue occured within it;
# this is the default behaviour of the underlying netCDF4 module. This
# behaviour can now be switched off by setting the value of optional input
# argument prevent_masked_arrays to False. 
#
# Changed behaviour of function write_to_netcdf_file().
# This used to automatically add an entry to the history global attribute
# (creating the attribute if it was not already defined) to state when
# and on which computer the netCDF file had been created. Now the value of
# optional input argument automatically_update_history must be set to True
# in order for this to happen. 
#
# Fixed code error in function
#   Creator.check_template_for_dimensions_and_substitutions(). 
# This caused the software to crash if a template contained a string
# substitution field in a variable attribute value. This problem was not
# encountered for global attributes. It was fixed by the following code change
#     substitution_name = attribute_value[1:]
#  -> substitution_name = attribute["value"][1:]
#
# Fixed code error in function Creator.load_a_template()
# A call was made
#   show_dimensions_and_substitutions_for_template(
#       self.variables["templates_file-name"][-1])
#  Firstly, the function had been renamed and secondly, the input argument 
#  was invalid. This section of code has now been changed to
#   show_requirements_for_template(
#       self.variables["templates_data-object-type"][-1])
#
# Fixed code error in function Creator.return_substituted_attribute_value.
#   changed 
#     attribute_value = data_type_object(
#         self.variables["substitutions"][attribute_name]
#   to 
#     substitution_key = attribute["value"][1:]
#     attribute_value = data_type_object(
#         self.variables["substitutions"][substitution_key])
#
# Fixed code errror in function Creator.create_from_template, which caused
# a crash if a numerical substitution was made into a 'missing_value' attribute
# for a variable. This was fixed by delaying the routine until after all
# variable attribute values (with substitutions where necessary) have been
# assigned to the data object. At the same time, a change was made so that
# the value of '_FillValue' (where provided) is used to pre-allocate the
# variable values array. Previously this was only done if a 'missing_value'
# attribute was supplied.
#
import datetime, netCDF4, numpy, os, platform, string, yaml
#
#########
#
# Internal function used by both the Creator class and the
# write_to_netcdf_file() main function. It returns a data type object for an
# input data type string.
#
def return_data_type_object(data_type):
    if data_type == "int8":
        data_type_object = numpy.int8
    elif data_type == "int16":
        data_type_object = numpy.int16
    elif data_type == "int32":
        data_type_object = numpy.int32
    elif data_type == "float32":
        data_type_object = numpy.float32
    elif data_type == "float64":
        data_type_object = numpy.float64
    else:
        data_type_object = ()
        print "ERROR: %s.return_data_type_object()" % __file__
        print "  unrecognised input data type"

    return data_type_object
#
######################################
#
# Class for creating data objects from one or more templates. The verbosity
# level is an optional input argument. The default value of 1 causes error
# and warning messages to be shown. A value of 0 means that no messages are
# shown. If a level of greater than 1 is used, the required dimensions
# and substitution keys for a template will be shown as soon as it is
# loaded. 
#
class Creator():
    def __init__(self,verbosity_level=1):
        self.variables = {
            "verbosity_level": verbosity_level,
            "permissible_data_types": [
                "str", "int8", "int16", "int32", "float32", "float64"],
            "permissible_imported_str_data_types": [str, unicode],
            "required_global_attributes": ["Conventions", "title"],
            "required_variable_features": ["data_type", "dimensions"],
            "names_of_variable_features": [
                "data_type", "dimensions", "values"],
            "required_variable_attributes": ["units", "standard_or_long_name"],
            "no_template_errors_have_been_encountered": True,
            "no_creation_errors_have_been_encountered": True,
            "templates_file-name": [],
            "templates_data-object-type": [],
            "templates_names-of-dimensions": [],
            "templates_names-of-unspecified-dimensions": [],
            "templates_lengths-of-specified-dimensions": [],
            "templates_substitution-keys": [],
            "templates_substitution-data-types": []}

        self.objects = {
            "templates": [],
            "string_formatter": string.Formatter()}
#
#########
#
# Internal function to register a template error
#
    def register_a_template_error(self,error_message):
        self.variables["no_template_errors_have_been_encountered"] = False
        if self.variables["verbosity_level"] > 0:
            print "ERROR: %s() in template file %s" % (
                self.__class__,self.variables["templates_file-name"][-1])
            print "  %s" % error_message
#
#########
#
# Internal function to register a data object creation error
#
    def register_a_creation_error(self,error_message):
        self.variables["no_creation_errors_have_been_encounteredl"] = False
        if self.variables["verbosity_level"] > 0:
            print "ERROR: %s() in creating a data object" % self.__class__
            print "  %s" % error_message
#
#########
#
# Internal function to show a warning message
#
    def show_a_warning(self,warning_message):
        if self.variables["verbosity_level"] > 0:
            print "WARNING: %s()" % self.__class__
            print "  %s" % warning_message
#
#########
#
# This function simply tests whether or not yaml is able to parse the template
# file. It does not load it in to a Creator object. It's intended purpose 
# is for debugging the yaml syntax errors. If no errors are shown, the
# template can be then be loaded using the 'load_a_template' function.    
#  
    def test_parse_a_template(self,template_file_path):
        if not os.path.isfile(template_file_path):
            self.show_a_warning("unable to test parse a template file since its path is invalid, %s" % template_file_path)
        else:
            print "Test parsing a template"
            test_parse = yaml.load(
                file(template_file_path,"r"),Loader=yaml.Loader)
            print "\nThe template has been parsed successfully"
#
#########
#
# Main function to load a template (from a yaml file) into the Creator object.
# If no errors have been encountered, the function returns the data object type
# identifier string, which is given in the template file. Otherwise it
# returns an empty string, i.e. ""
#
    def load_a_template(self,template_file_path):
        self.variables["no_template_errors_have_been_encountered"] = True
        self.variables["templates_file-name"].append("unknown")

        if not os.path.isfile(template_file_path):
            self.register_a_template_error("invalid template file path")
        else:
            self.variables["templates_file-name"][-1] = os.path.basename(
                template_file_path)
            try:
                self.objects["templates"].append(
                    yaml.load(file(template_file_path,"r"),
                              Loader=yaml.Loader))    
            except:
                self.register_a_template_error(
                    "template file fails yaml parsing")
                del self.variables["templates_file-name"][-1]                
            else:
                self.variables["templates_data-object-type"].append("")
                self.variables["templates_substitution-keys"].append([])
                self.variables["templates_substitution-data-types"].append([])
                self.variables["templates_names-of-dimensions"].append([])
                self.variables["templates_names-of-unspecified-dimensions"].append([])
                self.variables["templates_lengths-of-specified-dimensions"].append({})
                self.check_template_for_conformity()

                if self.variables["no_template_errors_have_been_encountered"]:
                    self.check_template_for_dimensions_and_substitutions()
                    if self.variables["verbosity_level"] > 1:
                        self.show_requirements_for_template(
                            self.variables["templates_data-object-type"][-1])
                else:
                    del self.variables["templates_data-object-type"][-1]
                    del self.variables["templates_substitution-keys"][-1]
                    del self.variables["templates_substitution-data-types"][-1]
                    del self.variables["templates_names-of-dimensions"][-1]
                    del self.variables["templates_names-of-unspecified-dimensions"][-1]
                    del self.variables["templates_lengths-of-specified-dimensions"][-1]

        if self.variables["no_template_errors_have_been_encountered"]:
            return self.variables["templates_data-object-type"][-1]
        else:
            return ""
#
#########
#
# Internal function for checking whether the template conforms to the expected
# structure.
#
    def check_template_for_conformity(self):
        global_attributes_are_available = False
        variables_are_available = False
        names_of_global_attributes = []
        names_of_variables = []

        if type(self.objects["templates"][-1]) != dict:
            self.register_a_template_error("template does not consist of a dictionary at the top level")
        else:
            if "global_attributes" not in self.objects["templates"][-1]:
                self.register_a_template_error("no 'global_attributes' entry has been found at the top level")
            elif (type(self.objects["templates"][-1]["global_attributes"]) 
                  != list):

                self.register_a_template_error("the contents of 'global_attributes' is not given as a list")
            else:
                global_attributes_are_available = True

            if "variables" not in self.objects["templates"][-1]:
                self.register_a_template_error("no 'variables' entry has been found at the top level")
            elif type(self.objects["templates"][-1]["variables"]) != list:
                self.register_a_template_error("the contents of 'variables' is not given as a list")
            else:
                variables_are_available = True

            if "data_object_type" not in self.objects["templates"][-1]:
                self.register_a_template_error("no 'data_object_type' entry has been found at the top level")
            elif type(self.objects["templates"][-1]["data_object_type"]) != str:
                self.register_a_template_error("the value of 'data_object_type' is not a string as expected")
            else:
                data_object_type = \
                    self.objects["templates"][-1]["data_object_type"]
                if data_object_type in self.variables["templates_data-object-type"]:
                    self.register_a_template_error("a template has already been loaded for data object type '%s'" % data_object_type)
                else:
                    self.variables["templates_data-object-type"][-1] = \
                        data_object_type

        if global_attributes_are_available:
            number_of_global_attributes = len(
                self.objects["templates"][-1]["global_attributes"])
            global_attributes_index = 0
            while global_attributes_index < number_of_global_attributes:
                if type(self.objects["templates"][-1]["global_attributes"][global_attributes_index]) != dict:
                    self.register_a_template_error("global attribute %i does not consist of a dictionary at the top level" % global_attributes_index)
                else:
                    global_attribute_keys = self.objects["templates"][-1][
                        "global_attributes"][global_attributes_index].keys()
                    if len(global_attribute_keys) != 1:
                        self.register_a_template_error("global attribute %i does not have only 1 key (i.e. its name)" % global_attributes_index)
                    else:
                        global_attribute_name = global_attribute_keys[0]
                        if global_attribute_name in names_of_global_attributes:
                            self.register_a_template_error("global attribute '%s' has been defined more than once" % global_attribute_name)
                        else:
                            names_of_global_attributes.append(
                                global_attribute_name)

                        global_attribute = self.objects["templates"][-1]["global_attributes"][global_attributes_index][global_attribute_name]
                        self.check_attribute_for_conformity(
                            "global",global_attribute_name,global_attribute)

                global_attributes_index += 1
#
        if variables_are_available:
            number_of_variables = len(
                self.objects["templates"][-1]["variables"])
            variables_index = 0
            while variables_index < number_of_variables:
                if type(self.objects["templates"][-1]["variables"][variables_index]) != dict:
                    self.register_a_template_error("variable %i does not consist of a dictionary at the top level" % variables_index)
                else:
                    variable_keys = self.objects["templates"][-1][
                        "variables"][variables_index].keys()
                    if len(variable_keys) != 1:
                        self.register_a_template_error("variable %i does not have only 1 key (i.e. its name)" % variables_index)
                    else:
                        variable_name = variable_keys[0]

                        if variable_name in names_of_variables:
                            self.register_a_template_error("variable '%s' has been defined more than once" % variable_name)
                        else:
                            names_of_variables.append(variable_name)

                        variable = self.objects["templates"][-1]["variables"][
                            variables_index][variable_name]
                        self.check_variable_for_conformity(
                            variable_name,variable)

                variables_index += 1
#
#########
#
# Internal sub-function of check_template_for_conformity, which checks whether
# a (global or variable) attribute portion of a template conforms to the
# expected structure. 
# 
    def check_attribute_for_conformity(
        self,attribute_parent_name,attribute_name,attribute):

        if attribute_parent_name == "global":
            attribute_description = "global attribute '%s'" % attribute_name
        else:
            attribute_description = "variable '%s' attribute '%s'" % (
                attribute_parent_name,attribute_name)

        self.variables["data_type_is_available_for_attribute"] = False

        if type(attribute) != dict:
            self.register_a_template_error(
                "%s is not defined as a dictionary" % attribute_description)
        else:
            number_of_attribute_elements = len(attribute)
            if "data_type" not in attribute:
                self.register_a_template_error(
                    "no data type has been defined for %s" % 
                    attribute_description)
            else:
                number_of_attribute_elements -= 1

                if type(attribute["data_type"]) != str:
                    self.register_a_template_error(
                        "data type for %s is not a string as expected" %
                        attribute_description)
                elif attribute["data_type"] not in self.variables[
                    "permissible_data_types"]:

                    self.register_a_template_error(
                        "data type '%s' for %s is not permissible" % 
                        (attribute["data_type"], attribute_description))
                else:
                    self.variables[
                        "data_type_is_available_for_attribute"] = True
#
            if "value" not in attribute:
                self.register_a_template_error(
                    "no value has been defined for %s" % attribute_description)
            else:
                number_of_attribute_elements -= 1
                imported_data_type = type(attribute["value"])
                if imported_data_type == dict: 
                    self.register_a_template_error("the value for %s has been given as a dictionary - it shold contain a value" % attribute_description)

                elif imported_data_type == list:
                    number_of_values = len(attribute["value"])
                    first_value_imported_data_type = type(attribute["value"][0])
                    values_index = 1
                    while values_index < number_of_values:
                        if type(attribute["value"][values_index]) != first_value_imported_data_type:
                            self.register_a_template_error("the values for %s are not all of the same data type" % attribute_description)

                        values_index +=1

                    if self.variables["data_type_is_available_for_attribute"]:
                        if first_value_imported_data_type == int:
                            if not attribute["data_type"].startswith("int"):
                                self.register_a_template_error("value for %s is not consistent with defined data type" % attribute_description)
                    
                        elif first_value_imported_data_type == float:
                            if not attribute["data_type"].startswith("float"):
                                self.register_a_template_error("value for %s is not consistent with defined data type" % attribute_description)
                        else:
                            self.register_a_template_error("value for %s is an invalid data type" % attribute_description)                         

                elif self.variables["data_type_is_available_for_attribute"]:
                    if imported_data_type in self.variables[
                        "permissible_imported_str_data_types"]:

                        if ((attribute["data_type"] != "str") and
                            not(attribute["value"].startswith("$"))):

                            self.register_a_template_error("value for %s is not consistent with a numerical data type" % attribute_description)

                    elif imported_data_type == int:
                        if not attribute["data_type"].startswith("int"):
                            self.register_a_template_error("value for %s is not consistent with defined data type" % attribute_description)
                    
                    elif imported_data_type == float:
                        if not attribute["data_type"].startswith("float"):
                            self.register_a_template_error("value for %s is not consistent with defined data type" % attribute_description)
                    else:
                        self.register_a_template_error("value for %s is an invalid data type" % attribute_description)
#
            if number_of_attribute_elements != 0:
                self.register_a_template_error("%s has an invalid number of elements" % attribute_description)
#
#########
#
# Internal sub function of check_template_for_conformity, which checks whether
# a variable portion of a template conforms to the expected structure. 
#
    def check_variable_for_conformity(self,variable_name,variable):
        names_of_attributes = []
        attribute_is_not_available = {}
        for attribute_name in self.variables["required_variable_attributes"]:
            attribute_is_not_available[attribute_name] = True
        values_imported_data_type = ""
        number_of_values = -1
        number_of_dimensions = -1
        variable_data_type = ""
        missing_value_data_type = ""

        if type(variable) != list:
            self.register_a_template_error("variable '%s' is not defined as a list" % variable_name)
        else:
            number_of_properties = len(variable)
            property_index = 0
            while property_index < number_of_properties:
                if type(variable[property_index]) != dict:
                    self.register_a_template_error("property %i for variable '%s' is not defined as a dictionary" % variable_name)
                else:
                    attribute_keys = variable[property_index].keys()
                    if len(attribute_keys) != 1:
                        self.register_a_template_error("variable '%s' attribute %i does not have only 1 key (i.e. its name)" % (variable_name,property_index))
                    else:
                        attribute_name = attribute_keys[0]
                        attribute = variable[property_index][attribute_name]
                        attribute_imported_data_type = type(attribute)

                        if attribute_name in names_of_attributes:
                            self.register_a_template_error("attribute '%s' for variable '%s' has been defined more than once" % (attribute_name,variable_name))
                        else:
                            names_of_attributes.append(attribute_name)

                        if attribute_name == "dimensions":
                            if attribute_imported_data_type != list:
                                self.register_a_template_error("dimensions defined for variable '%s' are not given as a list" % variable_name)
                            else:
                                number_of_dimensions = len(attribute)
                                for dimension_name in attribute:
                                    if type(dimension_name) != str:
                                        self.register_a_template_error("a dimension name for variable '%s' is not a string" % variable_name)

                        elif attribute_name == "data_type":
                            if attribute_imported_data_type != str:
                                self.register_a_template_error("data type for variable '%s' is not consistent with a string" % variable_name)
                            elif attribute not in self.variables["permissible_data_types"]:
                                self.register_a_template_error("data type '%s' for variable '%s' is not permissible" % (attribute,variable_name))
                            else:
                                variable_data_type = attribute

                        elif attribute_name == "values":
                            if attribute_imported_data_type != list:
                                self.register_a_template_error("values for variable '%s' have not given as a list" % variable_name)
                            else:
                                number_of_values = len(attribute)
                                if number_of_values == 0:
                                    self.register_a_template_error("values for variable '%s' is an empty list" % variable_name)
                                else:
                                    first_value_imported_data_type = type(attribute[0])
                                    values_index = 1
                                    while values_index < number_of_values:
                                        if type(attribute[values_index]) != first_value_imported_data_type:
                                            self.register_a_template_error("the values for variable '%s' are not all of the same data type" % variable_name)

                                        values_index +=1

                                    if ((first_value_imported_data_type != float) and
                                        (first_value_imported_data_type != int)):

                                        self.register_a_template_error("values for variable '%s' are not of a numerical type" % variable_name)

                        else:
                            self.check_attribute_for_conformity(
                                variable_name,attribute_name,attribute)
                            if ((attribute_name == "missing_value") and
                                self.variables["data_type_is_available_for_attribute"]):
                                missing_value_data_type = attribute["data_type"]

                        if ((attribute_name == "standard_name") or
                            (attribute_name == "long_name")):

                            attribute_is_not_available["standard_or_long_name"] = False
                        elif attribute_name in self.variables["required_variable_attributes"]:
                            attribute_is_not_available[attribute_name] = False

                property_index += 1

            for attribute_name in attribute_is_not_available:
                if attribute_is_not_available[attribute_name]:
                    self.register_a_template_error("required attribute '%s' has not been defined for variable '%s'" % (attribute_name,variable_name))

            if variable_data_type != "":
                if values_imported_data_type == int:
                    if not variable_data_type.startswith("int"):
                        self.register_a_template_error("values for variable '%s' are not consistent with the defined data type" % variable_name)
                if values_imported_data_type == float:
                    if not variable_data_type.startswith("float"):
                        self.register_a_template_error("values for variable '%s' are not consistent with defined data type" % variable_name)

                if ((missing_value_data_type != "") and
                    (missing_value_data_type != variable_data_type)):

                    self.register_a_template_error("inconsistent data types for variable '%s' and its 'missing_value' attribute" % variable_name)

            if number_of_values > 0:
                if (number_of_dimensions == 0) and (number_of_values != 1):
                    self.register_a_template_error("dimensionless variable '%s' may have only 1 value" % variable_name)
                elif number_of_dimensions > 1:
                    self.register_a_template_error("variable '%s' has more than 1 dimension" % variable_name)
#
#########
#
# Internal function that returns the locations within a template that 
# relate to a variable, i.e. to its features and attributes
#
    def return_template_locations_for_variable(self,variable):
        template_locations = {
            "property_index_for_feature": {}, 
            "property_index_for_attribute": {},
            "names_of_attributes": []}
        number_of_properties = len(variable)
        property_index = 0
        while property_index < number_of_properties:
            property_name = variable[property_index].keys()[0]
            if property_name in self.variables["names_of_variable_features"]:
                template_locations["property_index_for_feature"][
                    property_name] = property_index
            else:
                template_locations["property_index_for_attribute"][
                    property_name] = property_index
                template_locations["names_of_attributes"].append(property_name)

            property_index += 1

        if "values" not in template_locations["property_index_for_feature"]:
            template_locations["property_index_for_feature"]["values"] = -1

        return template_locations
#
#########
#
# Internal function that checks a template in order to identify the
# dimensions and substitution keys. It checks that all dimensions have
# and associated dimension variable.
#
    def check_template_for_dimensions_and_substitutions(self):

        if self.variables["verbosity_level"] > 2:
            print "Checking template for dimensions and substitutions"
            print "  Global attributes"

        number_of_global_attributes = len(
            self.objects["templates"][-1]["global_attributes"])
        global_attributes_index = 0
        while global_attributes_index < number_of_global_attributes:
            global_attribute_name = self.objects["templates"][-1][
                "global_attributes"][global_attributes_index].keys()[0]
            global_attribute = self.objects["templates"][-1]["global_attributes"][global_attributes_index][global_attribute_name]

            if self.variables["verbosity_level"] > 2:
                print "    %s" % global_attribute_name

            if global_attribute["data_type"] == "str":
                if "$" in global_attribute["value"]:
                    self.show_a_warning("'$' based substitution cannot be used for a string value - see global attribute '%s'" % global_attribute_name)

                for text_fragment in self.objects["string_formatter"].parse(
                    global_attribute["value"]):

                    if ((text_fragment[1] != None) and 
                        (text_fragment[1] not in self.variables["templates_substitution-keys"][-1])):

                        self.variables["templates_substitution-keys"][-1].append(text_fragment[1])
                        self.variables["templates_substitution-data-types"][-1].append(global_attribute["data_type"])

            elif type(global_attribute["value"]) == str:
                substitution_key = global_attribute["value"][1:]
                if substitution_key not in self.variables[
                    "templates_substitution-keys"][-1]:

                    self.variables["templates_substitution-keys"][-1].append(substitution_key)
                    self.variables["templates_substitution-data-types"][-1].append(global_attribute["data_type"])

            global_attributes_index += 1
#
        if self.variables["verbosity_level"] > 2:
            print "  Variables"

        names_of_dimension_variables = []
        lengths_of_variables_with_values = {}
        number_of_variables = len(self.objects["templates"][-1]["variables"])
        variables_index = 0
        while variables_index < number_of_variables:
            variable_name = self.objects["templates"][-1]["variables"][
                variables_index].keys()[0]
            variable = self.objects["templates"][-1]["variables"][
                variables_index][variable_name]
            template_locations = self.return_template_locations_for_variable(
                variable)
            dimensions_property_index = \
                template_locations["property_index_for_feature"]["dimensions"]
            values_property_index = \
                template_locations["property_index_for_feature"]["values"]

            if self.variables["verbosity_level"] > 2:
                print "    %s" % variable_name

            number_of_dimensions = len(
                variable[dimensions_property_index]["dimensions"])
            if ((number_of_dimensions == 1) and
                (variable[dimensions_property_index]["dimensions"][0] == variable_name)):
                names_of_dimension_variables.append(variable_name)

            for dimension_name in variable[dimensions_property_index]["dimensions"]:
                if dimension_name not in self.variables["templates_names-of-dimensions"][-1]:
                    self.variables["templates_names-of-dimensions"][-1].append(dimension_name)

            if values_property_index != -1:
                lengths_of_variables_with_values[variable_name] = len(
                    variable[values_property_index]["values"])
                if not ((variable_name in names_of_dimension_variables) or
                        (number_of_dimensions == 0)):

                    self.register_a_template_error("cannot specify values for '%s' since it is neither a dimension variable nor a variable with no dimensions" % variable_name)

            for attribute_name in template_locations["names_of_attributes"]:
                property_index = template_locations[
                    "property_index_for_attribute"][attribute_name]
                attribute = variable[property_index][attribute_name]
                if attribute["data_type"] == "str":                    
                    if "$" in attribute["value"]:
                        self.show_a_warning("'$' based substitution cannot be used for a string value - see variable '%s' attribute '%s'" % (variable_name,attribute_name))

                    for text_fragment in self.objects["string_formatter"].parse(attribute["value"]):
                        if ((text_fragment[1] != None) and 
                            (text_fragment[1] not in self.variables["templates_substitution-keys"][-1])):

                            self.variables["templates_substitution-keys"][-1].append(text_fragment[1])
                            self.variables["templates_substitution-data-types"][-1].append(attribute["data_type"])

                elif type(attribute["value"]) == str:
                    substitution_name = attribute["value"][1:]
                    if substitution_name not in self.variables["templates_substitution-keys"][-1]:
                        self.variables["templates_substitution-keys"][-1].append(substitution_name)
                        self.variables["templates_substitution-data-types"][-1].append(attribute["data_type"])

            variables_index += 1
#
# Check that all dimension names correspond to dimension variable and compile
# a list of dimensions whose lengths have not been specified. 
#
        for dimension_name in self.variables["templates_names-of-dimensions"][-1]:
            if dimension_name not in names_of_dimension_variables:
                self.register_a_template_error("no variable has been defined for dimension '%s'" % dimension_name)

            if dimension_name in lengths_of_variables_with_values:
                self.variables["templates_lengths-of-specified-dimensions"][-1][dimension_name] = lengths_of_variables_with_values[dimension_name]

            else:
                self.variables["templates_names-of-unspecified-dimensions"][-1].append(dimension_name)
#
#########
#
# Function to show a list of templates available by their data object types and
# source file names. No input argument is required.
#
    def show_templates_available(self):
        print "\nTemplates available"
        number_of_templates = len(self.objects["templates"])
        templates_index = 0
        while templates_index < number_of_templates:
            print "  %s  [%s]" % (
                self.variables["templates_data-object-type"][templates_index],
                self.variables["templates_file-name"][templates_index])

            templates_index += 1
#
#########
#
# Function to show the details of a template, i.e. the names and data types
# and values of global attributes and variables. The appropriate data object
# type string (which is returned from the load_a_template function) must be
# supplied as input.
#
    def show_details_for_template(self,data_object_type):
        its_okay_to_continue = True
        if data_object_type not in self.variables["templates_data-object-type"]:
            its_okay_to_continue = False
            self.show_a_warning("there is no template for data object type %s" % data_object_type)
        else:
            templates_index = self.variables[
                "templates_data-object-type"].index(data_object_type)

        if its_okay_to_continue:
            print "Template of data object for data object type: %s\n" % data_object_type
            print "GLOBAL ATTRIBUTES"
            number_of_global_attributes = len(
                self.objects["templates"][templates_index]["global_attributes"])
            global_attributes_index = 0
            while global_attributes_index < number_of_global_attributes:
                global_attribute_name = self.objects["templates"][templates_index]["global_attributes"][global_attributes_index].keys()[0]
                global_attribute = self.objects["templates"][templates_index]["global_attributes"][global_attributes_index][global_attribute_name]

                formatted_attribute_value = self.return_formatted_attribute_value("global",global_attribute)

                print "- %s:" % global_attribute_name
                print "    data_type: %s" % global_attribute["data_type"]
                print "    value    : %s" % formatted_attribute_value
                print ""

                global_attributes_index += 1

            print "\nVARIABLES"
            number_of_variables = len(
                self.objects["templates"][templates_index]["variables"])
            variables_index = 0
            while variables_index < number_of_variables:
                variable_name = self.objects["templates"][templates_index][
                    "variables"][variables_index].keys()[0]
                variable = self.objects["templates"][templates_index]["variables"][variables_index][variable_name]
                template_locations = \
                    self.return_template_locations_for_variable(variable)

                data_type_property_index = template_locations[
                    "property_index_for_feature"]["data_type"]
                dimensions_property_index = template_locations[
                    "property_index_for_feature"]["dimensions"]
                values_property_index = template_locations[
                    "property_index_for_feature"]["values"]
                print "- %s%s" % (
                    variable_name,
                    variable[dimensions_property_index]["dimensions"])
                print "    data_type: %s" % variable[
                    data_type_property_index]["data_type"]
                if values_property_index > -1:
                    print "    values   : %s" % variable[
                        values_property_index]["values"]

                for attribute_name in template_locations["names_of_attributes"]:
                    property_index = template_locations[
                        "property_index_for_attribute"][attribute_name]
                    attribute = variable[property_index][attribute_name]

                    formatted_attribute_value = \
                        self.return_formatted_attribute_value("variable",attribute)

                    print "    %s:" % attribute_name
                    print "      data_type: %s" % attribute["data_type"]
                    print "      value    : %s" % formatted_attribute_value

                print ""
                variables_index += 1
#
#########
#
# Function to show the dimensions and substitution keys required for a
# particular template. The appropriate data object type string (which is
# returned from the load_a_template function) must be supplied as input.
#
    def show_requirements_for_template(self,data_object_type):
        its_okay_to_continue = True
        if data_object_type not in self.variables["templates_data-object-type"]:
            its_okay_to_continue = False
            self.show_a_warning("there is no template for data object type %s" % data_object_type)
        else:
            templates_index = self.variables[
                "templates_data-object-type"].index(data_object_type)

        if its_okay_to_continue:
            print "\nData object type: %s" % self.variables["templates_data-object-type"][templates_index]

            print "  Required substitutions:"
            number_of_substitutions = len(
                self.variables["templates_substitution-keys"][templates_index])
            substitutions_index = 0
            while substitutions_index < number_of_substitutions:
                print "  %7s - %s" % (
                    self.variables["templates_substitution-data-types"][
                        templates_index][substitutions_index],
                    self.variables["templates_substitution-keys"][
                        templates_index][substitutions_index])
                substitutions_index += 1

            print "\n  Required dimension lengths:"
            for dimension_name in self.variables[
                "templates_names-of-unspecified-dimensions"][templates_index]:

                print "    %s" % dimension_name
#
#########
#
# Internal function to return the value of an attribute after any necessary
# substitutions have been made.
# 
    def return_substituted_attribute_value(self,attribute_name,attribute):
        imported_value_data_type = type(attribute["value"])
        if imported_value_data_type in self.variables["permissible_imported_str_data_types"]:
            if attribute["data_type"] == "str":
                attribute_value_template = attribute["value"].rstrip()
                attribute_value = attribute_value_template.format(**self.variables["substitutions"])

            else:
                data_type_object = return_data_type_object(
                    attribute["data_type"])
                substitution_key = attribute["value"][1:]
                attribute_value = data_type_object(
                    self.variables["substitutions"][substitution_key])

        elif imported_value_data_type == list:
            data_type_object = return_data_type_object(attribute["data_type"])
            number_of_values = len(attribute["value"])
            attribute_value = numpy.zeros([number_of_values],data_type_object)
            values_index = 0
            while values_index < number_of_values:
                attribute_value[values_index] = attribute["value"][values_index]
                values_index += 1

        else:
            data_type_object = return_data_type_object(attribute["data_type"])
            attribute_value = data_type_object(attribute["value"])

        return attribute_value
#
#########
#
# Internal function to return the value of an attribute formatted for
# the self.show_details_for_template function. 
# 
    def return_formatted_attribute_value(self,attribute_type,attribute):
        if attribute_type == "global":
            indentation_string = "  " * 3
        else:
            indentation_string = "  " * 4

        if attribute["data_type"] == "str":
            formatted_lines = []
            unformatted_lines = attribute["value"].rstrip().splitlines()
            if len(unformatted_lines) > 1:
                value_contains_multiple_lines = True
                this_is_the_first_of_multiple_lines = True
            else:
                value_contains_multiple_lines = False
                this_is_the_first_of_multiple_lines = False
                
            for unformatted_line in unformatted_lines:
                formatted_line_elements = []
                if this_is_the_first_of_multiple_lines:
                    formatted_lines.append("|")
                    this_is_the_first_of_multiple_lines = False
                if value_contains_multiple_lines:
                    formatted_line_elements.append(indentation_string)
                    
                for unformatted_line_elements in self.objects["string_formatter"].parse(unformatted_line):
                    if unformatted_line_elements[0] != None:
                        formatted_line_elements.append(
                            unformatted_line_elements[0])
                    if unformatted_line_elements[1] != None:
                        formatted_line_elements.append("\033[1m{")
                        formatted_line_elements.append(
                            unformatted_line_elements[1])
                        formatted_line_elements.append(":")
                    if unformatted_line_elements[2] != None:
                        formatted_line_elements.append(
                            unformatted_line_elements[2])
                        formatted_line_elements.append("}\033[0m")

                formatted_lines.append("".join(formatted_line_elements))
    
            if attribute["value"] == "":
                formatted_attribute_value = '""'
            else:
                formatted_attribute_value = "\n".join(formatted_lines)

        elif type(attribute["value"]) == str:
            formatted_line_elements = [
                "\033[1m", attribute["value"], "\033[0m"]
            formatted_attribute_value = "".join(formatted_line_elements)
        else:
            formatted_attribute_value = "%s" % attribute["value"]

        return formatted_attribute_value
#
#########
#
# Main function of Creator class that returns an "empty" data object.
# A template must be loaded - using the load_a_template function - before 
# this can be used. The data object type string (of the template), a dictionary 
# containing the lengths of the required dimensions, and a dictionary
# containing the required template substitution values, must be supplied as
# input. The data object will be populated with all of the relevant
# metadata values after appropriate substitutions have been made. The 
# variable values arrays will be of the required shapes and sizes (defined
# by the specified lengths of the dimensions) and will be filled with zeros,
# unless a "missing_value" attribute has been defined. In the latter case,
# the variable values arrays will be populated with the missing datum value.
# This function will return an empty dictionary is any errors are 
# encountered.
# 
    def create_from_template(
            self,data_object_type,lengths_of_dimensions,substitutions={},add_fill_value=False):

        self.variables["no_creation_errors_have_been_encountered"] = True
        self.variables["substitutions"] = substitutions
        data_object = {}

        if data_object_type not in self.variables["templates_data-object-type"]:
            self.register_a_creation_error("there is no template for data object type %s" % data_object_type)
        else:
            templates_index = self.variables[
                "templates_data-object-type"].index(data_object_type)
            for dimension_name in self.variables["templates_names-of-unspecified-dimensions"][templates_index]:

                if dimension_name not in lengths_of_dimensions:
                    self.register_a_creation_error("length of dimension %s has not been specified" % dimension_name)

            for substitution_name in self.variables["templates_substitution-keys"][templates_index]:
                if substitution_name not in substitutions:
                    self.register_a_creation_error("substitution %s has not been specified" % substitution_name)
#
        if self.variables["no_creation_errors_have_been_encountered"]:
            data_object["names_of_global_attributes"] = []
            data_object["names_of_variables"] = []
            data_object["names_of_dimensions"] = []
            data_object["global_attributes"] = {}
            data_object["variables"] = {}
            data_object["dimensions"] = {}

            for dimension_name in self.variables[
                "templates_names-of-dimensions"][templates_index]:

                data_object["names_of_dimensions"].append(dimension_name)
                if dimension_name in lengths_of_dimensions:
                    data_object["dimensions"][dimension_name] = \
                        lengths_of_dimensions[dimension_name]
                else:
                    data_object["dimensions"][dimension_name] = self.variables["templates_lengths-of-specified-dimensions"][templates_index][dimension_name]
#
            number_of_global_attributes = len(self.objects["templates"][templates_index]["global_attributes"])
            global_attributes_index = 0
            while global_attributes_index < number_of_global_attributes:
                global_attribute_name = self.objects["templates"][templates_index]["global_attributes"][global_attributes_index].keys()[0]
                global_attribute = self.objects["templates"][templates_index]["global_attributes"][global_attributes_index][global_attribute_name]

                data_object["names_of_global_attributes"].append(
                    global_attribute_name)
                data_object["global_attributes"][global_attribute_name] = {
                    "data_type": global_attribute["data_type"], 
                    "value": self.return_substituted_attribute_value(global_attribute_name,global_attribute)}
                                    
                global_attributes_index += 1
#
            number_of_variables = len(
                self.objects["templates"][templates_index]["variables"])

            variables_index = 0
            while variables_index < number_of_variables:
                variable_name = self.objects["templates"][templates_index]["variables"][variables_index].keys()[0]
                variable = self.objects["templates"][templates_index]["variables"][variables_index][variable_name]
                
                template_locations = \
                    self.return_template_locations_for_variable(variable)
                data_type_property_index = template_locations[
                    "property_index_for_feature"]["data_type"]
                dimensions_property_index = template_locations[
                    "property_index_for_feature"]["dimensions"]
                values_property_index = template_locations[
                    "property_index_for_feature"]["values"]

                data_type_object = return_data_type_object(
                    variable[data_type_property_index]["data_type"])
                values_shape = []
                for dimension_name in variable[dimensions_property_index]["dimensions"]:
                    values_shape.append(data_object["dimensions"][dimension_name])
#
# Note that a variable without dimensions is expected to have only one value
#
                if values_shape == []:
                    values_shape = [1]

                data_object["names_of_variables"].append(variable_name)
                data_object["variables"][variable_name] = {
                    "data_type": variable[data_type_property_index]["data_type"],
                    "dimensions": variable[dimensions_property_index]["dimensions"],
                    "values": numpy.zeros(values_shape,data_type_object),
                    "names_of_attributes": []}

                for attribute_name in template_locations["names_of_attributes"]:
                    data_object["variables"][variable_name][
                        "names_of_attributes"].append(attribute_name)

                    property_index = template_locations[
                        "property_index_for_attribute"][attribute_name]
                    attribute = variable[property_index][attribute_name]

                    data_object["variables"][variable_name][attribute_name] = {
                        "data_type": attribute["data_type"],
                        "value": self.return_substituted_attribute_value(
                            attribute_name,attribute)}

                    if (add_fill_value and
                        (attribute_name == "missing_value") and 
                        ("_FillValue" not in template_locations["names_of_attributes"])):

                        data_object["variables"][variable_name]["names_of_attributes"].append("_FillValue")
                        data_object["variables"][variable_name]["_FillValue"] = {
                            "data_type": attribute["data_type"],
                            "value": self.return_substituted_attribute_value(attribute_name,attribute)}

                if values_property_index != -1:
                    values_index = 0
                    while values_index < len(variable[values_property_index]["values"]):
                        data_object["variables"][variable_name]["values"][values_index] = variable[values_property_index]["values"][values_index]
                        values_index += 1

                elif "missing_value" in data_object["variables"][variable_name]["names_of_attributes"]:

                    data_object["variables"][variable_name]["values"][:] = \
                        data_object["variables"][variable_name]["missing_value"]["value"]

                elif "_FillValue" in data_object["variables"][variable_name]["names_of_attributes"]:

                    data_object["variables"][variable_name]["values"][:] = \
                        data_object["variables"][variable_name]["_FillValue"]["value"]

                variables_index += 1

        return data_object
#
#################
#
# Internal sub function of extract_from_netcdf_file(). It returns the data
# type (string) from a value extracted from a netCDF file
#
def return_data_type_for_value(value):
    if type(value) == unicode:
        data_type = "str"
    else:
        data_type = str(value.dtype)

    return data_type
#
#######################
#
# Main function that extracts - and returns - a data object from a netCDF
# file. 
#
def extract_from_netcdf_file(
        netcdf_file_path,verbosity_level=1,prevent_masked_arrays=False):

    data_object = {}
    if not os.path.isfile(netcdf_file_path):
        if verbosity_level > 0:
            print "ERROR: %s.extract_from_netcdf_file()" % __file__
            print "  netcdf file path is invalid: %s" % netcdf_file_path
    else:
        if verbosity_level >= 2:
            print "Extracting contents from netcdf file %s" % netcdf_file_path
            print "  Global attributes"

        netcdf_file = netCDF4.Dataset(netcdf_file_path)
        if prevent_masked_arrays:
            netcdf_file.set_auto_mask(False)

        data_object["names_of_global_attributes"] = []
        data_object["global_attributes"] = {}
        for global_attribute_name in netcdf_file.ncattrs():
            data_object["names_of_global_attributes"].append(
                global_attribute_name)
            data_object["global_attributes"][global_attribute_name] = {
                "value": netcdf_file.getncattr(global_attribute_name)}
            data_object["global_attributes"][global_attribute_name]["data_type"] = return_data_type_for_value(data_object["global_attributes"][global_attribute_name]["value"])

            if verbosity_level >= 2:
                print "    %s" % global_attribute_name

        if verbosity_level >= 2:
            print "\n  Dimensions"

        data_object["names_of_dimensions"] = []
        data_object["dimensions"] = {}
        for dimension_name in netcdf_file.dimensions:
            data_object["names_of_dimensions"].append(dimension_name)
            data_object["dimensions"][dimension_name] = len(
                netcdf_file.dimensions[dimension_name])

            if verbosity_level >= 2:
                print "    %s" % dimension_name

        if verbosity_level >= 2:
            print "\n  Variables"

        data_object["names_of_variables"] = []
        data_object["variables"] = {}
        for variable_name in netcdf_file.variables:
            if verbosity_level >= 2:
                print "    %s" % variable_name

            data_object["names_of_variables"].append(variable_name)
            data_object["variables"][variable_name] = {
                "values": netcdf_file.variables[variable_name][:],
                "dimensions": [],
                "names_of_attributes": []}

            data_object["variables"][variable_name]["data_type"] = return_data_type_for_value(data_object["variables"][variable_name]["values"])

            for dimension_name in netcdf_file.variables[
                variable_name].dimensions:

                data_object["variables"][variable_name]["dimensions"].append(
                    dimension_name)

            for attribute_name in netcdf_file.variables[variable_name].ncattrs():
                data_object["variables"][variable_name][
                    "names_of_attributes"].append(attribute_name)
                data_object["variables"][variable_name][attribute_name] = {
                    "value": netcdf_file.variables[variable_name].getncattr(attribute_name)}
                data_object["variables"][variable_name][attribute_name]["data_type"] = return_data_type_for_value(data_object["variables"][variable_name][attribute_name]["value"])

                if verbosity_level >= 3:
                    print "      %s" % attribute_name

        netcdf_file.close()

    return data_object
#
########################################################################
#
# Main function - writes a data object to a netCDF file. It currently only
# permits netCDF 3 classic files to be created. 
#
def write_to_netcdf_file(
        data_object,netcdf_file_path,automatically_update_history=False):

    no_errors_have_been_encountered = True

    directory_path = os.path.dirname(netcdf_file_path)
    if not ((directory_path == "") or os.path.isdir(directory_path)):
        no_errors_have_been_encountered = False
        print "ERROR: %s.write_to_netcdf_file()" % __file__
        print "  directory part of netcdf file path (%s) is invalid" % directory_path

    if not netcdf_file_path.endswith(".nc"):
        no_errors_have_been_encountered = False
        print "ERROR: %s.write_to_netcdf_file()" % __file__
        print "  supplied netcdf file path does not have an 'nc' extensionvalid: %s" % netcdf_file_path

    if automatically_update_history not in [True, False]:
        no_errors_have_been_encountered = False
        print "ERROR: %s.write_to_netcdf_file()" % __file__
        print "  the supplied value of 'automatically_update_history' was neither True nor False"
#
    if no_errors_have_been_encountered:
        netcdf_file = netCDF4.Dataset(
            netcdf_file_path,"w",format="NETCDF3_CLASSIC")

        for dimension_name in data_object["names_of_dimensions"]:
            dimension = netcdf_file.createDimension(
                dimension_name,data_object["dimensions"][dimension_name])
#
# Create a "history" global attribute if one doesn't already exist, and 
# update it with the current date/time for file creation.
#
        if automatically_update_history:
            line_break = ""
            if "history" in data_object["names_of_global_attributes"]:
                if ((len(data_object["global_attributes"]["history"]["value"]) > 0) and
                    not(data_object["global_attributes"]["history"]["value"].endswith("\n"))):
                    line_break = "\n"
            else:
                data_object["names_of_global_attributes"].append("history")
                data_object["global_attributes"]["history"] = {
                    "data_type": "str", "value": ""}
              
            new_history_element = \
                "%s%s - netcdf file created on computer %s ." % (
                    line_break,
                    datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                    platform.node())
            data_object["global_attributes"]["history"]["value"] += new_history_element
#    
        for attribute_name in data_object["names_of_global_attributes"]:
            netcdf_file.setncattr(
                attribute_name,
                data_object["global_attributes"][attribute_name]["value"])
#
        for variable_name in data_object["names_of_variables"]:
            data_type_object = return_data_type_object(
                data_object["variables"][variable_name]["data_type"])
            netcdf_variable = netcdf_file.createVariable(
                variable_name,
                data_type_object,
                data_object["variables"][variable_name]["dimensions"])

            netcdf_variable[:] = data_object[
                "variables"][variable_name]["values"][:]

            for attribute_name in data_object["variables"][variable_name]["names_of_attributes"]:
                netcdf_variable.setncattr(
                    attribute_name,
                    data_object["variables"][variable_name][attribute_name]["value"])
        netcdf_file.close()
#
    if no_errors_have_been_encountered:
        return 0
    else:
        return 1
#
#######################
#
