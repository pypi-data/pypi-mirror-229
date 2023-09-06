# -*- coding: utf-8 -*-
# @Time    : 2023/1/12 12:03
# @Author  : Quanfa
# @Desc    :

from .path_tool import MyPath
from .matlab import save_mat, load_mat
import torch as saver
import sys

def save(object, path, name, suffix):
    if suffix == 'Figure':
        object.savefig(path)
    if suffix == 'mat':
        save_mat(object, path, name)
    else:
        saver.save(object, path)
    print('save ',suffix,' at ', path)

class ScriptFileSaver:
    def __init__(self, script_file, locals, version: int=None):
        """
        A combination of database and saver in framework.

        :param root_path: local path
        :param date_mark:
        :param version:
        :param author:
        """
        self.locals = locals
        # region calculate version
        script_path = MyPath.from_file(script_file)
        relative_path = script_path.relative_to('myscripts').get_parent()
        script_name = MyPath.from_file(script_file).get_name()[:-3]
        root_path = script_path.my_root()
        local_path = root_path.cat('mylocal')
        save_path_parent = local_path.cat(relative_path).cat(script_name)
        save_path_parent.ensure()
        if version is None:
            version = len(save_path_parent.get_files(mark='s', list_r=True)) # version exists in save path
            if version == 0:
                version = 1
        # endregion
        self.local_path = save_path_parent.cat('s'+str(version))
        self.version = version
        self.local_path.ensure()
        self.root_path = root_path

        # region append project path to system
        # sys.path.append(root_path.cat('myclasses'))
        # sys.path.append(root_path.cat('myscripts'))
        sys.path.append(root_path)
        # endregion

    def path_of(self, file_name='auto_save_result', suffix='sus'):
        """

        :param file_name:
        :return:
        """
        if suffix == '':
            path = self.local_path.cat(file_name)
        else:
            path = self.local_path.cat(file_name + '.' + suffix)

        return path

    def save(self, name, suffix=None, path=None):
        """
        save object to location.

        :param object:
        :param name:
        :param suffix: sus, sci util saved; mat, matlab
        :return:
        """
        object = self.locals[name]
        if suffix is None:
            suffix = str(type(object)).split("'")[1].split('.')[-1]
        if path is None:
            path = self.path_of(name, suffix)
        else:
            path = MyPath(path)

        save(object, path, suffix, name)
        return path

    def load(self, name=None, suffix=None, object_sample=None, path=None):
        """
        load from specified version.
        :param name:
        :return:
        """
        if path is None:
            if suffix is None:
                path = self.local_path.    get_files(mark=name, list_r=True)[0]
                suffix = path.split('.')[-1]
            else:
                path = self.path_of(name, suffix)
        print('load ',suffix,' from ', path)
        if object_sample is not None:
            return object_sample.load(path)
        if suffix == 'mat':
            return load_mat(path)
        else:
            return saver.load(path)

    # def export(self, names=None, destination: str = None, export_name=None):
    #     """
    #     export saved files to destination.
    #     init params and zip files.
    #     saver scan all files in srcipt file path, so need hide exportation into a folder.
    #
    #     :param names: file names for exportation
    #     :param destination:
    #     :param export_name: export zip name
    #     :return:
    #     """
    #     import os
    #     # param init
    #     if destination is None:
    #         destination = self.local_path
    #     destination.ensure()
    #     if export_name is None:
    #         export_name = self.author + '_' + self.date_mark + self.version + '.zip'
    #     zip_path = destination.cat(export_name)
    #     if names is None:
    #         # zip
    #         with zipfile.ZipFile(zip_path, 'w') as zip:
    #             dirpath = self.__script_file_path
    #             for path, dirnames, filenames in os.walk(dirpath):  # 遍历文件
    #                 fpath = path.split('/mylocal/')[-1]  # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩（即生成相对路径）
    #                 for filename in filenames:
    #                     zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    #
    # def import_from(self, zip_path: str = None):
    #     """
    #     unzip to local is ok.
    #     """
    #     if zip_path is None:
    #         destination = self.local_path
    #         destination.ensure()
    #         export_name = self.author + '_' + self.date_mark + self.version + '.zip'
    #         zip_path = destination.cat(export_name)
    #
    #     with zipfile.ZipFile(zip_path, 'r') as zip:
    #         zip.extractall(self.local_path)
    #
    #     print('import from', zip_path)
    #
    # def end_script(self, __script_file__):
    #     """
    #     print end messages in terminal.
    #
    #     :return:
    #     """
    #     # # get information
    #     # script_file_path = MyPath.from_file(__script_file__)
    #     # script_name = script_file_path.split('/')[-1]
    #     # running_date = self.running_date
    #     # running_time = self.running_version
    #     #
    #     # # renew information
    #     # with open(script_file_path, 'r', encoding="utf-8") as file_old, open(script_file_path+'.tmp', 'w', encoding="utf-8") as file_new:
    #     #     skip = False
    #     #     for line in file_old:
    #     #         if not skip:
    #     #             if 'date = ' in line:
    #     #                 line = 'date = \'' + running_date + '\'\n'
    #     #             if 'version = ' in line:
    #     #                 line = 'version = \''+running_time+'\'\n'
    #     #                 skip = True
    #     #         file_new.write(line)
    #     # os.remove(script_file_path)
    #     # os.rename(script_file_path+'.tmp', script_file_path)
    #     # print
    #     print('script', script_name, 'finished its running in', running_date, 'at', running_time)