from fastapi import APIRouter, Depends
from .models import Command, Macro, AssistantConfig
from .schemas import ConfigResponse
from .deps import get_current_admin
router = APIRouter(prefix='/admin', tags=['admin'])
DB={'config':AssistantConfig(),'commands':{},'macros':{}}
@router.get('/config', response_model=ConfigResponse)
def get_cfg(_:dict=Depends(get_current_admin)):
    return {'config':DB['config'],'commands':list(DB['commands'].values()),'macros':list(DB['macros'].values())}
@router.post('/config')
def set_cfg(cfg:AssistantConfig,_:dict=Depends(get_current_admin)):
    DB['config']=cfg; return {'ok':True}
@router.post('/commands')
def upsert(cmd:Command,_:dict=Depends(get_current_admin)):
    DB['commands'][cmd.id]=cmd; return {'ok':True}
@router.delete('/commands/{cid}')
def delete(cid:str,_:dict=Depends(get_current_admin)):
    DB['commands'].pop(cid,None); return {'ok':True}
@router.post('/macros')
def upsert_macro(m:Macro,_:dict=Depends(get_current_admin)):
    DB['macros'][m.id]=m; return {'ok':True}
