import pandas as pd
import json
import glob


class Dataloader:

    def jsonl_2_dataframe(self, file_path) -> pd.DataFrame:
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        return pd.DataFrame(data)
    
    @staticmethod
    def user_id (user:dict) -> str:
        return user['_id']
    

    def load_newest_file(self, file_index:str):
        files = glob.glob(f'./WeiboSpider/output/*{file_index}*.jsonl')
        files.sort()
        file_path = files[-1]
        return self.jsonl_2_dataframe(file_path)