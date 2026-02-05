# 服务器配置
import os

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# CORS 配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# API 配置
API_TITLE = "采集助手 API"
API_DESCRIPTION = "AI 驱动的数据采集系统"
API_VERSION = "1.0.0"

# 爬虫系统提示词
scrapy_agent_sys_prompt="""你是一个智能采集助手，可以根据用户的需求进行数据采集和数据提取。 
  1.根据输入的关键词和数据来源，采集相关数据。 
  2.可以使用检索工具搜索数据。 
  3.如果需要使用playwright进行数据采集，请使用playwright进行数据采集。
  4.采集社交账号数据，twitter、抖音、facebook等社交媒体平台上的账号数据。
  5.如果是比较复杂的采集任务，在采集完所有数据后，进行总结处理，如果用户没有指定总结方式，默认使用总结所有数据。
  """

# MCP 服务器配置
mcp_servers_config = {
        # "ddg-search": {
        #     "command": "uvx",
        #     "args": ["duckduckgo-mcp-server"],
        #     "env":{
        #         "https_proxy": "http://127.0.0.1:5081",
        #         "http_proxy": "http://127.0.0.1:5081"
        #     }
        # },
        # "playwright": {
        #     "command": "npx",
        #     "args": ["@playwright/mcp@latest"],
        #     "env":{
        #         "https_proxy": "http://127.0.0.1:5081",
        #         "http_proxy": "http://127.0.0.1:5081"
        #     }
        # }


        "minimax-coding-plan": {
            "command": "uvx" ,
            "args": ["minimax-coding-plan-mcp", "-y"],
            "env": {
                "MINIMAX_API_KEY": "sk-cp-R8tQCex8PrScJF87RNAwK61AhDBMcCWc2OXNiaSUCxAcT7qFGeWEnaHr5IiIYD-zCNK9ANXRQtrPQl_cQEKcALA3__yJ3fjqi63nwzTfJn1_-qmSeAp2kV0",
                "MINIMAX_API_HOST": "https://api.minimaxi.com"
            }

        }
    }


