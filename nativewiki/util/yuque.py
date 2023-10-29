import requests
import re

class YuQue:

    # 初始化配置
    def __init__(self,namespace, token):

        # 个人空间名称
        self.namespace = namespace
        # token
        self.token = token
        # 基础url
        self.url = "https://www.yuque.com/api/v2"
        # 初始化请求
        self.session = requests.session()
        # 添加请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ExportMD",
            "X-Auth-Token": self.token
        })
        #
        self.repo = []

    # 发起请求
    def _request(self,api):
        res = self.session.get(api)
        result = res.json()
        return result

    # 获取所有知识库
    def get_repository(self):

        repository_url = self.url + f"/users/{self.namespace}/repos"
        result = self._request(repository_url)

        for repo in result.get('data'):
            repo_dict = {}
            repo_id = str(repo['id'])
            repo_dict["name"] = repo['name']
            repo_dict["repo_id"] = repo_id
            self.repo.append(repo_dict)

    # 获取单个知识库列表
    def repository_doc(self,repo_id):
        doc_url = self.url + f"/repos/{repo_id}/docs"
        result = self._request(doc_url)
        print(result)

    # 获取正文MarkDown源代码
    def get_markdown_content(self, repo_id, slug):

        content_url = self.url + f"/repos/{repo_id}/docs/{slug}"
        result = self._request(content_url)
        body = result.json()['data']['body']
        body = re.sub("<a name=\".*\"></a>", "", body)  # 正则去除语雀导出的<a>标签
        body = re.sub("\x00", "", body)  # 去除不可见字符\x00
        body = re.sub("\x05", "", body)  # 去除不可见字符\x05
        body = re.sub(r'\<br \/\>!\[images.png\]', "\n![images.png]", body)  # 正则去除语雀导出的图片后紧跟的<br \>标签
        body = re.sub(r'\)\<br \/\>', ")\n", body)


    # 获取单个知识库目录结构
    def get_toc(self,repo_id):
        toc_url = self.url + f"/repos/{repo_id}/toc"
        result = self._request(toc_url)
        return result




if __name__ == '__main__':
    Y = YuQue(namespace="输入你的namespace",token="输入你的token")
    Y.get_repository()

