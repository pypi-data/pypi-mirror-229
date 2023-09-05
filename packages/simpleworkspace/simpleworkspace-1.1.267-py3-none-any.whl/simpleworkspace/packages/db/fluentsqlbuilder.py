from typing import List, Optional, Generator
from ...utility.stopwatch import StopWatch

try:
    from mysql.connector.connection import MySQLConnectionAbstract as MySQLConnection 
    from mysql.connector.cursor import CursorBase as MySQLCursor
except ImportError:
    pass

try:
    from pyodbc import Connection as MsSqlConnection
    from pyodbc import Cursor as MsSqlCursor
except ImportError:
    pass

try:
    from sqlite3 import Connection as Sqlite3Connection
    from sqlite3 import Cursor as Sqlite3Cursor
except ImportError:
    pass


class _FluentSqlBuilderExecuteResults:
    '''Represents the result of an executed SQL query using FluentSqlBuilder'''
    def __init__(self, executed_statement: 'Sqlite3Cursor|MsSqlCursor|MySQLCursor', execution_time_ms):
        self._executed_statement = executed_statement
        self.execution_time_ms = execution_time_ms
        self._FetchMode_Dictionary = True

    def _OnGetRow(self, row: tuple):
        '''row is by default cursors expected to be numeric index mode'''

        if not (self._FetchMode_Dictionary):
            return row
        
        row_dict = {}
        for i, value in enumerate(row):
            column_name = self._executed_statement.description[i][0]
            row_dict[column_name] = value
        return row_dict
    
    def FirstOrDefault(self) -> dict|tuple|None:
        '''Returns the first row or None if no result'''
        for row in self.Iterator():
            return row
        return None

    def ToArray(self) -> List[dict]|List[tuple]:
        '''Loads all resulting rows into memory and returns them as a list'''
        return list(self.Iterator())

    def Iterator(self) -> Generator[int, dict|tuple, None]:
        '''
        Loads one row at a time in a memory-efficient manner, useful for large result sets.
        
        Example:
        >>> for row in self.iterator():
        ...
        '''
        while True:
            row = self._executed_statement.fetchone()
            if row is None:
                break
            yield self._OnGetRow(row)

    def AffectedRowCount(self) -> int:
        '''Returns the number of rows affected by the query (for DELETE, INSERT, UPDATE queries)'''
        return self._executed_statement.rowcount

    def SetFetchMode_Dictionary(self):
        self._FetchMode_Dictionary = True
        return self
    
    def SetFetchMode_NumericIndex(self):
        '''
        Uses column indexes instead of column names when gathering results
        Example:
          result['columnName'] changes to result[0]...
        '''
        self._FetchMode_Dictionary = False
        return self

    def __del__(self):
        '''when garbage collecting the result, closes the cursor'''
        self._executed_statement.close()


class FluentSqlBuilderError(Exception):
    def __init__(self, operation: str, message: str):
        if operation:
            message = f"{operation}: {message}"
        super().__init__(message)

