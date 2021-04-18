import asyncio
from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor
from lxml import html
from datetime import datetime
from aiopg.sa import create_engine
import sqlalchemy as sa
from db import connection, Links


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=8)


def parse_html(html_code):
    dom_tree = html.fromstring(html_code)
    links = dom_tree.xpath('//a[@class="VDXfz"]/@href')
    return links


async def crawler(queue):
    async with create_engine(**connection) as engine:
        async with ClientSession() as session:
            while not queue.empty():
                topic = await queue.get()
                domain = 'https://news.google.com/'
                url = f'{domain}search?q={topic}'

                headers = {
                    'User-Agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 
                    YaBrowser/21.3.1.185 Yowser/2.5 Safari/537.36'''
                }

                try:
                    async with session.get(url, headers=headers) as response:
                        status = response.status
                        print(status, url)
                        html_code = await response.text()

                    links = await loop.run_in_executor(executor, parse_html, html_code)

                except Exception as e:
                    print(f'Не удалось установить соединение с "{domain}" '
                          f'по поисковому запросу "{topic}". Ошибка {e}')

                async with engine.acquire() as conn:
                    for link in links:
                        data = {
                            'domain': domain,
                            'url': url,
                            'topic': topic,
                            'link': f'{domain}{link[2:]}',
                            'datetime': datetime.now(),
                            'response': status
                        }

                    query = Links.insert().values(**data)
                    await conn.execute(query)

                # Save in results file
                # with open('result.txt', 'w') as f:
                #     for link in links:
                #         f.write(f'{domain}{link[2:]}\n')


async def main():
    with open('topics.txt', 'r') as f:
        topics = [line.strip() for line in f if line]

    queue = asyncio.Queue()
    for topic in topics:
        await queue.put(topic)

    tasks = []
    for _ in range(4):
        task = asyncio.Task(crawler(queue))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop.run_until_complete(main())
