import asyncio
from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor
from lxml import html


loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=8)


def parse_html(html_code):
    dom_tree = html.fromstring(html_code)
    links = dom_tree.xpath('//a[@class="VDXfz"]/@href')
    return links


async def crawler(queue):
    while True:
        topic = await queue.get()
        domain = 'https://news.google.com/'
        url = f'{domain}search?q={topic}'

        if queue.empty():
            break

        headers = {
            'User-Agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 
            YaBrowser/21.3.1.185 Yowser/2.5 Safari/537.36'''
        }

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(response.status, url)
                html_code = await response.text()

            links = await loop.run_in_executor(executor, parse_html, html_code)

            with open('result.txt', 'w') as f:
                for link in links:
                    f.write(f'{domain}{link[2:]}\n')


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
