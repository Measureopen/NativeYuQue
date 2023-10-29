
from django.shortcuts import render
from django.http import JsonResponse
from .models import User,Repository,RepoCatalogue,Wiki_Detail
from django.db.models import Q

from util.yuque import YuQue
from util.yuque1 import YuQue1
from django.views.decorators.csrf import csrf_exempt

import json
import asyncio


def wiki_project(request):

    repo_list = []
    repo_query = Repository.objects.filter(is_download=True).values_list("name","repo_id")
    for repo in repo_query:
        repo_dict = {}
        repo_dict["name"] = repo[0]
        repo_dict["repo_id"] = repo[1]
        repo_list.append(repo_dict)

    return render(request,"repository.html",{"repo_list": repo_list})

def wiki_detail(request,detail_id):

    if request.GET.get("wiki_id"):
        url = request.GET.get("wiki_id")
        # 去查询数据库
        wiki_object = Wiki_Detail.objects.filter(slug=url).values("content").first()
        return render(request, "wiki.html",{'wiki_object': wiki_object, "repo_id": detail_id})

    return render(request, "wiki.html", {"repo_id": detail_id})

def save_settings(namespace,token):

    if namespace and token:
    # 查询数据库是否存在
        query = (Q(namespace=namespace) & Q(token=token))
        # 使用Q对象进行查询
        results = User.objects.filter(query)
        if not results:
            # 写入数据库
            User.objects.create(namespace=namespace,token=token)
        else:
            # 如果存在则更新
            update_id = list(results)[0].id
            User.objects.filter(id=update_id).update(namespace=namespace,token=token)

@csrf_exempt
def get_repo(request):

    if request.method == "GET":
        return render(request, "settings.html")
    else:
        data = request.POST
        # 获取到前端namespace,Token的值,调用接口返回个人所有知识库
        try:
            namespace,token = data["spaceName"],data["tokenValue"]
            # 将namespace,token 保存到数据库中
            save_settings(namespace,token)
            # 调用语雀API
            Y = YuQue(namespace=namespace, token=token)
            Y.get_repository()
            all_repo = Y.repo
            # 将个人数知识库写入数据库中
            for repo in all_repo:
                name = repo.get("name")
                repo_id = repo.get("repo_id")
                results = Repository.objects.filter(Q(repo_id=repo_id) & Q(name=name))
                if not results:
                    Repository.objects.create(name=name,repo_id=repo_id,is_selected=False)
            return JsonResponse({'status': True, 'data': all_repo})
        except Exception as e:
            print(e)
            return JsonResponse({'status': False})

@csrf_exempt
def repo_download(request):

    selected_values = request.POST.getlist('selected[]')
    if len(selected_values):
        # 更新数据库字段 勾选
        for selected_name in selected_values:
            Repository.objects.filter(name=selected_name).update(is_selected=True)

    repo_name_list = []
    # 下载知识库目录-已勾选
    repo_name_query = Repository.objects.filter(is_selected=True).values("name").all()
    for repo_name in repo_name_query:
        repo_name_list.append(repo_name.get("name"))
    # 获取数据库中space_name和token
    first_query = User.objects.first()
    namespace = first_query.namespace
    token = first_query.token
    # 初始化下载
    Y1 = YuQue1(namespace=namespace,token=token, repo_select=repo_name_list)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Y1.run())

    # 下载完成is_download 改为True | is_selected 是否勾选改为False
    for download_name in repo_name_list:
        Repository.objects.filter(name=download_name).update(is_selected=False, is_download=True)

    return JsonResponse({'status': True, 'data': "ok"})

def build_directory_tree(repo_id, parent_uuid, visited=None):

    if visited is None:
        visited = set()

    directory = []

    records = RepoCatalogue.objects.filter(repo_id=repo_id, parent_uuid=parent_uuid)

    for record in records:
        if record.uuid not in visited:
            visited.add(record.uuid)
            has_children = RepoCatalogue.objects.filter(repo_id=repo_id, parent_uuid=record.uuid).exists()
            item = {"text": record.title, "href": '?wiki_id='+record.url}
            if has_children:
                item["nodes"] = build_directory_tree(repo_id, record.uuid, visited)
            directory.append(item)

    return directory

def init_catalog(request,repo_id):

    # 根节点的UUID，通常是空值或根节点的UUID
    root_uuid = ""
    # 构建目录层次结构
    directory_structure = build_directory_tree(repo_id,root_uuid)
    # 如果需要将目录结构转换为JSON格式
    directory_json = json.dumps(directory_structure, ensure_ascii=False, indent=4)

    return JsonResponse({'status': True, "data": directory_json})

