import vk_api 
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import threading

import inspect,types


from .utils import BotUtils
from .exceptions import EmptyValueError
from .database import Database




def add_to_loop(_object : object):
    """
Add functions or objects to the loop execution.

Args:
    _object (object): The object or function to be added to the loop.

Description:
    - If `_object` is a function, it is added to the `_builder` object with
      the name as a string representation of the function.
    - If `_object` is not a function, it iterates over the attributes of
      the object and selects only the functions (excluding the
      `add_to_loop` function itself). Each selected function is then added
      to the `_builder` object with the name as a string representation
      of the function.
    """
    if isinstance(_object,types.FunctionType):
      setattr(_builder,str(_object),_object)
    else :
      funcs = [func for func in _object.__dict__.values() if inspect.isfunction(func) and func != _builder.add_to_loop]
      for function in funcs:
        setattr(_builder,str(function),function)

class _builder:
  """
An empty class to which functions are passed for execution
  """

class _handlers:
  
  def __init__(meta,database: Database) -> None:
    meta.db = database  
  
  def state(meta, *states: str, next_state : str = None) -> None:
    def inner(function):
      def wrapper(self):
        if self.state in states:
          meta.db.set_state(next_state) if next_state else None
          return function(self)
      add_to_loop(wrapper)
      return wrapper
    return inner

  def message(meta,*commands:str, next_state : str = None) -> None:
    def inner(function):
      def wrapper(self):
        if self.text in commands:
          meta.db.set_state(next_state) if next_state else None
          return function(self)
        elif not commands:
          meta.db.set_state(next_state) if next_state else None
          return function(self)
      add_to_loop(wrapper)
      return wrapper
    return inner

  def multiply(meta,commands : list[str], states : list[str], next_state : str = None)-> None:
    def inner(function):
      def wrapper(self):
        if self.state in states and self.text in commands:
          meta.db.set_state(next_state) if next_state else None
          return function(self)
      add_to_loop(wrapper)
      return wrapper
    return inner

  def empty(meta,condition : str,next_state : str = None) -> None:
    """
    This decorator takes a single argument called condition, 
    which should be a string that is suitable for use in the eval() function.
    """
    def inner(function):
      def wrapper(self):
        if eval(condition):
          meta.db.set_state(next_state) if next_state else None
          return function(self)
      add_to_loop(wrapper)
      return wrapper
    return inner


class Bot:

  def __init__(self, __token : str = None, 
               group_id : int = None, 
               dbfile : str = 'TinyVK.db',table_name : str  = 'Bot', 
               columns : dict = {}) -> None:

    self.__token = __token
    self.chat = 1 if group_id else 0
    
    session = vk_api.VkApi(token=self.__token)
    self.longpoll = VkBotLongPoll(session, group_id=group_id) if self.chat else VkLongPoll(session)
    
   
    
    table_name if table_name else ['User','Chat'][self.chat]+'Bot'

    
    # Initializing the database file
    self.db = Database(dbfile,table_name)
    
    col = [{"id" : "INT", "state" : "TEXT"},{"id":"INT"}][self.chat] 
    self.db.create_table(col | columns)
    
    # Initializing handlers
    self.on = _handlers(database=self.db)


  def __loop(self) -> None:
    
    
    # Launching additional utilities
    self.utils = BotUtils(self.__token,self.id,self.chat)
    
    # Initializing the table
    self.db._one_loop_(self.id)
    
    # Getting attributes for id by database tags
    data = self.db.get_information()
    for name,value in data.items():
      setattr(Bot,name,value)

    # Getting handler functions
    funcs = [func for func in _builder.__dict__.values() if inspect.isfunction(func)]
    for execute_function in funcs:
      execute_function(self)

  def start(self) -> None:
    """Start the bot"""
    if self.chat == 0:
      for event in self.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
          self.id = event.user_id
          self.text = event.text
          
          #Starting a thread with handlers
          threading.Thread(target=self.__loop).start()
    else:
      for event in self.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
          self.id = event.chat_id
          self.text = event.message['text']
          
          #Starting a thread with handlers
          threading.Thread(target=self.__loop).start()