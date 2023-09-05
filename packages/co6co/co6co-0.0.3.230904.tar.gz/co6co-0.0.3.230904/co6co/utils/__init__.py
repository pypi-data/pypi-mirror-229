#-*- coding:utf-8 -*-
import re

def isBase64(content:str)->bool:
    _reg="^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$"
    group=re.match(_reg,content)
    if group !=None:return True