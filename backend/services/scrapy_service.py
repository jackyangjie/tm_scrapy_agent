from agent.scrapy_agent import get_scrapy_agent
from tools.excel_reader import read_excel


class ScrapyService:


    async def start(self, file_path):
        async with  get_scrapy_agent() as agent:
            excel_data = read_excel(file_path)
            for index, row in excel_data.iterrows():
                print(row["类型"], row["职务原文名"], row["职务中文名"], row["数据源"])
                await agent.run(row.to_dict())