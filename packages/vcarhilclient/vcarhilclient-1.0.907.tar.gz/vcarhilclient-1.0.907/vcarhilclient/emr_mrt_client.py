
import json,time
import shutil
import uuid
import os ,sys
emr_r=os.path.abspath(os.path.dirname(__file__))
rootpath_=os.path.split(emr_r)[0]
sys.path.append(rootpath_)
from vcarhilclient.kunyi_util import *
from vcarhilclient.kunyi_mrt import mrt_client
from vcarhilclient.mrt_client_Logger import _handle_log
from vcarhilclient.kunyi_project import hil_project

class Emr_mrt_client(mrt_client):

    def __init__(self,emr_path, host, server_name = None, managerment_port=8888, push_port=8889, subscription_port=8890):
        super().__init__(host, server_name, managerment_port, push_port,subscription_port)
        self.mrt_clien_Log = _handle_log(os.path.join(emr_r,"Log"))
        self._emr_path = emr_path
        self._emrInfo,self._temp_dir = self._get_proinfo_forEmrPath()

    def _close_env_by_name(self, envName):
        is_env_exists = self.is_env_exists(envName)
        if is_env_exists:
            ec = self.stop_test(envName)
            if ec.value != 0:
                self.mrt_clien_Log.error("End test fail due to %s" % (ec.get_name()))
                return False
            rc = self.delete_test_env(envName)
            if rc.value != 0:
                self.mrt_clien_Log.error("Delete test env %s fail, rc is %s " % (envName, str(rc.value)))
                return False
            else:
                return True
        else:
            self.mrt_clien_Log.warning(f"{envName} not exit!")
            return False

    def close_env_all_of_Em_project(self):
        if len(self.emr_env_names) == 0:
            self.mrt_clien_Log.warning("The current object has no experiments to destroy ")
            return
        for emr_envName,env in self.emr_env_names.items():
            re = self._close_env_by_name(env)
            if re:
                self.mrt_clien_Log.info(f"close env:{env} success!")
            else:
                self.mrt_clien_Log.error(f"close env:{env} failed!")

    def _get_proinfo_forEmrPath(self):
        emrPath = self._emr_path
        '''
        :param emrPath: emr file Path
        :return: [ProjectFilePath;MappingFilePath;EnvironmentName] ;TestBenchLocation
        '''
        cur_dir = os.path.dirname(os.path.abspath(emrPath))
        with open(emrPath) as emr_file:
            try:
                emr_json = json.load(emr_file)
            except:
                self.mrt_clien_Log.error("ipr is not a valid json file")
                raise Exception("ipr is not a valid json file")

            envInfos = []
            self.emr_env_names = {}
            self.emr_env_iprs = {}
            code = uuid.UUID(int=uuid.getnode()).hex[-12:]
            pro_name = os.path.basename(emrPath).replace(".emr", "")
            for i in emr_json["EnvironmentList"]:
                envInfo = []
                ProjectFilePath = i["ProjectFilePath"]
                MappingFilePath = i["MappingFilePath"]
                EnvironmentName = f"{code}_{pro_name}_{i['EnvironmentName']}"
                emr_env_name = i['EnvironmentName']
                envInfo.append(EnvironmentName)
                envInfo.append(os.path.join(cur_dir, ProjectFilePath))
                envInfo.append(os.path.join(cur_dir, MappingFilePath))
                envInfos.append(envInfo)
                self.emr_env_names[emr_env_name] = EnvironmentName
                self.emr_env_iprs[emr_env_name] = os.path.join(cur_dir, ProjectFilePath)

        return envInfos,os.path.join(cur_dir,".em/EEProject/.publish")

    def load_env_for_EmProject(self, is_startEnv=True, is_destoryEnv_ifExist=False):

        temp_dir = self._temp_dir
        if not os.path.exists(temp_dir):

            os.mkdir(temp_dir)
        shutil.rmtree(temp_dir)
        self.connet()

        for env_name, ip_project_path, mapping_path in self._emrInfo:
            project = os.path.dirname(ip_project_path)
            is_env_exists = self.is_env_exists(env_name)
            if is_env_exists and is_destoryEnv_ifExist:
                self._close_env_by_name(env_name)
                is_env_exists = False
                time.sleep(1)
            if not is_env_exists:
                ec = self.create_test_env(env_name)
                if not (ec.value == 0):
                    msg = f"create test env {env_name} fail {ec.value}"
                    self.mrt_clien_Log.error(msg)
                    raise Exception(msg)
                self.mrt_clien_Log.info(f"create test env:{env_name} success!")
                ec, map_id = self.download_file(mapping_path)
                if ec.value != 0:
                    msg = f"download mapping file fail {ec.value}"
                    self.mrt_clien_Log.error(msg)
                    raise Exception(msg)
                ec = self.load_enviroment_interface_mapping(env_name, map_id)
                if ec.value != 0:
                    msg = f"load enviroment interface mapping fail {ec.value}"
                    self.mrt_clien_Log.error(msg)
                    raise Exception(msg)
                zipfile = os.path.join(temp_dir, env_name)
                env_build_path = kunyi_util.file_compress(project, zipfile)
                ec, file_id = self.download_file(env_build_path)
                time.sleep(1)
                if not (ec.value == 0):
                    msg = "Dispatch ip project to rtpc fail"
                    self.mrt_clien_Log.error(msg)
                    raise Exception(msg)
                while True:
                    value = mrt_client.dispatch_progress
                    if value >= 1:
                        if value > 1:
                            msg = "Dispatch ip project to rtpc fail in the middle"
                            self.mrt_clien_Log.error(msg)
                            raise Exception(msg)
                        ecc = self.load_test_resources_to_env(env_name, file_id)
                        if not (ecc.value == 0):
                            msg = "Load project in env %s fail" % (env_name)
                            self.mrt_clien_Log.error(msg)
                            raise Exception(msg)
                        self.mrt_clien_Log.info(("Load project in env:%s success!" % (env_name)))
                        break
            if is_startEnv:
                ec = self.start_test(env_name)
                if ec.value != 0:
                    msg = "Start test fail due to %s" % (ec.get_name())
                    self.mrt_clien_Log.error(msg)
                    raise Exception(msg)
                self.mrt_clien_Log.info(f"start env:{env_name} success!")

    def get_env_by_emr_envName(self,emr_envName):
        if len(self.emr_env_names)<1:
            return None

        if emr_envName in self.emr_env_names:
            return self.emr_env_names[emr_envName]
        else:
            return None

    def get_ipr_by_emr_envName(self,emr_envName):
        if len(self.emr_env_names)<1:
            return None

        if emr_envName in self.emr_env_iprs:
            return self.emr_env_iprs[emr_envName]
        else:
            return None

    def get_project_by_emr_envName(self,emr_envName):
        if len(self.emr_env_names)<1:
            return None
        pro = hil_project(self.get_ipr_by_emr_envName(emr_envName))
        return pro


    def get_signal_Type_itemCount_structName_structDetail(self,emr_envName, instance_name,portType,port_name):
        '''
        :param env_name:
        :param instance_name:
        :param portType: inputport, outputport, measurement, calibration
        :param port_name:
        :return:
        '''

        pro = self.get_project_by_emr_envName(emr_envName)
        env_pro_name = self.get_env_by_emr_envName(emr_envName)
        signal_type,item_count,st_id,struct_name = pro.get_dataType_itemcount(instance_name,portType,port_name)
        struct_detail = pro.get_struct_detail(instance_name,struct_name)

        return env_pro_name,signal_type,item_count,struct_detail

    def write_input_port_value(self, emr_envName, instance_name, port_name, signal_value,**sub_struct_detail):

        portType = "inputport"
        env_pro_name, signal_type, item_count, struct_detail = \
            self.get_signal_Type_itemCount_structName_structDetail(emr_envName, instance_name,portType,port_name)
        return self.set_port_value(env_pro_name, instance_name, port_name,
                                   signal_type, signal_value, mrt_port_type_t.MRT_INPUT_PORT,
                                   item_count, struct_detail, **sub_struct_detail)

    def read_input_port_value(self, emr_envName, instance_name, port_name,**sub_struct_detail):

        portType = "inputport"
        env_pro_name, signal_type, item_count, struct_detail = \
            self.get_signal_Type_itemCount_structName_structDetail(emr_envName, instance_name, portType, port_name)
        return self.get_port_value(env_pro_name, instance_name, port_name,
                                   mrt_port_type_t.MRT_INPUT_PORT, signal_type, item_count, struct_detail, **sub_struct_detail)

    def read_output_port_value(self, emr_envName, instance_name, port_name,**sub_struct_detail):

        portType = "outputport"
        env_pro_name, signal_type, item_count, struct_detail = \
            self.get_signal_Type_itemCount_structName_structDetail(emr_envName, instance_name, portType, port_name)
        return self.get_port_value(env_pro_name, instance_name, port_name,
                                   mrt_port_type_t.MRT_OUTPUT_PORT, signal_type, item_count, struct_detail, **sub_struct_detail)

