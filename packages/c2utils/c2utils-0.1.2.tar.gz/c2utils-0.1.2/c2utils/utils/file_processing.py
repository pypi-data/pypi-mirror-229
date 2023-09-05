# -*- coding: UTF-8 -*-
import concurrent.futures
import json
import logging
import os
import pickle
import zipfile
from json import JSONDecodeError
from pathlib import Path
from typing import List, NamedTuple, Optional, cast

import pandas as pd

logger = logging.getLogger(__name__)


class FileEncoding(NamedTuple):
    """A file encoding as the NamedTuple."""

    encoding: Optional[str]
    """The encoding of the file."""
    confidence: float
    """The confidence of the encoding."""
    language: Optional[str]
    """The language of the file."""


class FileProcessing:
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        self.args, self.kwargs = args, kwargs
        self._file_type = self._get_file_extension(self.file_path).lower()

        self.file_data = None

    @staticmethod
    def _get_file_extension(filename):
        _, extension = os.path.splitext(filename)
        return extension[1:]

    def _read_txt(self, encoding: Optional[str] = None, autodetect_encoding=False):
        try:
            with open(self.file_path, encoding=encoding) as f:
                self.file_data = f.readlines()
        except UnicodeDecodeError as e:
            if autodetect_encoding:
                detected_encodings = self._detect_file_encodings(self.file_path)
                for encoding in detected_encodings:
                    logger.debug(f"Trying encoding: {encoding.encoding}")
                    try:
                        with open(self.file_path, encoding=encoding.encoding) as f:
                            self.file_data = f.readlines()
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

    def _read_json(self, encoding='utf-8'):
        try:
            with open(self.file_path, encoding=encoding) as f:
                self.file_data = json.load(f)
        except JSONDecodeError:
            self.file_data = []
            with open(self.file_path, encoding=encoding) as f:
                for line in f.readlines():
                    self.file_data.append(json.loads(line))
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

    def _read_csv(self):
        self.file_data = pd.read_csv(self.file_path, **self.kwargs)

    def _read_excel(self):
        self.file_data = pd.read_excel(self.file_path, **self.kwargs)

    def _read_file(self):
        if self._file_type == "txt":
            self._read_txt(**self.kwargs)
        elif self._file_type == "json":
            self._read_json(**self.kwargs)
        elif self._file_type == "csv":
            self._read_csv()
        elif self._file_type in ["xlsx", "xls"]:
            self._read_excel()
        else:
            raise Exception("文件类型错误！目前只支持txt、json、csv、excel等类型。")

    def read_file_by_line(self):
        """
        按行读取文件（txt/json/csv/excel）
        :return:
        """
        if self.file_data is None:
            self._read_file()

        if self._file_type == "txt":
            for line in self.file_data:
                yield line.strip()
        elif self._file_type == "json":
            for d in self.file_data:
                yield d
        elif self._file_type == "csv":
            for d in self.file_data.to_dict(orient="records"):
                yield d
        elif self._file_type in ["xlsx", "xls"]:
            for d in self.file_data.to_dict(orient="records"):
                yield d
        else:
            raise Exception("文件类型错误！目前支持txt、json、csv、excel等类型。")

    def data2txt(self, data_list, mode='w'):
        """
        写入数据到txt文件
        :param mode:
        :param data_list:
        :return:
        """
        with open(self.file_path, mode, encoding='utf-8') as f:
            for line in data_list:
                f.write(str(line) + '\n')

    def check_file_exist(self):
        """
        检查文件是否存在
        :return:
        """
        return os.path.exists(self.file_path)

    def get_file_data_len(self):
        """
        获取文件总行数
        :return:
        """
        if self.file_data is None:
            self._read_file()

        if self._file_type in ["txt", "json"]:
            line_count = 0
            for _ in self.read_file_by_line():
                line_count += 1
            return line_count
        elif self._file_type in ["csv", "xlsx", "xls"]:
            return self.file_data.shape[0]
        else:
            raise Exception("文件类型错误！目前支持txt、json、csv、excel等类型。")

    def get_file_dir(self):
        """
        获取文件所在目录
        :return:
        """
        return Path(self.file_path).resolve().parent

    def get_file_size(self):
        """
        获取文件大小
        :return:
        """
        file_size = os.path.getsize(self.file_path) / 1024
        size_unit = "KB"

        if file_size > 1024:
            file_size = file_size / 1024
            size_unit = "MB"

        return f"{file_size:.3f} {size_unit}"

    @staticmethod
    def _detect_file_encodings(file_path: str, timeout: int = 5) -> List[FileEncoding]:
        import chardet

        def read_and_detect(file_path: str) -> List[dict]:
            with open(file_path, "rb") as f:
                rawdata = f.read()
            return cast(List[dict], chardet.detect_all(rawdata))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(read_and_detect, file_path)
            try:
                encodings = future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(
                    f"Timeout reached while detecting encoding for {file_path}"
                )

        if all(encoding["encoding"] is None for encoding in encodings):
            raise RuntimeError(f"Could not detect encoding for {file_path}")
        return [FileEncoding(**enc) for enc in encodings if enc["encoding"] is not None]


def check_file_contents(f1, f2, check=False):
    """
    比较两个文件内容是否一致
    :param check: 是否详细对比（按照字节对比，效率低下，默认为False）两个文件
    :param f1: 文件一
    :param f2: 文件二
    :return:
    """
    st1 = os.stat(f1)
    st2 = os.stat(f2)

    if check:
        if st1.st_size != st2.st_size:
            return False

        buf_size = 8 * 1024
        with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
            while True:
                b1 = fp1.read(buf_size)  # 读取指定大小的数据进行比较
                b2 = fp2.read(buf_size)
                if b1 != b2:
                    return False
                if not b1:
                    return True
    else:
        if st1.st_size != st2.st_size:
            return False
        else:
            return True


def print_file_directory_tree(current_path, count=0):
    """
    打印文件目录树
    :param current_path:
    :param count:
    :return:
    """
    if not os.path.exists(current_path):
        return
    if os.path.isfile(current_path):
        file_name = os.path.basename(current_path)
        print('\t' * count + '├── ' + file_name)
    elif os.path.isdir(current_path):
        print('\t' * count + '├── ' + current_path)
        path_list = os.listdir(current_path)
        for eachPath in path_list:
            print_file_directory_tree(current_path + '/' + eachPath, count + 1)


def unzip_file(zip_name, target_dir):
    """
    zip文件解压
    :param zip_name: 待解压的zip包名称
    :param target_dir: 解压路径
    :return:
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    file_zip = zipfile.ZipFile(zip_name, 'r')
    for file in file_zip.namelist():
        file_zip.extract(file, target_dir)
    file_zip.close()


def save_pickle(data, file_path):
    """
    保存成pickle文件
    :param data:
    :param file_path:
    :return:
    """
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(input_file):
    """
    读取pickle文件
    :param input_file:
    :return:
    """
    with open(input_file, 'rb') as f:
        data = pickle.load(f)
    return data


def save_json(data, file_path, ensure_ascii=False, indent=4):
    """
    保存成json文件
    :param data:
    :param file_path:
    :param ensure_ascii:
    :param indent:
    :return:
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)


def load_json(file_path):
    """
    加载json文件
    :param file_path:
    :return:
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
