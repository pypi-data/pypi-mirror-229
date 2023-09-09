# this is an example of how to load:
# 1. Schema files into blank instances of Interfaces
# 2. Data into blank instances
# 3. A schema file and a data file and load them


# this is helpful for type checking data!! P.S. if someone wants to create something like TypeChat using this, I WOULD BE THRILLEDD!

#imports
import IF4 
import json

#define paths
schema_path = "schema.json"
data_path = "data.json"


# generate_interfaces
# to load schema into blank Interfaces, you can use the IF4.generate_interfaces function
# it takes schema in a dictionary format, which you can do using something like json.load(open(schema_path))

schema_data = json.load(open(schema_path))
interfaces = IF4.generate_interfaces(schema_data)    #this will return  interfaces that are blank but have the types that are defined in the file

# now, we can load the data the same way

data_data = json.load(open(data_path))

# then, we use the load_data function to load the data decided in the file

objects = IF4.load_data(data_data, interfaces) # this will return a dictionary of defined interfaces with the data from the file


# now, to do this all in one step, you can use the getObjs function, which take the paths to both of your files. It will return 
# a dictionary of defiend and loaded interfaces

objects_different = IF4.getObjs(schema_path, data_path)

# as a reminder, this will check the types as they are loaded



