import asyncio
from aiohttp import ClientSession
from lxml import html


with open('topics.txt', 'r') as f:
    topics = [line.strip() for line in f if line]


async def crawler(topic, semaphore):
    async with semaphore:
        domain = 'https://news.google.com/'
        url = f'{domain}search?q={topic}'

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
            print(links)

            with open('result.txt', 'w') as f:
                for link in links:
                    f.write(f'{domain}{link[2:]}\n')


async def main():
    tasks = []
    sem = asyncio.Semaphore(value=1)

    for topic in topics:
        task = asyncio.Task(crawler(topic, sem))
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())