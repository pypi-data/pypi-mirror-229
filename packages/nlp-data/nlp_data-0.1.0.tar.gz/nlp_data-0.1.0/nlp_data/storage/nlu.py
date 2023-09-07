from docarray.store.s3 import S3DocStore
from typing import Dict, List, Optional
from ..document import NLUDocList, NLUDoc
import boto3
from botocore.client import Config
import botocore


S3URL = "http://192.168.130.5:9005"

boto3.Session.client.__defaults__ = (
    "us-east-1",
    None,
    False,
    None,
    S3URL,
    "minioadmin",
    "minioadmin",
    None,
    Config(signature_version="s3v4"),
)



class NLUDocStore(S3DocStore):
    """对docarray本地文件存储的封装
    """
    
    @classmethod
    def list(cls, name_space: Optional[str] = None, show_table: bool = True) -> List[str]:
        """列出nlu bucket下的所有NLUDocLists
        """
        s3 = boto3.resource(service_name='s3',
                            region_name="us-east-1",
                            use_ssl=False,
                            endpoint_url=S3URL,
                            aws_access_key_id="minioadmin",
                            aws_secret_access_key="minioadmin",
                            config=Config(signature_version="s3v4"))
        s3_bucket = s3.Bucket('nlu')
        da_files = []
        for obj in s3_bucket.objects.all():
            if name_space is None:
                if obj.key.endswith('.docs'):
                    da_files.append(obj)
            else:
                if obj.key.endswith('.docs') and obj.key.startswith(name_space):
                    da_files.append(obj)
                    
        da_names = [f.key.split('.')[0] for f in da_files]

        if show_table:
            from rich import box, filesize
            from rich.console import Console
            from rich.table import Table

            table = Table(
                title=f'NLUDocLists in bucket s3://nlu',
                box=box.SIMPLE,
                highlight=True,
            )
            table.add_column('Name')
            table.add_column('Last Modified', justify='center')
            table.add_column('Size')

            for da_name, da_file in zip(da_names, da_files):
                table.add_row(
                    da_name,
                    str(da_file.last_modified),
                    str(filesize.decimal(da_file.size)),
                )

            Console().print(table)
        return da_names
    
    
    @staticmethod
    def delete(name: str, missing_ok: bool = True) -> bool:
        """Delete the [`DocList`][docarray.DocList] object at the specified bucket and key.

        :param name: The bucket and key to delete. e.g. my_bucket/my_key
        :param missing_ok: If true, no error will be raised if the object does not exist.
        :return: True if the object was deleted, False if it did not exist.
        """
        bucket = 'nlu'
        s3 = boto3.resource(service_name='s3',
            region_name="us-east-1",
            use_ssl=False,
            endpoint_url=S3URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"))
        object = s3.Object(bucket, name + '.docs')
        try:
            object.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                if missing_ok:
                    return False
                else:
                    raise ValueError(f'Object {name} does not exist')
            else:
                raise
        object.delete()
        return True
    
    
    @classmethod
    def pull(cls, name: str) -> NLUDocList[NLUDoc]:
        return NLUDocList[NLUDoc].pull(url=f's3://nlu/{name}')
    
    
    
    @classmethod
    def push(cls, docs: NLUDocList[NLUDoc], name: str) -> Dict:
        return NLUDocList[NLUDoc].push(docs, url=f's3://nlu/{name}')
    
    
    @classmethod
    def rename(cls, raw_name: str, change_name: str, list: bool = True):
        """Rename a NLUDocList on s3
        Args:
            raw_name (str): 文档列表的原始名称
            change_name (str): 文档列表的新名称
        """
        raw_docs = cls.pull(raw_name)
        _ = cls.push(raw_docs, change_name)
        if list:
            cls.list(change_name)
        return raw_docs