class FluentSqlBuilder:
    '''FluentSqlBuilder provides a fluent interface for building and executing SQL queries'''
    def __init__(self, connection: 'MySQLConnection|MsSqlConnection|Sqlite3Connection'):
        self._connection = connection
        self._segments = []
        self._params = []

        self._SetTypeOfConnection()

    def _SetTypeOfConnection(self):
        self._connection_is_MSSQL = False
        self._connection_is_MYSQL = False
        self._connection_is_SQLITE3 = False

        #if a module is missing, then we definitely do not have that type of connection
        try:
            self._connection_is_MYSQL = isinstance(self._connection, MySQLConnection)  # Detect Mysql connection
        except Exception:
            pass
        
        try:
            self._connection_is_MSSQL = isinstance(self._connection, MsSqlConnection)  # Detect MSSQL connection
        except Exception:
            pass

        try:
            self._connection_is_SQLITE3 = isinstance(self._connection, Sqlite3Connection)  # Detect sqlite3 connection
        except Exception:
            pass  
        return


    def CreateTable(self, tableName: str, ignoreIfExists = False):
        """
        Creates a new table in the database.

        :param tableName: Name of the table.
        :param ignore_if_exists: Ignore error if the table already exists.
        
        Example:
        >>> FluentSqlBuilder(connection) 
        >>>     .CreateTable('users') 
        >>>     .Column('id', 'INT PRIMARY KEY') 
        >>>     .Column('name', 'VARCHAR(100)') 
        >>>     .Column('age', 'INT') 
        >>>     .Execute()
        ...
        """

        if not tableName:
            raise FluentSqlBuilderError("create_table", "No table name specified")

        if(self._connection_is_MSSQL):
            ignoreIfExists = False #mssql doesnt support this
        
        if(ignoreIfExists):
            self.Append(f"CREATE TABLE IF NOT EXISTS {tableName}")
        else:
            self.Append(f"CREATE TABLE {tableName}")
        return self

    def Column(self, column_name: str, attributes: str, foreignKeyReference: Optional[str] = None):
        '''
        Adds a column to the table.

        :param column_name: Name of the column.
        :param attributes: Any column attributes, e.g., "INT PRIMARY KEY".
        :param foreign_key_reference: Make the column a foreign key by specifying a reference like 'OtherTable(columnName)'.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .CreateTable('users')
        >>>     .Column('id', 'INT PRIMARY KEY')
        >>>     .Column('name', 'VARCHAR(100)')
        >>>     .Column('age', 'INT')
        >>>     .Execute()
        ...
        '''
        
        if not column_name or not attributes:
            raise FluentSqlBuilderError("column", "Empty column name or attributes")

        last_segment = self.GetLastSegment()
        if not isinstance(last_segment, _FluentSqlBuilderChainableClauseColumn):
            last_segment = _FluentSqlBuilderChainableClauseColumn()
            self._segments.append(last_segment)

        last_segment.Add(f"{column_name} {attributes}")
        if foreignKeyReference:
            last_segment.Add(f"FOREIGN KEY ({column_name}) REFERENCES {foreignKeyReference}")
        return self

    def Select(self, *column_names: str, TOP:int=None):
        if not column_names:
            raise FluentSqlBuilderError("select", "Nothing selected")

        sql = f"SELECT "
        if(self._connection_is_MSSQL and TOP is not None):
            sql += f"TOP {TOP} "

        sql += ', '.join(column_names)
        
        self.Append(sql)
        return self

    def From(self, tableName: str):
        if not tableName:
            raise FluentSqlBuilderError("from_table", "Table name not specified")

        sql = f"FROM {tableName}"
        self.Append(sql)
        return self

    def Insert(self, tableName: str, *keyValuePairs: dict):
        '''
        Adds an INSERT INTO clause to the query for inserting data into a table.

        :param table: The name of the table where data will be inserted.
        :param keyValuePairs: An dict of column names and their corresponding values.

        Example insert - single:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .Execute()
        ...

        Example insert - multiple:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users',
        >>>         {'name': 'John Doe', 'age': 30},
        >>>         {'name': 'Bob Lasso', 'age': 45}
        >>>     )
        >>>     .Execute()
        ...
        '''

        if not tableName or not keyValuePairs:
            raise FluentSqlBuilderError("insert", "Empty or invalid table/keyValuePairs")

        column_names = list(keyValuePairs[0].keys())
        value_placeholder_template = "(" + self.GeneratePreparedPlaceholders(len(column_names)) + ")"
        value_placeholders = []

        for row_mapping in keyValuePairs:
            self._params.extend(list(row_mapping.values()))
            value_placeholders.append(value_placeholder_template)

        column_names = ', '.join(column_names)
        value_placeholders = ', '.join(value_placeholders)

        self.Append(f"INSERT INTO {tableName} ({column_names}) VALUES {value_placeholders}")
        return self

    def OnDuplicateKeyUpdate(self):
        '''
        Is used after an insert statement. When the insert fails due to a duplicate key,
        allows updating specific columns with new values.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .OnDuplicateKeyUpdate()
        >>>     .Set("age = VALUES(age)")
        >>>     .Set("name = ?", "newName")
        >>>     .Execute()
        ...
        '''

        if not self._IsStatementInsert():
            raise FluentSqlBuilderError("on_duplicate_key_update", "Used in conjunction with insert statements only")

        self.Append("ON DUPLICATE KEY UPDATE")
        return self

    def OnDuplicateKeyIgnore(self):
        '''
        Is used after an insert statement. When the insert fails due to a duplicate key, errors are ignored
        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .OnDuplicateKeyIgnore()
        >>>     .Execute()
        ...
        '''

        if not self._IsStatementInsert():
            raise FluentSqlBuilderError("on_duplicate_key_update", "Used in conjunction with insert statements only")

        self._segments[0] = "INSERT IGNORE" + self._segments[0][6:]
        return self
    
    def Update(self, tableName: str):
        '''
        Adds an UPDATE clause to the query for updating values in a table.
        Requires a where condition before execute.

        :param table: The name of the table where the update operation will take place.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Update('users')
        >>>     .Set('name = ?', new_name)
        >>>     .Set('age = age + 1')
        >>>     .Where('id = ?', user_id)
        >>>     .Execute()
        ...
        '''
        if not tableName:
            raise FluentSqlBuilderError("update", "Empty table")

        self.Append(f"UPDATE {tableName} SET")
        return self

    def Set(self, sql: str, *params):
        '''
        A chainable clause that simply makes comma-separated assignments, mainly used
        in conjunction with statements/clauses where you need to assign variables such as UPDATE or ONDUPLICATEKEYUPDATE.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Update('users')
        >>>     .Set('name = ?', new_name)
        >>>     .Set('age = age + 1')
        >>>     .Where('id = ?', user_id)
        >>>     .Execute()
        ...
        '''
        if not sql:
            raise FluentSqlBuilderError("set", "Empty assignment")

        last_segment = self.GetLastSegment()
        if not isinstance(last_segment, _FluentSqlBuilderChainableClauseSet):
            last_segment = _FluentSqlBuilderChainableClauseSet()
            self._segments.append(last_segment)

        last_segment.Add(sql)
        self._params.extend(params)
        return self

    def Delete(self):
        '''
        Adds a DELETE clause to the query for deleting rows in a table.
        Requires a where condition.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Delete()
        >>>     .From('users')
        >>>     .Where('name = ?', 'John Doe')
        >>>     .Execute()
        ...
        '''
        self.Append("DELETE")
        return self

    def Join(self, tableName: str, onCondition: str):
        '''
        Adds a join clause to the query.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Select(*)
        >>>     .From('users')
        >>>     .Join('user_roles', onCondition='users.roleId = user_roles.id')
        >>>     .Execute()
        ...
        '''
        if not tableName or not onCondition:
            raise FluentSqlBuilderError("join", "Empty tableName/onCondition")

        self.Append(f"JOIN {tableName} ON {onCondition}")
        return self
    
    def InnerJoin(self, tableName, onCondition:str):
        self.Append("INNER")
        self.Join(tableName, onCondition)

    def LeftJoin(self, tableName, onCondition:str):
        self.Append("LEFT")
        self.Join(tableName, onCondition) 

    def RightJoin(self, tableName, onCondition:str):
        self.Append("RIGHT")
        self.Join(tableName, onCondition) 

    def FullOuterJoin(self, tableName, onCondition:str):
        self.Append("FULL OUTER")
        self.Join(tableName, onCondition) 

    def CrossJoin(self, tableName):
        self.Append(f"CROSS JOIN {tableName}")

    def Where(self, condition: str, *params):
        '''
        Adds the starting WHERE clause and is a start point to create conditions.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Select('*')
        >>>     .From('users')
        >>>     .Where('name = ?', 'John Doe')
        >>>     .Execute()
        ...
        '''
        if not condition:
            raise FluentSqlBuilderError("where", "Empty condition")

        self.Append(f"WHERE {condition}", *params)
        return self

    def WhereIn(self, column_name: str, params:tuple):
        '''
        Adds the starting WHERE IN clause and is a start point to create conditions.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Select('*')
        >>>     .From('users')
        >>>     .WhereIn('name', ['John Doe', 'Bob Dylan'])
        >>>     .Execute()
        ...
        '''
        self.GenericInClause("WHERE", column_name, params)
        return self

    def WhereNotIn(self, column_name: str, params:tuple):
        self.GenericNotInClause("WHERE", column_name, params)
        return self

    def And(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("And", "Empty condition")

        self.Append(f"AND {condition}", *params)
        return self

    def AndNot(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("AndNot", "Empty condition")

        self.Append(f"AND NOT {condition}", *params)
        return self

    def AndIn(self, column_name: str, params:tuple):
        self.GenericInClause("AND", column_name, params)
        return self

    def AndNotIn(self, column_name: str, params:tuple):
        self.GenericNotInClause("AND", column_name, params)
        return self

    def Or(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("Or", "Empty condition")

        self.Append(f"OR {condition}", *params)
        return self

    def OrNot(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("OrNot", "Empty condition")

        self.Append(f"OR NOT {condition}", *params)
        return self

    def OrIn(self, column_name: str, params:tuple):
        self.GenericInClause("OR", column_name, params)
        return self

    def OrNotIn(self, column_name: str, params:tuple):
        self.GenericNotInClause("OR", column_name, params)
        return self

    def Append(self, sql: str, *params):
        '''
        This method allows you to freely add a parameterized/prepared SQL query.

        :param sql: The custom SQL to be added to the query.
        :param params: The parameters to be bound to the condition placeholders.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Append('SELECT *')
        >>>     .Append('FROM users')
        >>>     .Append('WHERE age > ?', 18)
        >>>     .Execute()
        ...
        '''
        if not sql:
            raise FluentSqlBuilderError("append", "Empty SQL")

        self._segments.append(sql)
        if params:
            self._params.extend(params)
        return self

    def OrderByAscending(self, column_name: str):
        '''
        Adds ORDER BY clause with ascending direction. This clause is chainable by following
        with more OrderBy* methods.
        '''
        return self.OrderBy(column_name, "ASC")

    def OrderByDescending(self, column_name: str):
        '''
        Adds ORDER BY clause with descending direction. This clause is chainable by following
        with more OrderBy* methods.
        '''
        return self.OrderBy(column_name, "DESC")

    def OrderBy(self, column_name: str, direction: str):
        if not column_name or not direction:
            raise FluentSqlBuilderError("ORDERBY", "Empty column name or direction")

        last_segment = self.GetLastSegment()
        if not isinstance(last_segment, _FluentSqlBuilderChainableClauseOrderBy):
            last_segment = _FluentSqlBuilderChainableClauseOrderBy()
            self._segments.append(last_segment)

        last_segment.Add(column_name, direction)
        return self

    def Limit(self, max_row_count: int):
        self.Append(f"LIMIT {max_row_count}")
        return self

    def Execute(self):
        sw = StopWatch()
        sw.Start()
        self._ValidateBuiltQuery()

        if(self._connection_is_MYSQL):
            #only for mysql cursor, having prepared param behaves more like the rest, sql injections are safe either either way,
            #but small changes for example are that datatypes such as blob columns are retrieved properly.
            cursor = self._connection.cursor(prepared=True) 
        else:
            cursor = self._connection.cursor()

        cursor.execute(str(self), self._params)

        if(self._IsStatementDelete() or self._IsStatementInsert() or self._IsStatementUpdate()):
            self._connection.commit() #persist changes to database

        sw.Stop()
        return _FluentSqlBuilderExecuteResults(cursor, sw.GetElapsedMilliseconds())

    def __str__(self):
        '''Returns the built SQL query string with placeholders (e.g., ?)'''
        return " ".join(str(segment) for segment in self._segments)

    def _ValidateBuiltQuery(self):
        if not self._segments:
            raise FluentSqlBuilderError("Execute", "No query")

        if self._IsStatementUpdate() or self._IsStatementDelete():
            if not self._HasClauseWhere():
                raise FluentSqlBuilderError("Execute", "Safety check error, Update/Delete queries must have a where condition, otherwise all rows in the table would be altered")

    def _HasClauseWhere(self):
        for segment in self._segments:
            if not (isinstance(segment, str)): #where queries are only part of string segments
                continue
            if segment.startswith("WHERE"):
                return True
        return False

    def _IsStatementInsert(self):
        if not self._segments:
            return False
        return str(self._segments[0]).startswith("INSERT")

    def _IsStatementUpdate(self):
        if not self._segments:
            return False
        return str(self._segments[0]).startswith("UPDATE")

    def _IsStatementDelete(self):
        if not self._segments:
            return False
        return str(self._segments[0]).startswith("DELETE")

    def GenericInClause(self, prefix: str, column_name: str, params:tuple):
        if not params or not column_name:
            raise FluentSqlBuilderError("generic_in_clause", "Nothing compared")

        placeholders = self.GeneratePreparedPlaceholders(len(params))
        self.Append(f"{prefix} {column_name} IN ({placeholders})", *params)

    def GenericNotInClause(self, prefix: str, column_name: str, params:tuple):
        if not params or not column_name:
            raise FluentSqlBuilderError("generic_not_in_clause", "Nothing compared")

        placeholders = self.GeneratePreparedPlaceholders(len(params))
        self.Append(f"{prefix} {column_name} NOT IN ({placeholders})", *params)

    @staticmethod
    def GeneratePreparedPlaceholders(placeholder_count: int) -> str:
        if placeholder_count <= 0:
            return ""
        return ', '.join(['?'] * placeholder_count)

    def GetSegmentCount(self) -> int:
        return len(self._segments)


    def GetLastSegment(self):
        '''Retrieves the last segment or None if no segments exist'''
        if not self._segments:
            return None
        return self._segments[-1]


class _FluentSqlBuilderChainableClauseColumn:
    def __init__(self):
        self._segments = []

    def Add(self, sql: str):
        self._segments.append(sql)

    def __str__(self):
        return '(' + ', '.join(self._segments) + ')'


class _FluentSqlBuilderChainableClauseSet:
    def __init__(self):
        self._segments = []

    def Add(self, sql: str):
        self._segments.append(sql)

    def __str__(self):
        return ', '.join(self._segments)


class _FluentSqlBuilderChainableClauseOrderBy:
    def __init__(self):
        self._segments = []

    def Add(self, column_name: str, direction: str):
        self._segments.append(f"{column_name} {direction}")

    def __str__(self):
        return "ORDER BY " + ', '.join(self._segments)


