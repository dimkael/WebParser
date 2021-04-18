import asyncio
from aiohttp import ClientSession
from lxml import html


keyword = 'python'


async def crawler(keyword):
    url = 'https://realpython.com'

    headers = {
        'User-Agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 
        YaBrowser/21.3.1.185 Yowser/2.5 Safari/537.36'''
    }

    async with ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(response.status, url)
            html_code = await response.text()
        dom_tree = html.fromstring(html_code)
        links = dom_tree.xpath('//div[@class="card border-0"]/a/@href')
        print(links)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler(keyword))