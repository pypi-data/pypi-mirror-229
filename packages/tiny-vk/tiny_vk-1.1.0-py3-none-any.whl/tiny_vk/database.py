import sqlite3

def _dict_to_sqlite3(dictionary : dict) -> str:

  __string = ""
  __counter = 0
  #Проверка типов данных
  for key,dtype in dictionary.items():
    __counter += 1
    if dtype not in ('INT','REAL','TEXT','BLOB'):
      raise TypeError(f"{key} not supported type : {dtype}")
    __string+= "{} {}".format(key,dtype)
    __string+= "" if __counter == len(dictionary) else ","
  return f"({__string})"

class Database:
  """Класс базы данных для удобного управления tinyvk"""

  def __init__(self,__dbfile : str ,__table_name : str) -> None:
    self.__conn = sqlite3.connect(f'{__dbfile}',check_same_thread=False)
    self.__cur = self.__conn.cursor()
    self.__table_name = __table_name

  def create_table(self, __colums : dict):
    self.__dictionary = _dict_to_sqlite3(__colums)
    self.__cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.__table_name}{self.__dictionary};""")
    self.__conn.commit()
    
  def get_titles(self) -> list:
    self.__cur.execute(f'PRAGMA table_info({self.__table_name})')
    titles = [i[1] for i in self.__cur.fetchall()]
    return titles 
  
  def update_field(self, id : int | str = None, category : str = None,  new : str = None):
    id = id if id else self.id
    
    self.__cur.execute(f"""UPDATE {self.__table_name} set {category} = '{new}' where id = {id}""")
    self.__conn.commit()

  def get_information(self, id : int | str = None )-> dict:
    id = id if id else self.id
    
    self.__cur.execute(f"""SELECT * from {self.__table_name} where id = {id}""")
    values = self.__cur.fetchone()
    
    self.__cur.execute(f'PRAGMA table_info({self.__table_name})')
    titles = [i[1] for i in self.__cur.fetchall()]
    
    dictionary = {}
    
    
    for title,value in zip(titles,values):
      dictionary[title] = value
    return dictionary

  def _one_loop_(self, id : int | str = None):
    self.id = id
    self.__cur.execute(f"""SELECT * from {self.__table_name} """)
    id_list = [row[0] for row in self.__cur.  fetchall()]
    if id not in id_list:
      self.__cur.execute(f"""INSERT INTO {self.__table_name}(id) VALUES ('{id}')""")
      self.__conn.commit()

  def delete_user(self, id : int | str = None):
    id = id if id else self.id
    self.__cur.execute(f"""DELETE from {self.__table_name} where id = {id}""")
    self.__conn.commit()

  def set_state(self,__new_state: str = None,id : int | str = None):
    id = id if id else self.id
    self.__cur.execute(f"""UPDATE {self.__table_name} set state = '{__new_state}' where id = {id}""")
    self.__conn.commit()

  def get_users(self) -> list | None:
    self.__cur.execute(f"""SELECT * from {self.__table_name} """)
    result = [elem[0] for elem in self.__cur.fetchall()]
  
    if not result:
      return None
    return result

  def get_mailing_ids(self,category : str) -> tuple[int]:
    self.__cur.execute(f"""SELECT * from {self.__table_name} where {category} = 1""")
    values = [(i[0],i[2]) for i in self.__cur.fetchall()]
    return tuple(values)
