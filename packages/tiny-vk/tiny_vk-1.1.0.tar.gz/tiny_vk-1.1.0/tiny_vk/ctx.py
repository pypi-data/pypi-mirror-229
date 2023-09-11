class CtxStorage():
  """
This class is a simple mechanism for storing data available within the context of program execution.
  """
  @staticmethod
  def set(name : str , value : object):
    setattr(CtxStorage,str(name),value)

  @staticmethod
  def delete(name : str):
    delattr(CtxStorage,str(name))
  
  @staticmethod
  def get(name : str):
    return getattr(CtxStorage,str(name))