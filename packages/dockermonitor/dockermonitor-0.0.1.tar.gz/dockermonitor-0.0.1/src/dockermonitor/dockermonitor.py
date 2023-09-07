import re
import threading
import subprocess
from datetime import date, timedelta


class DockerMonitor:
    def __init__(self, cache_interval=60):
        self.containers = {}
        self.cache_interval = cache_interval
        self.stop_thread = False
        self.cache_container_info()
        self.thread = threading.Thread(target=self._update_containers_periodically)
        self.cond_var = threading.Condition()
        self.thread.start()

    def _run_command(self, cmd_list):
        try:
            process = subprocess.Popen(
                cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Error executing {' '.join(cmd_list)}: {stderr.decode()}")
                return None
            return stdout.decode().splitlines()
        except Exception as e:
            print(f"Error executing {' '.join(cmd_list)}: {str(e)}")
            return None

    def cache_container_info(self):
        cmd = ["docker", "ps", "--format", "{{.ID}} {{.Image}} {{.Names}}"]
        output = self._run_command(cmd)
        if output:
            for line in output:
                id, image, names = line.split(None, 2)
                self.containers[id] = {"id": id, "image": image, "names": names}
        else:
            print("There are no running containers.")
            return None

    def get_cached_container_info(self):
        return self.containers

    def _update_containers_periodically(self):
        while not self.stop_thread:
            self.cache_container_info()
            with self.cond_var:
                if self.stop_thread:  # Check again before waiting
                    break
                self.cond_var.wait(self.cache_interval)

    def _get_target_containers(
        self, container_id=None, container_name=None, image_name=None
    ):
        if container_id is None and image_name is None and container_name is None:
            target_containers = list(self.containers.values())
            if target_containers == []:
                print("There are no running containers.")
                return []
        elif container_id:
            target_containers = [
                container
                for container in self.containers.values()
                if container["id"] == container_id
            ]
        elif container_name:
            target_containers = [
                container
                for container in self.containers.values()
                if container["names"] == container_name
            ]
        elif image_name:
            target_containers = [
                container
                for container in self.containers.values()
                if container["image"] == image_name
            ]

        if target_containers:
            return target_containers
        else:
            print("No matching containers.")
            return []

    def get_logs(
        self, container_id=None, log_line_count=10, container_name=None, image_name=None
    ):
        target_containers = self._get_target_containers(
            container_id, container_name, image_name
        )
        logs = {}
        for container in target_containers:
            cmd = [
                "docker",
                "logs",
                "-t",
                "--tail",
                f"{log_line_count}",
                container["id"],
            ]
            output = self._run_command(cmd)
            if output is not None:
                logs[container["id"]] = output
        return logs

    def show_containers(self):
        for container in self.containers.values():
            print(
                f"ID: {container['id']} | Image: {container['image']} | container_name: {container['names']}"
            )

    def show_logs(
        self,
        logs=None,
        container_id=None,
        log_line_count=10,
        container_name=None,
        image_name=None,
    ):
        if logs == None:
            print(
                "Logs are not provided. Ensure you retrieve them before calling this method."
            )
            return None

        target_containers = self._get_target_containers(
            container_id, container_name, image_name
        )
        target_logs = {
            container["id"]: logs.get(container["id"], [])
            for container in target_containers
        }

        for cid, log_lines in target_logs.items():
            print(
                f"\n##################\nLogs for container ID: {cid}\n##################"
            )
            for line in log_lines:
                print(line)

    def check_error_logs(
        self, logs=None, container_id=None, container_name=None, image_name=None
    ):
        error_keywords = ["error", "exception", "fail", "fatal"]
        if logs == None:
            print(
                "Logs are not provided. Ensure you retrieve them before calling this method."
            )
            return {}

        target_containers = self._get_target_containers(
            container_id, container_name, image_name
        )
        target_logs = {
            container["id"]: logs.get(container["id"], [])
            for container in target_containers
        }

        errors = {}
        for cid, log_lines in target_logs.items():
            error_lines = []
            for line in log_lines:
                if any(keyword in line.lower() for keyword in error_keywords):
                    error_lines.append(line)
            if error_lines:
                errors[cid] = error_lines
        if errors == {}:
            print("There is no error log.")
        return errors

    def stop(self):
        with self.cond_var:
            self.stop_thread = True
            self.cond_var.notify()
        self.thread.join()

    def get_logs_date_UTC(
        self,
        start_date=None,
        end_date=None,
        container_id=None,
        container_name=None,
        image_name=None,
    ):
        if start_date is None:
            start_date = date.today() - timedelta(1)
            start_date = start_date.strftime("%Y-%m-%d")
        if end_date is None:
            end_date = date.today()
            end_date = end_date.strftime("%Y-%m-%d")

        pattern = r"^\d{4}-\d{2}-\d{2}$"
        logs = {}
        if re.match(pattern, start_date) and re.match(pattern, end_date):
            change_start_date = start_date + "T00:00:00Z"
            change_end_date = end_date + "T23:59:59Z"
            target_containers = self._get_target_containers(
                container_id, container_name, image_name
            )
            for container in target_containers:
                cmd = [
                    "docker",
                    "logs",
                    "-t",
                    "--since",
                    change_start_date,
                    "--until",
                    change_end_date,
                    container["id"],
                ]
                output = self._run_command(cmd)
                if output is not None:
                    logs[container["id"]] = output
            return logs
        else:
            print("invalid value. Use 'YYYY-mm-dd' format")
            return None

    def get_logs_date_relative(
        self,
        hours=24,
        container_id=None,
        container_name=None,
        image_name=None,
    ):
        target_containers = self._get_target_containers(
            container_id, container_name, image_name
        )
        logs = {}
        for container in target_containers:
            cmd = [
                "docker",
                "logs",
                "-t",
                "--since",
                f"{hours}h",
                container["id"],
            ]
            output = self._run_command(cmd)
            if output is not None:
                logs[container["id"]] = output
        return logs


if __name__ == "__main__":
    docker_mon = DockerMonitor()
    docker_mon.get_cached_container_info()
    docker_mon.show_containers()
    logs = docker_mon.get_logs(log_line_count=5)
    docker_mon.show_logs(logs)
    logs_utc = docker_mon.get_logs_date_UTC()
    docker_mon.show_logs(logs_utc)
    logs_time = docker_mon.get_logs_date_relative()
    docker_mon.show_logs(logs_time)
    errors = docker_mon.check_error_logs(logs)
    docker_mon.stop()
