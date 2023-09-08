import time
from copy import deepcopy

import requests
from loguru import logger

from . import utils


class Zabbix(object):
    """Zabbix"""

    api: str | None = None
    auth: str | None = None
    debug: bool = False

    def __init__(self, api: str, username: str, password: str, debug: bool = False):
        ''' Initiation '''
        self.api = api
        self.auth = self.login(username=username, password=password)
        self.debug = debug

    def request(self, method: str, params: dict, log_prefix: str = '', **kwargs) -> dict | None:
        '''
        Request Data

            https://www.zabbix.com/documentation/current/en/manual/api#authentication

            id - an arbitrary identifier of the request
            id - 请求标识符, 这里使用UNIX时间戳作为唯一标示
        '''
        try:

            log_prefix += f'[Request]({method})'

            logger.info(f'{log_prefix}......')

            '''
            https://www.zabbix.com/documentation/current/en/manual/api#performing-requests
            The request must have the Content-Type header set to one of these values:
                application/json-rpc, application/json or application/jsonrequest.
            '''
            headers = {'Content-Type': 'application/json-rpc'}

            data: dict = {
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'auth': self.auth,
                'id': int(time.time())
            }

            logger.info(f'{log_prefix}data: {data}') if utils.v_true(self.debug, bool) else next

            response = requests.post(self.api, headers=headers, json=data, timeout=10, **kwargs)

            if response.status_code == 200:
                logger.success(f'{log_prefix}success')
                return response.json()
            else:
                logger.error(f'{log_prefix}failed')
                return None

        except Exception as e:
            logger.error(f'{log_prefix}failed')
            logger.exception(e) if utils.v_true(self.debug, bool) else logger.error(f'{log_prefix}{e}')
            return None

    def login(self, username: str, password: str) -> dict:
        """User Login"""
        try:

            log_prefix = '[Login]'
            logger.info(f'{log_prefix}......')

            response = self.request(
                method='user.login',
                params={'username': username, 'password': password},
                log_prefix=log_prefix
            )

            if utils.v_true(response, dict) and response.get('result'):
                logger.success(f'{log_prefix}success')
                return response['result']
            else:
                logger.error(f'{log_prefix}failed')
                return None

        except Exception as e:
            logger.error(f'{log_prefix}failed')
            logger.exception(e) if utils.v_true(self.debug, bool) else logger.error(f'{log_prefix}{e}')
            return None

    def logout(self) -> bool:
        """User Logout"""
        try:

            log_prefix = '[Logout]'
            logger.info(f'{log_prefix}......')

            response = self.request(method='user.logout', params={}, log_prefix=log_prefix)

            match True:
                case True if utils.v_true(response, dict) and response.get('result'):
                    logger.success(f'{log_prefix}success')
                    return True
                case True if utils.v_true(response, dict) and response.get('error'):
                    logger.error(f"{log_prefix}failed: {response.get('error',{}).get('data')}")
                    return False
                case _:
                    logger.error(f"{log_prefix}failed")
                    return False

        except Exception as e:
            logger.error(f'{log_prefix}failed')
            logger.exception(e) if utils.v_true(self.debug, bool) else logger.error(f'{log_prefix}{e}')
            return False

    def logout_and_exit(self):
        '''Logout and Exit'''
        try:
            self.logout()
        except Exception as e:
            logger.exception(e)
        finally:
            exit()

    def get_ids_by_template_name(self, name: str) -> list | None:
        '''
        Get ids by template name

            name: string/array
            example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']

            如果 name 为 '' (空), 返回所有 template id
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:
            response = self.request('template.get', {'output': 'templateid', 'filter': {'name': name}})
            if utils.v_true(response, dict) and utils.v_true(response['result'], list):
                return [i['templateid'] for i in response['result']]
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def get_ids_by_hostgroup_name(self, name: str) -> list | None:
        '''
        Get ids by hostgroup name

            name: string/array
            example: 'Linux servers' / ['Linux servers', 'Discovered hosts']

            如果 name 为 '' (空), 返回所有 hostgroup id
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:
            response = self.request('hostgroup.get', {'output': 'groupid', 'filter': {'name': name}})
            if utils.v_true(response, dict) and utils.v_true(response.get('result'), list):
                return [i['groupid'] for i in response['result']]
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def get_hosts_by_template_name(self, name: str, output: str = 'extend', **kwargs) -> list | None:
        '''
        Get hosts by template name

            name: string/array
            example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']

            如果 name 为 '' (空), 返回所有 host
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:
            response = self.request('template.get', {'output': ['templateid'], 'filter': {'host': name}})
            if utils.v_true(response, dict) and utils.v_true(response.get('result'), list):
                ids = [i['templateid'] for i in response['result']]
                hosts = self.request('host.get', {'output': output, 'templateids': ids, **kwargs})
                if utils.v_true(hosts, dict) and utils.v_true(hosts.get('result', []), list):
                    return hosts['result']
                else:
                    return None
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def get_hosts_by_hostgroup_name(self, name: str, output: str = 'extend', **kwargs) -> list | None:
        '''
        Get hosts by hostgroup name

            name: string/array
            example: 'Linux servers' / ['Linux servers', 'Discovered hosts']

            如果 name 为 '' (空), 返回所有 hosts
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:
            ids = self.get_ids_by_hostgroup_name(name)
            if ids == []:
                return None
            hosts = self.request('host.get', {'output': output, 'groupids': ids, **kwargs})
            if utils.v_true(hosts, dict) and utils.v_true(hosts.get('result', []), list):
                return hosts['result']
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def get_interface_by_host_id(self, hostid: str, output: str = 'extend') -> list | None:
        '''
        Get interface by host id

            hostids: string/array
            example: '10792' / ['10792', '10793']

            如果 name 为 '' (空), 则返回 []
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:
            response = self.request('hostinterface.get', {'output': output, 'hostids': hostid})
            if utils.v_true(response, dict) and utils.v_true(response.get('result'), list):
                return response['result']
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def available_hosts(self, hosts: list = []) -> tuple | None:
        '''可用服务器'''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:

            # 可用服务器, 不可用服务器
            available_hosts, unavailable_hosts = [], []

            # 服务器排查
            for host in hosts:
                if host['interfaces'][0]['available'] != '1':
                    unavailable_hosts.append(host['name'])
                else:
                    available_hosts.append(host)

            return available_hosts, unavailable_hosts

        except Exception as e:
            logger.exception(e)
            return None

    def get_history_by_item_key(self, hosts: list = [], time_from: int = 0, time_till: int = 0, item_key: str = '', data_type: int = 3) -> list | None:
        '''
        1. 根据 item key 获取 item id, 通过 item id 获取 history
        2. 根据 host 的 item id 和 history 的 item id 将数据提取为一个 history list
        3. 根据 history list 中的 clock 排序, 然后将 history list 整合到 host 中
        4. 返回包含有 item key, item id 和 history list 的 host 的 host list

        通过 Item Key 获取 Item history

            hosts: 主机列表
            time_from: 开始时间
            time_till: 结束时间
            item_key: Item Key
            data_type: 数据类型

        参考文档:

            https://www.zabbix.com/documentation/6.0/en/manual/api/reference/history/get

        history

            0 - numeric float
            1 - character
            2 - log
            3 - numeric unsigned
            4 - text

            Default: 3

        默认数据类型是 numeric unsigned (整数), 如果 history.get 返回的数据为 None, 有可能是 data_type 类型不对
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:

            match True:
                case True if not utils.v_true(hosts, list):
                    logger.error('ERROR!! hosts is not list or none')
                    return None
                case True if not utils.v_true(time_from, int):
                    logger.error('ERROR!! time_from is not integer or zero')
                    return None
                case True if not utils.v_true(time_till, int):
                    logger.error('ERROR!! time_till is not integer or zero')
                    return None
                case True if not utils.v_true(item_key, str):
                    logger.error('ERROR!! item_key is not string or none')
                    return None

            # 初始化变量
            # item_ids 获取历史数据时使用
            # item_history 历史数据集合, 最后返回
            item_ids: list = []
            item_history: list = []

            '''
            Deep Copy (拷贝数据)
            父函数的变量是 list 或者 dict 类型, 父函数将变量传递个子函数, 如果子函数对变量数据进行了修改, 那么父函数的变量的数据也会被修改
            为了避免出现这种问题, 可以使用 Deep Copy 拷贝一份数据, 避免子函数修改父函数的变量的数据
            '''
            hosts = deepcopy(hosts)

            # --------------------------------------------------------------------------------------------------

            # Get Item
            hostids = [i['hostid'] for i in hosts]
            item_params = {
                'output': ['name', 'itemid', 'hostid'],
                'hostids': hostids,
                'filter': {'key_': item_key}
            }
            items = self.request('item.get', item_params)

            # --------------------------------------------------------------------------------------------------

            # 因为 history 获取的顺序是乱的, 为了使输出和 hosts 列表顺序一致, 将 Item ID 追加到 hosts, 然后遍历 hosts 列表输出
            if utils.v_true(items, dict) and utils.v_true(items.get('result'), list):
                for host in hosts:
                    item: dict = next((item_object for item_object in items['result'] if host['hostid'] == item_object['hostid']), '')
                    if utils.v_true(item, dict) and item.get('itemid') != None:
                        host['itemkey'] = item_key
                        host['itemid'] = item['itemid']
                        item_ids.append(item['itemid'])
                        item_history.append(host)
            else:
                logger.error(f'ERROR!! item key {item_key} not find')
                return None

            # 如果 ID 列表为空, 则返回 None
            if not utils.v_true(item_ids, list):
                logger.error(f'ERROR!! item key {item_key} not find')
                return None

            # --------------------------------------------------------------------------------------------------

            # Get History
            history_params = {
                'output': 'extend',
                'history': data_type,
                'itemids': item_ids,
                'time_from': time_from,
                'time_till': time_till
            }
            history = self.request('history.get', history_params)

            # --------------------------------------------------------------------------------------------------

            if utils.v_true(history, dict) and utils.v_true(history.get('result'), list):

                for item in item_history:
                    # 根据 itemid 提取数据
                    item_history_data = [history_result for history_result in history['result'] if item['itemid'] == history_result['itemid']]
                    # 根据 clock 排序
                    item_history_data = utils.list_dict_sorted_by_key(item_history_data, 'clock')
                    # 整合数据
                    item['history'] = item_history_data

                return item_history

            else:

                logger.error('ERROR!! item history not find')
                return None

        except Exception as e:
            logger.exception(e)
            return None

    def get_history_by_interface(self, hosts: list = [], interfaces: list = [], time_from: int = 0, time_till: int = 0, direction: str = '') -> list | None:
        '''获取网卡历史数据'''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:

            match True:
                case True if not utils.v_true(hosts, list):
                    logger.error('ERROR!! hosts is not list or none')
                    return None
                case True if not utils.v_true(interfaces, list):
                    logger.error('ERROR!! interfaces is not list or none')
                    return None
                case True if not utils.v_true(time_from, int):
                    logger.error('ERROR!! time_from is not integer or zero')
                    return None
                case True if not utils.v_true(time_till, int):
                    logger.error('ERROR!! time_till is not integer or zero')
                    return None
                case True if not utils.v_true(direction, str):
                    logger.error('ERROR!! direction is not string or none')
                    return None

            # 创建一个只有 网卡名称 的 列表
            interfaces_names: set = set(interface['interface'] for interface in interfaces)

            # 创建一个 Key 为 网卡名称 的 dictionary
            interfaces_dict: dict = {key: [] for key in interfaces_names}

            # 汇集 相同网卡名称 的 IP
            for interface in interfaces:
                interfaces_dict[interface['interface']].append(interface['host'])

            # 获取历史数据
            history: list = []
            for key, value in interfaces_dict.items():
                hosts_by_ip = [host for v in value for host in hosts if v == host['interfaces'][0]['ip']]
                history += self.get_history_by_item_key(
                    hosts=hosts_by_ip,
                    time_from=time_from,
                    time_till=time_till,
                    item_key=f'net.if.{direction}["{key}"]',
                    data_type=3
                )

            # 根据 name 排序
            history = utils.list_dict_sorted_by_key(history, 'name')

            return history

        except Exception as e:
            logger.exception(e)
            return None

    def create_process_object(
        self,
        ips: list = [],
        name: str = '',
        item_type: int = 0,
        proc_name: str = '',
        proc_user: str = '',
        proc_cmdline: str = '',
        ignore_cpu: bool = False,
        ignore_mem: bool = False,
    ) -> bool:
        '''
        创建进程对象

            ips: IP列表
            name: 名称 (Item, Trigger, Graph 的名称前缀)
            item_type: Item Type (默认 0: Zabbix agent)
            proc_name: 进程名称
            proc_user: 进程用户
            proc_cmdline: 进程参数
            ignore_cpu: 是否创建 CPU Item 和 Graph
            ignore_mem: 是否创建 Memory Item 和 Graph

        参考文档:

            https://www.zabbix.com/documentation/6.0/en/manual/api/reference/item/object
            https://www.zabbix.com/documentation/6.0/en/manual/config/items/itemtypes/zabbix_agent#process-data

        type:

            0 - Zabbix agent;
            2 - Zabbix trapper;
            3 - Simple check;
            5 - Zabbix internal;
            7 - Zabbix agent (active);
            9 - Web item;
            10 - External check;
            11 - Database monitor;
            12 - IPMI agent;
            13 - SSH agent;
            14 - Telnet agent;
            15 - Calculated;
            16 - JMX agent;
            17 - SNMP trap;
            18 - Dependent item;
            19 - HTTP agent;
            20 - SNMP agent;
            21 - Script

        value_type:

            0 - numeric float;
            1 - character;
            2 - log;
            3 - numeric unsigned;
            4 - text.

        测试:

            zabbix_get -s 47.109.22.195 -p 10050 -k 'proc.num[java,karakal,,server.port=8011]'
            zabbix_get -s 47.109.22.195 -p 10050 -k 'proc.cpu.util[java,karakal,,server.port=8011]'
            zabbix_get -s 47.109.22.195 -p 10050 -k 'proc.mem[java,karakal,,server.port=8011,rss]'
            zabbix_get -s 47.109.22.195 -p 10050 -k 'proc.mem[java,karakal,,server.port=8011,pmem]'

            Memory used (rss) 的值除以 1024 就和 Zabbix Web 显示的一样了

        创建 Item:

            Number of processes 进程数量
            CPU utilization     CPU使用率
            Memory used (rss)   内存使用量
            Memory used (pmem)  内存使用率

            value type:

                Number of processes 3
                CPU utilization     0
                Memory used (rss)   0
                Memory used (pmem)  0

            获取 Item history 时, 如果返回结果为 None, 有可能是 value type 不一致

        创建 Trigger:

            Number of processes 如果进程数量为 0, 表示进程不存在 (应用或服务挂了)

        创建 Graph:

            CPU utilization CPU使用率
            Memory used (rss) 内存使用量
            Memory used (pmem) 内存使用率

            如果创建 Graph 后显示 [no data], 可以在 Items 中进入对应的 Item, 然后点击最下方的 Latest data
            在 Latest data 的右边的 Info 下面会有黄色感叹号, 将鼠标移动到上面, 可以看到相关的提示
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:

            match True:
                case True if not utils.v_true(ips, list):
                    logger.error('ERROR!! ips is not list or none')
                    return False
                case True if not utils.v_true(name, str):
                    logger.error('ERROR!! name is not string or none')
                    return False
                case True if not utils.v_true(proc_name, str):
                    logger.error('ERROR!! proc_name is not string or none')
                    return False

            # The number of processes
            # proc.num[<name>,<user>,<state>,<cmdline>,<zone>]
            proc_num_item_name: str = f'{name} Number of processes'
            proc_num_item_key: str = f'proc.num[{proc_name},{proc_user},,{proc_cmdline}]'

            proc_num_trigger_name: str = f'{name} is down'

            # Process CPU utilization percentage
            # proc.cpu.util[<name>,<user>,<type>,<cmdline>,<mode>,<zone>]
            proc_cpu_util_item_name: str = f'{name} CPU utilization'
            proc_cpu_util_item_key: str = f'proc.cpu.util[{proc_name},{proc_user},,{proc_cmdline}]'

            # Memory used by process in bytes
            # https://www.zabbix.com/documentation/6.0/en/manual/appendix/items/proc_mem_notes
            # proc.mem[<name>,<user>,<mode>,<cmdline>,<memtype>]
            # pmem: 内存使用量百分比, 即 top 显示的百分比
            # rss: 内存使用量实际数值, 即 总内存 x pmem(百分比)
            # Value Type 要使用 numeric float, 即 0, 否则会报错:
            # Value of type 'string' is not suitable for value type 'Numeric (unsigned)'.
            proc_mem_rss_item_name: str = f'{name} Memory used (rss)'
            proc_mem_rss_item_key: str = f'proc.mem[{proc_name},{proc_user},,{proc_cmdline},rss]'

            proc_mem_pmem_item_name: str = f'{name} Memory used (pmem)'
            proc_mem_pmem_item_key: str = f'proc.mem[{proc_name},{proc_user},,{proc_cmdline},pmem]'

            # Create Item, Trigger, Graph
            for ip in ips:

                # Host Info
                hostinterface = self.request('hostinterface.get', {'filter': {'ip': ip}, 'selectHosts': ['host']})
                host = hostinterface['result'][0]['hosts'][0]['host']
                host_id = hostinterface['result'][0]['hostid']
                interface_id = hostinterface['result'][0]['interfaceid']

                # --------------------------------------------------------------------------------------------------

                # Number of processes

                # Create Item
                params = {
                    'name': proc_num_item_name,
                    'key_': proc_num_item_key,
                    'hostid': host_id,
                    'type': item_type,
                    'value_type': 3,
                    'interfaceid': interface_id,
                    'delay': '1m',
                    'history': '7d',
                    'trends': '7d'
                }
                _ = self.request('item.create', params)
                if isinstance(_, utils.NoneType):
                    logger.error('create process item error')
                else:
                    logger.success('create process item successful')

                # Create Trigger
                params = [
                    {
                        'description': proc_num_trigger_name,
                        'priority': '2',
                        'expression': f'last(/{host}/{proc_num_item_key})=0',
                        'manual_close': '1'
                    }
                ]
                _ = self.request('trigger.create', params)
                if isinstance(_, utils.NoneType):
                    logger.error('create process trigger error')
                else:
                    logger.success('create process trigger successful')

                # --------------------------------------------------------------------------------------------------

                # CPU utilization

                if ignore_cpu == False:

                    # Create Item
                    params = {
                        'name': proc_cpu_util_item_name,
                        'key_': proc_cpu_util_item_key,
                        'hostid': host_id,
                        'type': item_type,
                        'value_type': 0,
                        'interfaceid': interface_id,
                        'delay': '1m',
                        'history': '7d',
                        'trends': '7d'
                    }
                    _ = self.request('item.create', params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create cpu item error')
                    else:
                        logger.success('create cpu item successful')

                    # Item Info
                    item_params = {
                        'output': 'itemid',
                        'hostids': host_id,
                        'filter': {'key_': proc_cpu_util_item_key}
                    }
                    item = self.request('item.get', item_params)
                    item_id = item['result'][0]['itemid']

                    # Create Graph
                    graph_params = {
                        'name': proc_cpu_util_item_name,
                        'width': 900,
                        'height': 200,
                        'yaxismin': 0,
                        'yaxismax': 100,
                        'ymin_type': 1,
                        'ymax_type': 1,
                        'gitems': [{'itemid': item_id, 'color': '0040FF'}]
                    }
                    _ = self.request('graph.create', graph_params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create cpu graph error')
                    else:
                        logger.success('create cpu graph successful')

                # --------------------------------------------------------------------------------------------------

                # Memory used

                if ignore_mem == False:

                    # Memory used (rss)

                    # Create Item
                    params = {
                        'name': proc_mem_rss_item_name,
                        'key_': proc_mem_rss_item_key,
                        'hostid': host_id,
                        'type': item_type,
                        'value_type': 0,
                        'interfaceid': interface_id,
                        'delay': '1m',
                        'history': '7d',
                        'trends': '7d'
                    }
                    _ = self.request('item.create', params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create memory used (rss) item error')
                    else:
                        logger.success('create memory used (rss) item successful')

                    # Total memory
                    vm_params = {
                        'output': 'itemid',
                        'hostids': host_id,
                        'filter': {'key_': 'vm.memory.size[total]'}
                    }
                    vm_total = self.request('item.get', vm_params)
                    vm_total_itemid = vm_total['result'][0]['itemid']

                    # Item Info
                    item_params = {
                        'output': 'itemid',
                        'hostids': host_id,
                        'filter': {'key_': proc_mem_rss_item_key}
                    }
                    item = self.request('item.get', item_params)
                    item_id = item['result'][0]['itemid']

                    # Create Graph
                    # gitems 需要注意顺序
                    graph_params = {
                        'name': proc_mem_rss_item_name,
                        'width': 900,
                        'height': 200,
                        'graphtype': 1,
                        'gitems': [
                            {'itemid': item_id, 'color': '00FF00'},
                            {'itemid': vm_total_itemid, 'color': '1E88E5'}
                        ]
                    }
                    _ = self.request('graph.create', graph_params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create memory used (rss) graph error')
                    else:
                        logger.success('create memory used (rss) graph successful')

                    # --------------------------------------------------------------------------------------------------

                    # Memory used (pmem)

                    # Create Item
                    # Units: %
                    params = {
                        'name': proc_mem_pmem_item_name,
                        'key_': proc_mem_pmem_item_key,
                        'hostid': host_id,
                        'type': item_type,
                        'value_type': 0,
                        'interfaceid': interface_id,
                        'units': '%',
                        'delay': '1m',
                        'history': '7d',
                        'trends': '7d'
                    }
                    _ = self.request('item.create', params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create memory used (pmem) item error')
                    else:
                        logger.success('create memory used (pmem) item successful')

                    # Item Info
                    item_params = {
                        'output': 'itemid',
                        'hostids': host_id,
                        'filter': {'key_': proc_mem_pmem_item_key}
                    }
                    item = self.request('item.get', item_params)
                    item_id = item['result'][0]['itemid']

                    # Create Graph
                    graph_params = {
                        'name': proc_mem_pmem_item_name,
                        'width': 900,
                        'height': 200,
                        'graphtype': 1,
                        'yaxismin': 0,
                        'yaxismax': 100,
                        'ymin_type': 1,
                        'ymax_type': 1,
                        'gitems': [
                            {'itemid': item_id, 'color': '66BB6A'}
                        ]
                    }
                    _ = self.request('graph.create', graph_params)
                    if isinstance(_, utils.NoneType):
                        logger.error('create memory used (pmem) graph error')
                    else:
                        logger.success('create memory used (pmem) graph successful')

            return True

        except Exception as e:
            logger.exception(e)
            return False

    def create_tcp_port_check(self, ips: list, name: str, target_ip: str, target_port: int, item_type: int = 0) -> bool:
        '''
        创建进程对象

            ips: IP列表
            name: 名称 (Item, Trigger, Graph 的名称前缀)
            item_type: Item Type (默认 0: Zabbix agent)
            ip: IP地址
            port: 目标端口

        参考文档:

            https://www.zabbix.com/documentation/6.0/en/manual/api/reference/item/object
            https://www.zabbix.com/documentation/6.0/en/manual/config/items/itemtypes/zabbix_agent#network-data

        type:

            0 - Zabbix agent;
            2 - Zabbix trapper;
            3 - Simple check;
            5 - Zabbix internal;
            7 - Zabbix agent (active);
            9 - Web item;
            10 - External check;
            11 - Database monitor;
            12 - IPMI agent;
            13 - SSH agent;
            14 - Telnet agent;
            15 - Calculated;
            16 - JMX agent;
            17 - SNMP trap;
            18 - Dependent item;
            19 - HTTP agent;
            20 - SNMP agent;
            21 - Script

        value_type:

            0 - numeric float;
            1 - character;
            2 - log;
            3 - numeric unsigned;
            4 - text.

        测试:

            zabbix_get -s 10.26.20.141 -p 20050 -k 'net.tcp.port[10.25.182.10,20051]'

        创建 Item:

            TCP connection 进程数量

            value type:

                TCP connection 3

            获取 Item history 时, 如果返回结果为 None, 有可能是 value type 不一致

        创建 Trigger:

            TCP connection 结果如果为 0, 端口无法访问
        '''

        if self.auth == None:
            logger.error('not authorized')
            return None

        try:

            match True:
                case True if not utils.v_true(ips, list):
                    logger.error('ERROR!! ips is not list or none')
                    return False
                case True if not utils.v_true(name, str):
                    logger.error('ERROR!! name is not string or none')
                    return False
                case True if not utils.v_true(target_ip, str):
                    logger.error('ERROR!! ip is not string or none')
                    return False
                case True if not utils.v_true(target_ip, int):
                    logger.error('ERROR!! port is not integer or none')
                    return False

            # Checks if it is possible to make TCP connection to specified port.
            # net.tcp.port[<ip>,port]
            item_name = f'TCP connection: {name}'
            item_key = f'net.tcp.port[{target_ip},{target_port}]'
            trigger_name = f'Failed to connect to {target_ip} port {target_port}'

            # Create Item, Trigger
            for ip in ips:

                # Host Info
                hostinterface = self.request('hostinterface.get', {'filter': {'ip': ip}, 'selectHosts': ['host']})
                host = hostinterface['result'][0]['hosts'][0]['host']
                host_id = hostinterface['result'][0]['hostid']
                interface_id = hostinterface['result'][0]['interfaceid']

                # Create Item
                params = {
                    'name': item_name,
                    'key_': item_key,
                    'hostid': host_id,
                    'type': item_type,
                    'value_type': 3,
                    'interfaceid': interface_id,
                    'delay': '1m',
                    'history': '7d',
                    'trends': '7d'
                }
                _ = self.request('item.create', params)
                if isinstance(_, utils.NoneType):
                    logger.error('create item error')
                else:
                    logger.success('create item successful')

                # Create Trigger
                expression = f'last(/{host}/{item_key})=0'
                params = [
                    {
                        'description': trigger_name,
                        'priority': '2',
                        'expression': expression,
                        'manual_close': '1'
                    }
                ]
                _ = self.request('trigger.create', params)
                if isinstance(_, utils.NoneType):
                    logger.error('create trigger error')
                else:
                    logger.success('create trigger successful')

            return True

        except Exception as e:
            logger.exception(e)
            return False
