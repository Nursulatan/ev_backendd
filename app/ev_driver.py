from typing import Dict
class EVDriver:
    def execute(self, command: Dict) -> Dict:
        return {'status':'ok','executed':command}
ev=EVDriver()
