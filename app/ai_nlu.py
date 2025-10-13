from typing import Tuple
KY={'жарык':'toggle_headlights','ач':'unlock_doors','кулпу':'lock_doors','заряд':'start_charging'}
RU={'фары':'toggle_headlights','открыть':'unlock_doors','закрыть':'lock_doors','заряд':'start_charging'}

def interpret(text:str, lang:str)->Tuple[str,dict]:
    low=text.lower(); table=KY if lang=='ky' else RU
    for k,i in table.items():
        if k in low: return i,{}
    return 'smalltalk',{'text':text}
