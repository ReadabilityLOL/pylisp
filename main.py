import cmath  #math functions
import operator  #operators
import importlib #get own imports

""" 
Classes
"""

class Env(dict):
  def __init__(self,params=(),args=(),outer_env=None):
    self.params, self.args, self.outer_env = params,args,outer_env
    self.update(zip(params,args))
  # def find(self,val):
  #   return self[val] if(val in self) else self.outer_env.find(val)
  def find(self, val):
    if val in self:
      return self[val]
    elif self.outer_env is not None:
      return self.outer_env.find(val)
    else:
      raise NameError(f'Name "{val}" is not defined.')

class String():
  def __init__(self,value):
    self.value = value

class Procedure(object):
  def __init__(self,params,body,env):
    self.params, self.body, self.env = params, body, env
    
  def __call__(self,*args):
    local_env = Env()
    local_env.update(normal_env)
    local_env.update(zip(self.params,args))
    return evaluate(self.body,local_env)

"""
Environment
"""

normal_env = Env()
#Well behaved functions
normal_env.update({
  "+":operator.add,
  "-":operator.sub,
  "/":operator.truediv,
  "*":operator.mul,
  "pow":operator.pow,
  "eq":operator.eq,
  "lt":operator.lt,
  "le":operator.le,
  "gt":operator.gt,
  "ge":operator.ge,
  "ne":operator.ne,
  "true":True,
  "false":False,
  "procedure?":callable,
  "not":operator.not_,
  "range":lambda x,y,z=1:list(range(x,y,z)),
  "map":lambda x,y:list(map(x,y)),
  "dict":lambda x:dict(x),
  "update":lambda x,y: x.update(y),
  "round":lambda x,y=0:round(x.real,y)+round(x.imag,y)*1j,
  "list":lambda *x: list(x),
  "cdr":lambda x:x[1:],
  "car":lambda x:x[0],
  "nth":lambda x,y:y[x],
  "sum":sum,
  "chr":chr,
  "print":print,
  "float":lambda x:float(x),
  "int":lambda x:int(x),
  "str":lambda x:str(x),
})

#functions that need a bit more help

# def define(var,val,env):
#   pass

# def fn(params,body,env):
#   pass

# special = {
#   "define":define,
#   "lambda":fn,
# }



normal_env.update(vars(cmath)) #math variables imported

#just a useful function
def clean(value):
  if isinstance(value,complex) and value == value.real:
    return value.real
  return value

"""
Lexing
"""

# scanner = re.Scanner([
#   (r"([a-zA-Z]([a-zA-Z0-9]?)+)",    lambda scanner,token:{"type":"SYMBOL", "value":token}),
#   (r"([0-9]+(\.[0-9]+))",    lambda scanner,token:{"type":"FLOAT", "value":float(token)}),
#   (r"([0-9]+)",    lambda scanner,token:{"type":"INTEGER", "value":int(token)}),
#   (r"([\+|-|/|\*]+)",   lambda scanner,token:{"type":"OPERATOR", "value":token}),
#   (r"(\".*\")",    lambda scanner,token:{"type":"STRING", "value":token}),
#   (r"(\()",    lambda scanner,token:{"type":"L_PAREN", "value":token}),
#   (r"(\))",    lambda scanner,token:{"type":"R_PAREN", "value":token}),
#   (r'.', lambda scanner, token: None),
# ], flags=re.DOTALL)

# def lex(string):
#   result = scanner.scan(string)
#   return result[0]

def lex(string): #VERY basic lexing. Not even lexing, tokenization
  # strlist = string.replace("("," ( ").replace(")"," ) ").split()
  # lexlist = []
  # for x in strlist:
  #   temp = ""
  #   if x == '"':
  #     while x != '"':
  #       temp+=x
  #     lexlist.append(String(x))
  #     continue
  #   lexlist.append(x)
      
    
  return string.replace("("," ( ").replace(")"," ) ").split()
  # return lexlist

"""
Parsing
"""

def parse(string):
  return read(lex(string))

def read(tokens):
  if len(tokens) == 0:
    return None
  token = tokens.pop(0)
  if token == "(":
    list1 = []
    while tokens[0] != ")":
      list1.append(read(tokens))
    tokens.pop(0)
    return list1
  if token == ")":
    raise Exception("Unexpected ')'")
  else:
    return atom(token)

def atom(token):
  try:
    return int(token) 
  except:
    try:
      return float(token)
    except:
      try:
        return complex(token)
      except:
        return token

"""
Evaluation
"""

def evaluate(parsed,env=normal_env):
  if parsed is None:
    return None
  elif isinstance(parsed,(int,float,complex)):
    return parsed
  elif parsed[0] == "quote":
    return parsed[1:]
  elif parsed[0] == "if":
    if len(parsed) == 3:
      (_,x,y) = parsed
      if evaluate(x):
        return evaluate(y)
    elif len(parsed) == 4:
      (_,x,y,z) = parsed
      if evaluate(x):
        return evaluate(y)
      else:
        return evaluate(z)
    else:
      raise Exception(f"If expects 2 or 3 parameters, not {len(parsed) - 1}")

  elif parsed[0] == "define":
    evaluated = [evaluate(x) for x in parsed[2:]]
    env[parsed[1]] = evaluated[0]
  elif parsed[0] == "lambda":
    (_,params,body) = parsed
    return Procedure(params,body,env)
  elif parsed[0] == "import":
    importlib.import_module(parsed[1:])
  elif parsed[0] == "while":
    (_,conditional,body) = parsed
    while evaluate(conditional):
      for x in body:
        evaluate(x)
  # if isinstance(parsed,list):
  #   list1 = [evaluate(x,env=env) for x in parsed]
  #   op, *args = list1
  #   return op(*args)

  elif isinstance(parsed,str):
    return env.find(parsed)
  elif isinstance(parsed[0],str):
    # if parsed in normal_env:
    #   return normal_env[parsed]
    arguments = [evaluate(x,env) for x in parsed[1:]]
    return env.find(parsed[0])(*arguments)
  elif callable(parsed):
    return parsed()
  else:
    return parsed

normal_env.update({"eval":evaluate})

"""
REPL
"""
def repl(prompt="prompt> "):
  while True:
    inputted = input(prompt)
    try:
      print(lispstring(evaluate(parse(inputted))))
    except Exception as e:
      print(e)
      
def niceprint(string):
  if string is not None:
    newstring = lispstring(string)
    print(newstring)

def lispstring(val):
  cleanval = clean(val)
  if isinstance(cleanval,list):
    return "("+ " ".join(str(lispstring(x)) for x in cleanval) + ")"
  if cleanval is None:
    return ""
  return cleanval

def main():
  repl()


if __name__ == "__main__": #idk people do this ig
  main()