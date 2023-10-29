from django.db import models

# Create your models here.
from django.db import models


class User(models.Model):

    # 个人空间名称
    namespace = models.CharField(max_length=100,verbose_name="个人空间名称")
    # Token
    token = models.CharField(max_length=50)


class Repository(models.Model):

    name = models.CharField(max_length=32,verbose_name='知识库名称')
    repo_id = models.CharField(max_length=20, verbose_name="知识库id")
    is_selected = models.BooleanField(verbose_name="是否勾选")
    is_download = models.BooleanField(verbose_name="是否下载",default=False)


class RepoCatalogue(models.Model):

    # 知识库id
    repo_id = models.CharField(max_length=20, verbose_name="知识库id")
    # 文章标题
    title = models.CharField(max_length=100, verbose_name="文章标题")
    # uuid
    uuid = models.CharField(max_length=20, verbose_name="uuid,唯一值")
    # 上一节点
    prev_uuid = models.CharField(max_length=20, null=True,blank=True, verbose_name="上一节点值")
    # 下一节点
    sibling_uuid = models.CharField(max_length=20, null=True, blank=True, verbose_name="下一节点值")
    # 父节点
    parent_uuid = models.CharField(max_length=20,  null=True, blank=True, verbose_name="父节点值")
    # 子节点
    child_uuid = models.CharField(max_length=20, null=True, blank=True, verbose_name="子节点值")
    # url
    url = models.CharField(max_length=20, verbose_name="拼接路径URL")


class Wiki_Detail(models.Model):
    # 知识库id
    slug = models.CharField(max_length=20, verbose_name="文档url")
    # 内容
    content = models.TextField(verbose_name='内容')
