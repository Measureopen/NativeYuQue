import re
import os
import time

import aiohttp
import asyncio
import aiosqlite
from urllib import parse



class YuQue1:

    # 初始化配置
    def __init__(self,namespace, token, repo_select):

        # 个人空间名称
        self.namespace = namespace
        # token
        self.token = token
        # 基础url
        self.url = "https://www.yuque.com/api/v2"

        # 添加请求头
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ExportMD",
            "X-Auth-Token": self.token
        }
        #
        self.repo = {}
        # 导出文件夹路径
        self.export_dir = '../static/yuque/'
        # 所选知识库
        self.repo_select = repo_select
        # db.sqlite3文件名称
        self.db_name = "db.sqlite3"

    # 发起请求
    async def _request(self, session, api):
        async with session.get(api, headers=self.headers) as resp:
            result = await resp.json()
            return result

    # 获取所有知识库
    async def get_repository(self):

        repository_url = self.url + f"/users/{self.namespace}/repos"
        async with aiohttp.ClientSession() as session:
            result = await self._request(session, repository_url)
            for repo in result.get('data'):
                repo_id = str(repo['id'])
                repo_name = repo['name']
                self.repo[repo_name] = repo_id

    # 获取单个知识库目录结构
    async def get_repo_toc(self,repo_id):
        toc_url = self.url + f"/repos/{repo_id}/toc"
        async with aiohttp.ClientSession() as session:
            result = await  self._request(session,toc_url)
            data_list = []
            for data in result["data"]:
                data_tuple = ()
                data_tuple +=(repo_id,)
                data_tuple += (data["title"],)
                data_tuple += (data["uuid"],)
                data_tuple += (data["prev_uuid"],)
                data_tuple += (data["sibling_uuid"],)
                data_tuple += (data["parent_uuid"],)
                data_tuple += (data["child_uuid"],)
                data_tuple += (data["url"],)
                data_list.append(data_tuple)
            return data_list

    # 获取单个知识库列表
    async def repository_doc(self,repo_id):
        doc_url = self.url + f"/repos/{repo_id}/docs"
        async with aiohttp.ClientSession() as session:
            result = await self._request(session,doc_url)
            docs = {}
            for doc in result.get('data'):
                title = doc['title']
                slug = doc['slug']
                docs[slug] = title
            return docs

    # 获取文章内容并保存
    async def download_md(self, repo_id, slug, repo_name, title):

        # 获取正文MarkDown内容
        body = await self.get_markdown_content(repo_id, slug)
        # 写入数据库
        await self.write_to_database(slug,body)
        # 语雀中的图片更换地址
        new_body, image_list = await self.to_local_image_src(body)

        if image_list:
            # 图片保存位置: ../static/yuque/<repo_name>/assets/<filename>
            save_dir = os.path.join(self.export_dir, repo_name, "assets")
            self.mkDir(save_dir)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *(self.download_image(session, image_info, save_dir) for image_info in image_list)
                )

        self.save(repo_name, title, new_body)

    # 获取正文MarkDown源代码
    async def get_markdown_content(self, repo_id, slug):

        content_url = self.url + f"/repos/{repo_id}/docs/{slug}"
        async with aiohttp.ClientSession() as session:
            result = await self._request(session,content_url)
            body = result['data']['body']
            body = re.sub("<a name=\".*\"></a>", "", body)  # 正则去除语雀导出的<a>标签
            body = re.sub("\x00", "", body)  # 去除不可见字符\x00
            body = re.sub("\x05", "", body)  # 去除不可见字符\x05
            body = re.sub(r'\<br \/\>!\[images.png\]', "\n![images.png]", body)  # 正则去除语雀导出的图片后紧跟的<br \>标签
            body = re.sub(r'\)\<br \/\>', ")\n", body)
            return body

    # 将md里的图片地址替换成本地的图片地址
    async def to_local_image_src(self, body):
        body = re.sub(r'\<br \/\>!\[images.png\]', "\n![images.png]", body)  # 正则去除语雀导出的图片后紧跟的<br \>标签
        body = re.sub(r'\)\<br \/\>', ")\n", body)  # 正则去除语雀导出的图片后紧跟的<br \>标签

        pattern = r"!\[(?P<img_name>.*?)\]" \
                  r"\((?P<img_src>https:\/\/cdn\.nlark\.com\/yuque.*\/(?P<slug>\d+)\/(?P<filename>.*?\.[a-zA-z]+)).*\)"
        repl = r"![\g<img_name>](./assets/\g<filename>)"
        images = [_.groupdict() for _ in re.finditer(pattern, body)]
        new_body = re.sub(pattern, repl, body)
        return new_body, images

    # 下载图片
    async def download_image(self, session, image_info: dict, save_dir: str):
        img_src = image_info['img_src']
        filename = image_info["filename"]

        async with session.get(img_src) as resp:
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(await resp.read())

    # 保存文章
    def save(self, repo_name, title, body):
        # 将不能作为文件名的字符进行编码
        def check_safe_path(path: str):
            for char in r'/\<>?:"|*':
                path = path.replace(char, parse.quote_plus(char))
            return path

        repo_name = check_safe_path(repo_name)
        title = check_safe_path(title)
        save_path = "../static/yuque/%s/%s.md" % (repo_name, title)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(body)

    # 创建文件夹
    def mkDir(self, dir):
        isExists = os.path.exists(dir)
        if not isExists:
            os.makedirs(dir)

    def get_dir_path(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(current_directory)
        resource_name = self.db_name
        # 拼接上一级目录下资源的路径
        resource_path = os.path.join(parent_directory, resource_name)
        return resource_path

    async def write_to_database(self, slug, content):
        # 获取db路径
        resource_path = self.get_dir_path()
        # 打开 SQLite 数据库连接
        async with aiosqlite.connect(resource_path) as db:
            # 插入数据
            await db.execute("INSERT INTO wiki_wiki_detail (slug,content) VALUES (?,?)", (slug, content))
            await db.commit()

    async def write_to_toc_database(self, data_list):
        # 获取db路径
        resource_path = self.get_dir_path()
        # 打开 SQLite 数据库连接
        async with aiosqlite.connect(resource_path) as db:
            # 插入数据
            await db.executemany("INSERT INTO wiki_repocatalogue (repo_id,title,uuid,prev_uuid,sibling_uuid,parent_uuid,child_uuid,url) VALUES (?,?,?,?,?,?,?,?)", data_list)
            await db.commit()

    async def run(self):
        # 获取知识库
        await self.get_repository()
        # 选择要下载的知识库
        repo_select = self.repo_select
        # 创建文件夹
        self.mkDir(self.export_dir)
        # 所选知识库创建文件夹
        for repo_name in repo_select:
            dir_path = self.export_dir + repo_name
            self.mkDir(dir_path)
            # 获取知识库repo_id
            repo_id = self.repo[repo_name]
            # 初始化各目录
            toc_list = await self.get_repo_toc(repo_id)
            await self.write_to_toc_database(toc_list)
            # 获取各目录下的文章
            docs = await self.repository_doc(repo_id)
            # 异步导出接口会报错，修改为同步导出，且每次导出等待50ms
            for slug in docs:
                time.sleep(0.05)
                title = docs[slug]
                await self.download_md(repo_id, slug, repo_name, title)
            print(f"{repo_name}下载完成")
        print("导出完成")



if __name__ == '__main__':
    export =YuQue1(namespace="输入你的namespace",token="输入你的token",repo_select=['输入你的知识库名称'])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(export.run())

