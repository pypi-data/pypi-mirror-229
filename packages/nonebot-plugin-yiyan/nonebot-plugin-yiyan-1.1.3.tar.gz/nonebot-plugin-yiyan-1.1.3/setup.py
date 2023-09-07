from setuptools import setup

packages = \
['nonebot_plugin_yiyan']

install_requires = \
['nonebot2',  
'nonebot-adapter-onebot',
'requests']

package_data = \
{'': ['*']}

description = """百度文心一言 nonebot对话平台

基于zhenxun_bot平台开发的文心一言对话插件，稍加修改也可用在各类基于nonebot的机器人平台上。

配置：
https://github.com/barryblueice/nonebot-plugin-yiyan

API申请：
https://github.com/barryblueice/nonebot-plugin-yiyan/wiki/%E6%9C%BA%E5%99%A8%E4%BA%BA%E9%85%8D%E7%BD%AE%E6%95%99%E7%A8%8
"""

_setup = {
    'name': 'nonebot-plugin-yiyan',
    'version': '1.1.3',
    'description': 'Nonebot文心一言对话平台',
    'long_description': description,
    'author': 'barryblueice',
    'author_email': 'barryblueice@outlook.com',
    'maintainer': 'barryblueice',
    'maintainer_email': 'barryblueice@outlook.com',
    'url': 'https://github.com/barryblueice/nonebot-plugin-yiyan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
    
}

setup(**_setup)