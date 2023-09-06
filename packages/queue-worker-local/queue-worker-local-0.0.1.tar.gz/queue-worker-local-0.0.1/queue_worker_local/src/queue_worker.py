import argparse
import json
import multiprocessing
import random
import subprocess
import sys
import time

from circles_local_database_python.connector import Connector
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from queue_local.database_queue import DatabaseQueue

QUEUE_WORKER_COMPONENT_ID = 159
QUEUE_WORKER_COMPONENT_NAME = 'queue_worker_local_python_package/src/queue_worker.py'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'


class QueueWorker:
    def __init__(self, action_ids: tuple) -> None:
        self.logger = Logger(object={'component_id': QUEUE_WORKER_COMPONENT_ID,
                                     'component_name': QUEUE_WORKER_COMPONENT_NAME,
                                     'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
                                     'developer_email': DEVELOPER_EMAIL})
        self.action_ids = action_ids

        # I don't want to use set_scheme because of the multiprocessing
        self.action_connection = Connector.connect("action")
        self.action_cursor = self.action_connection.cursor()
        self.queue_connection = Connector.connect("queue")
        self.queue_cursor = self.queue_connection.cursor()
        self.queue = DatabaseQueue()

    def execute(self, min_delay_after_execution: float, max_delay_after_execution: float,
                total_missions: int = sys.maxsize) -> None:
        """Execute tasks from the queue."""
        try:
            self.logger.start("START execute", object={
                "min_delay_after_execution": min_delay_after_execution,
                "max_delay_after_execution": max_delay_after_execution,
                "total_missions": total_missions})

            # Save actions in memory (shouldn't be too big)
            self.action_cursor.execute("SELECT id,filename,function_module,function_name FROM action.action_table")
            functions_by_action_id = {entry[0]: (entry[1], entry[2], entry[3]) for entry in self.action_cursor.fetchall()}

            for mission in range(total_missions):
                queue_item = self.queue.get(action_ids=self.action_ids)
                if not queue_item:
                    self.logger.info(f'The queue does not have more items of action_ids {self.action_ids}')
                    break
                try:
                    parameters = json.loads(queue_item["parameters_json"])
                except json.decoder.JSONDecodeError as e:
                    self.logger.exception(f'Wrong json format: {queue_item["parameters_json"]}', object=e)
                    raise
                formatted_params = ', '.join([f'{key}={repr(value)}' for key, value in parameters.items()])

                if queue_item['action_id'] not in functions_by_action_id:
                    self.logger.warn(f"No such action_id {queue_item['action_id']}")
                    self.push_back(queue_item)
                    break
                filename, function_module, function_name = functions_by_action_id[queue_item['action_id']]

                if filename.endswith('.py'):
                    filename = filename.replace(".py", "")
                    command = f'from {filename} import {function_module or function_name}\n' + \
                              (f'result = {function_module}().{function_name}(**{parameters})\n' if function_module
                               else f'result = {function_name}(**{parameters})\n') + \
                              f'print("return value:", result)'
                    self.logger.info(f'Executing the following python script: {command}')
                # elif...
                else:
                    self.logger.exception("Unsupported file extension " + filename + " for action " + str(queue_item['action_id']))
                    break
                result = subprocess.run(['python', '-c', command],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout = result.stdout
                stderr = result.stderr
                return_code = result.returncode
                return_message = "Success" if return_code == 0 else "Error"
                print(result.stdout, end="")  # for testing and debugging

                update_sql = "UPDATE queue.queue_item_table " \
                             "SET stdout = %s, stderr = %s, return_code = %s, return_message = %s " \
                             "WHERE queue_item_id = %s"
                values = (stdout, stderr, return_code, return_message, queue_item['queue_item_id'])
                self.queue_cursor.execute(update_sql, values)
                self.queue_connection.commit()
                if not stderr:
                    self.logger.info(f'Successfully executed {function_name}({formatted_params})')
                else:
                    self.logger.error(f'Error while executing {function_name}({formatted_params}):\n{stderr}')
                    self.push_back(queue_item)
                    break  # should we continue?
                time.sleep(random.uniform(min_delay_after_execution / 1000, max_delay_after_execution / 1000))
            self.logger.end("END execute_until_stopped")
        except Exception as e:
            self.logger.exception("An error occurred during execution:", object=e)

    def push_back(self, queue_item):
        """Push a queue item back to the queue."""
        # if we want to keep it at the top, we should update only the status_id
        self.queue.push(entry={k: queue_item[k] for k in ("item_description", "action_id", "parameters_json")})

    def close(self):
        self.action_connection.close()
        self.queue_connection.close()
        self.queue.close()


def execute_queue_worker(action_ids: tuple, min_delay_after_execution: float, max_delay_after_execution: float,
                         total_missions: int):
    queue_worker = QueueWorker(action_ids=action_ids)  # cannot share it between processes
    queue_worker.execute(min_delay_after_execution, max_delay_after_execution, total_missions)
    queue_worker.close()


def main():
    """See README.md"""
    parser = argparse.ArgumentParser(description='Queue Worker')

    parser.add_argument('-min_delay_after_execution', type=float)
    parser.add_argument('-max_delay_after_execution', type=float)
    parser.add_argument('-action_ids', type=int, nargs='+', help='List of action IDs')
    parser.add_argument('-total_missions', type=int, default=sys.maxsize, help='Number of missions to execute')
    parser.add_argument('-processes', type=int, default=1, help='Number of processes to start')

    args = parser.parse_args()

    if any(x is None for x in vars(args).values()):
        print(f"Usage: python {__file__} -min_delay_after_execution 0 -max_delay_after_execution 1 "
              f"-action_ids 1 2 4 -total_missions 100 -processes 1")
    else:
        processes = []
        try:
            for _ in range(args.processes):
                args = (tuple(args.action_ids), args.min_delay_after_execution, args.max_delay_after_execution,
                        args.total_missions // args.processes)
                process = multiprocessing.Process(target=execute_queue_worker, args=args)
                processes.append(process)

            # Start the processes
            for process in processes:
                process.start()

            # Wait for all processes to complete
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            for process in processes:
                process.terminate()


if __name__ == "__main__":
    main()
