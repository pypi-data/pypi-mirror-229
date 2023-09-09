# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
本文件实现了模型库hub接口封装

Authors: linyichong(linyichong@baidu.com)
Date:    2023/08/21
"""
import os
from pathlib import Path
from urllib.parse import quote
from aistudio_sdk.model_resources.abstract import APIResource, rewrite_token
from aistudio_sdk.api_requester import request_aistudio_hub, request_aistudio_git_download, request_aistudio_git_file_info
from aistudio_sdk.util import convert_to_dict_object, is_valid_host
from aistudio_sdk.util import err_resp
from aistudio_sdk import err_code
from aistudio_sdk import config


__all__ = [
    "create_repo",
    "download"
]


class Hub(APIResource):
    """Hub类"""
    OBJECT_NAME = "hub"

    def __init__(self):
        """初始化函数，从本地磁盘加载AI Studio认证令牌。
        
        Args:
            无参数。
        
        Returns:
            无返回值。
        """

        # 当用户已经设置了AISTUDIO_ACCESS_TOKEN环境变量，那么优先读取环境变量，忽略本地磁盘存的token
        # 未设置时才读存本地token
        if not os.getenv("AISTUDIO_ACCESS_TOKEN", default=""):
            cache_home = os.getenv("AISTUDIO_CACHE_HOME", default=os.getenv("HOME"))
            token_file_path = f'{cache_home}/.cache/aistudio/.auth/token'
            if os.path.exists(token_file_path):
                with open(token_file_path, 'r') as file:
                    os.environ["AISTUDIO_ACCESS_TOKEN"] = file.read().strip()

    @rewrite_token
    def create_repo(self, **kwargs):
        """
        创建一个repo仓库并返回创建成功后的信息。
        """
        # 参数检查
        if "repo_id" not in kwargs:
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            'params not valid.')
        if not os.getenv("AISTUDIO_ACCESS_TOKEN"):
            return err_resp(err_code.ERR_TOKEN_IS_EMPTY, 
                            'token have not been set.')
        if 'private' in kwargs and kwargs['private'] not in (True, False):
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            'params not valid.')
        for key in ['repo_id', 'model_name', 'license']:
            if key in kwargs:
                if type(kwargs[key]) != str:
                    return err_resp(err_code.ERR_PARAMS_INVALID, 
                                    'params not valid.')
                kwargs[key] = kwargs[key].strip()
                if not kwargs[key]:
                    return err_resp(err_code.ERR_PARAMS_INVALID, 
                                    'params not valid.')

        if 'desc' in kwargs \
                and type(kwargs['desc']) != str:
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            'params not valid.')

        params = {
            'repoType': 0 if kwargs.get('private') else 1,
            'repoName': kwargs['repo_id'],
            'modelName': kwargs['model_name'] if kwargs.get('model_name') else kwargs['repo_id'],
            'desc': kwargs.get('desc', ''),
            'license': kwargs['license'].strip() if kwargs.get('license') else 'Apache License 2.0'
        }
        resp = convert_to_dict_object(request_aistudio_hub(**params))
        if 'errorCode' in resp and resp['errorCode'] != 0:
            if "repo already created" in resp['errorMsg']:
                res = err_resp(err_code.ERR_REPO_EXISTS, 
                               resp['errorMsg'],
                               resp['errorCode'])
            else:
                res = err_resp(err_code.ERR_AISTUDIO_CREATE_REPO_FAILED, 
                               resp['errorMsg'],
                               resp['errorCode'])
            return res

        res = {
            'model_name': resp['result']['modelName'],
            'repo_id': resp['result']['repoName'],
            'private': True if resp['result']['repoType'] == 0 else False,
            'desc': resp['result']['desc'],
            'license': resp['result']['license']
        }
        return res

    @rewrite_token
    def download(self, **kwargs):
        """
        下载
        """
        # 参数检查
        str_params_not_valid = 'params not valid'
        if "repo_id" not in kwargs or "filename" not in kwargs:
            return err_resp(err_code.ERR_PARAMS_INVALID,
                            str_params_not_valid)

        for key in ['filename', 'repo_id', 'revision']:
            if key in kwargs:
                if type(kwargs[key]) != str:
                    return err_resp(err_code.ERR_PARAMS_INVALID, 
                                    'params not valid.')
                kwargs[key] = kwargs[key].strip()
                if not kwargs[key]:
                    return err_resp(err_code.ERR_PARAMS_INVALID, 
                                    'params not valid.')
        revision = kwargs['revision'] if kwargs.get('revision') else 'master'
        file_path = kwargs['filename']

        repo_name = kwargs['repo_id']
        if "/" not in repo_name:
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            str_params_not_valid)

        user_name, repo_name = repo_name.split('/')
        user_name = user_name.strip()
        repo_name = repo_name.strip()
        if not repo_name or not user_name:
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            str_params_not_valid)

        call_host = os.getenv("STUDIO_GIT_HOST", default=config.STUDIO_GIT_HOST_DEFAULT)
        if not is_valid_host(call_host):
            return err_resp(err_code.ERR_PARAMS_INVALID, 
                            'host not valid.')

        # 查询文件sha值
        # 构建查询url       
        url = f"{call_host}/api/v1/repos/{quote(user_name, safe='')}/{quote(repo_name, safe='')}/contents/{quote(file_path, safe='')}"
        if revision != 'master':
            url += f"?ref={quote(revision, safe='')}"

        info_res = request_aistudio_git_file_info(url)
        if 'error_code' in info_res and info_res['error_code'] != err_code.ERR_OK:
            return info_res

        # 构建source_path
        home = os.getenv("HOME")
        cache_home = os.getenv("AISTUDIO_CACHE_HOME", default=home)
        source_dir = Path(f"{cache_home}/.cache/aistudio/models/{repo_name}/blobs")
        file_sha = info_res['sha']
        source_path = Path(f"{source_dir}/{file_sha}")

        # 检查目标文件是否已下载
        if os.path.exists(source_path):
            print('文件已存在，跳过下载')
        else:
            print('开始下载')
            # 创建下载文件目录
            os.makedirs(source_dir, exist_ok=True)
            url = f"{call_host}/api/v1/repos/{quote(user_name, safe='')}/{quote(repo_name, safe='')}/media/{quote(file_path, safe='')}"
            if revision != 'master':
                url += f"?ref={quote(revision, safe='')}"
            download_res = request_aistudio_git_download(url, source_path)
            if 'error_code' in download_res and download_res['error_code'] != err_code.ERR_OK:
                return download_res

        # 构建软链接的路径
        commit_id = info_res['last_commit_sha']
        target_dir = Path(f"{cache_home}/.cache/aistudio/models/{repo_name}/snapshots/{revision}/{commit_id}")  
        target_path = Path(f"{target_dir}/{file_path}")

        # 删掉已经存在的软链接文件
        if os.path.exists(target_path):
            os.unlink(target_path)

        # 预创建软链接文件所在目录
        parsed_path = Path(file_path)
        prefix_path = parsed_path.parent
        os.makedirs(os.path.join(target_dir, prefix_path), exist_ok=True)

        # 创建符号链接（软链接）
        if os.name == "nt":  # Windows系统  
            # 使用不同的命令来创建目录链接和文件链接
            if os.path.isdir(source_path):
                os.system(f"mklink /D \"{target_path}\" \"{source_path}\"")
            else:
                os.system(f"mklink \"{target_path}\" \"{source_path}\"")
        else:  # 非Windows系统（如Linux）
            os.symlink(source_path, target_path) 

        return {'path': f"{target_path}"}


def create_repo(**kwargs):
    """
    创建
    """
    return Hub().create_repo(**kwargs)

def download(**kwargs):
    """
    下载
    """
    return Hub().download(**kwargs)
