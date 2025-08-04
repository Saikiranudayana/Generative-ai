import sqlite3


##connect to sqlite
connection= sqlite3.connect('students.db')

##create a cursor object to insert record , create table etc
cursor = connection.cursor()

## create the table  
table_info = """
create table STUDENTS(NAME VARCHAR(25),CLASS VARCHAR(25),
SECTION VARCHAR(25),MARKS INT) """

cursor.execute(table_info)

##insert records
cursor.execute('''INSERT INTO STUDENTS VALUES('Sai','AI','A',85)''')
cursor.execute('''INSERT INTO STUDENTS VALUES('Kiran','Data Science','B',85)''')
cursor.execute('''INSERT INTO STUDENTS VALUES('Nag','Devops','C',85)''')
cursor.execute('''INSERT INTO STUDENTS VALUES('ajay','Data Analytics','A',85)''')
cursor.execute('''INSERT INTO STUDENTS VALUES('Mani','Data Science','B',85)''')
cursor.execute('''INSERT INTO STUDENTS VALUES('Shiva','App Development','A',85)''')


## Display al the records
print("All records in the STUDENTS table:")
data = cursor.execute('''SELECT * FROM STUDENTS''')

for row in data:
    print(row)
    
## commit all the changes in the database
connection.commit()
connection.close()