import psutil


class ProcessName:

    def get_ios_process_name(self) -> list:
        '''
        Mac端获取正常运行的进程列表名称
        :return:
        '''
        process_names = []
        for process in psutil.process_iter():
            if process.ppid() == 1:
                if 'apple' not in process.name().lower():
                    process_names.append(process.name())
        return process_names

    def get_win_process_name(self):
        '''
        Windows端获取正常运行的进程列表名称
        :return:
        '''
        processes = {}
        for process in psutil.process_iter():
            try:
                pinfo = process.as_dict(attrs=['pid', 'name', 'username', 'memory_info', 'ppid'])
                processes[pinfo['pid']] = pinfo
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        process_names = []
        for pid, process in processes.items():
            process_names.append(process['name'])
        return list(set(process_names))

    def find_main_process_pid(self, process_name) -> None:
        '''
        通过进程名找到进程名的主进程pid
        :param process_name:
        :return:
        '''
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                parent = process.parent()
                if parent is None or parent.name() != process_name:
                    return process.info['pid']
        return None

    def get_child_pids(self, parent_id) -> list:
        '''
        通过主进程pid获取所有子进程pid
        :param parent_id:
        :return:
        '''
        parent_process = psutil.Process(parent_id)
        return [child_process.pid for child_process in parent_process.children]

    def get_pid_find_pid(self,pid) -> None:
        '''
        通过pid获取进程名
        :param pid:
        :return:
        '''
        try:
            process = psutil.Process(pid)
            name = process.name()
            return name
        except psutil.NoSuchProcess:
            return None
