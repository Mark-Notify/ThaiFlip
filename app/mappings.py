# -*- coding: utf-8 -*-
from typing import Dict
import re

MapDict = Dict[str, str]

# EN -> TH (เกษมณี)
en2th: MapDict = {
    "q":"ๆ","w":"ไ","e":"ำ","r":"พ","t":"ะ","y":"ั","u":"ี","i":"ร","o":"น","p":"ย","[":"บ","]":"ล",
    "a":"ฟ","s":"ห","d":"ก","f":"ด","g":"เ","h":"้","j":"่","k":"า","l":"ส",";":"ว","'":"ง",
    "z":"ผ","x":"ป","c":"แ","v":"อ","b":"ิ","n":"ื","m":"ท",",":"ม",".":"ใ","/":"ฝ",
    "Q":"๐","W":"\"","E":"ฎ","R":"ฑ","T":"ธ","Y":"ํ","U":"๊","I":"ณ","O":"ฯ","P":"ญ",
    "{":"ฆ","}":"ฎ","A":"ฤ","S":"ฆ","D":"ฏ","F":"โ","G":"ฌ","H":"็","J":"๋","K":"ษ","L":"ศ",":":"ซ","\"":"ฅ",
    "Z":"(","X":")","C":"ฉ","V":"ฮ","B":"ฺ","N":"์","M":"ฒ","<":"ฦ",">":"ฦ","?":"ฃ",
    " ":" ",
    "0":"0","1":"1","2":"2","3":"3","4":"4","5":"5","6":"6","7":"7","8":"8","9":"9",
    "-":"-","_":"_","=":"=","+":"+","\\":"\\"
}
th2en: MapDict = {v: k for k, v in en2th.items()}

thai_range = re.compile(r"[\u0E00-\u0E7F]")

def _should_convert(word: str, mapping: MapDict, ratio: float = 0.6) -> bool:
    if not word:
        return False
    hits = sum(1 for ch in word if ch in mapping)
    return (hits / max(1, len(word))) >= ratio

def _convert_word(word: str, mapping: MapDict) -> str:
    return "".join(mapping.get(ch, ch) for ch in word)

def convert_mistyped_token(tok: str) -> str:
    if not tok.strip():
        return tok
    is_thai = bool(thai_range.search(tok))
    if is_thai:
        return _convert_word(tok, th2en) if _should_convert(tok, th2en) else tok
    else:
        return _convert_word(tok, en2th) if _should_convert(tok, en2th) else tok

def convert_text_auto(s: str) -> str:
    parts = re.split(r"(\s+)", s)
    return "".join(convert_mistyped_token(p) if not p.isspace() else p for p in parts)
