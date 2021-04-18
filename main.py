import asyncio
from aiohttp import ClientSession
from lxml import html


async def crawler(queue):
    while True:
        topic = await queue.get()
        domain = 'https://news.google.com/'
        url = f'{domain}search?q={topic}'

        if queue.empty():
            await asyncio.sleep(10)
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
            dom_tree = html.fromstring(html_code)
            links = dom_tree.xpath('//a[@class="VDXfz"]/@href')

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
    for _ in range(1):
        task = asyncio.Task(crawler(queue))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())