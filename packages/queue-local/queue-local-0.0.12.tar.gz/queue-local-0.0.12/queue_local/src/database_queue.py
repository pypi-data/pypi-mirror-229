import json
import os
from enum import Enum

import mysql.connector

from circles_local_database_python.connector import Connector
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from .our_queue import OurQueue

QUEUE_LOCAL_PYTHON_COMPONENT_ID = 155
QUEUE_LOCAL_PYTHON_COMPONENT_NAME = "queue_local/src/database_queue.py"
DEVELOPER_EMAIL = 'akiva.s@circ.zone'
TABLE = "queue_item"


class StatusEnum(Enum):
    NEW = 0
    RETRIEVED = 1


class DatabaseQueue(OurQueue):
    """A database-backed queue for managing tasks."""
    def __init__(self):
        self.logger = Logger(
            object={
                'component_id': QUEUE_LOCAL_PYTHON_COMPONENT_ID,
                'component_name': QUEUE_LOCAL_PYTHON_COMPONENT_NAME,
                'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
                'developer_email': DEVELOPER_EMAIL
            }
        )
        self.connection = Connector.connect("queue")
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()  # closes the cursor too

    def __enter__(self):
        # Return self for use within the context block. everything else is done inside __init__
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()  # Close the connection when exiting the context block

    def push(self, entry: dict) -> None:
        """
        Pushes a new entry to the queue.

        :param entry: Dictionary with the following format:
            {"item_description": "xyz", "action_id": 0, "parameters_json": {"a": 1, "b": 2}}
        """
        created_user_id = 0  # TODO
        self.logger.start("Pushing entry to the queue database", object={"entry": entry})
        if not isinstance(entry, dict) or any(x not in entry for x in ("item_description", "action_id", "parameters_json")):
            self.logger.warn("Invalid argument while pushing to the queue database")
            raise ValueError("You must provide item_description, action_id, and parameters_json inside `entry`")

        try:
            if isinstance(entry["parameters_json"], str):
                parameters_json = entry['parameters_json'].replace("'", '"')
            else:
                parameters_json = json.dumps(entry["parameters_json"])
            sql = f"INSERT INTO queue.{TABLE + '_table'}" \
                  f"(status_id, item_description, action_id, parameters_json, created_user_id) " \
                  f"VALUES (%s, %s, %s, %s, %s)"
            values = (StatusEnum.NEW.value, entry['item_description'], entry['action_id'], parameters_json, created_user_id)
            self.cursor.execute(sql, values)
            self.connection.commit()
            self.logger.end("Entry pushed to the queue database successfully")
        except Exception as e:
            self.logger.exception("Error while pushing entry to the queue database", object=e)
            raise

    def get(self, action_ids: tuple = None) -> dict:
        """
        Returns the first item from the queue (possibly considering specific actions) and marks it as taken.

        :param action_ids: Tuple of action IDs to consider (optional).
        :return: Dictionary representing the retrieved queue item.
        """
        updated_user_id = 0  # TODO
        self.logger.start("Getting and updating queue item from the queue database", object={"action_ids": action_ids})
        if action_ids is not None:
            if isinstance(action_ids, int):
                action_ids = (action_ids,)
            elif not isinstance(action_ids, tuple):
                try:
                    action_ids = tuple(action_ids)
                except TypeError as e:
                    self.logger.error("get_by_action_ids (queue database) invalid argument", object=e)
                    raise ValueError("`action_ids` must be a tuple")
            action_ids = action_ids if len(action_ids) != 1 else f"({action_ids[0]})"

        try:
            lock_sql = f"UPDATE queue.{TABLE + '_view'} " \
                         f"SET process_id = {os.getpid()} " \
                         f"WHERE process_id IS NULL AND status_id = {StatusEnum.NEW.value} " \
                         + (f"AND action_id IN {action_ids} " if action_ids else "") + \
                         "ORDER BY created_timestamp LIMIT 1"
            self.cursor.execute(lock_sql)
            self.connection.commit()

            self.cursor.execute(f"SELECT * FROM queue.{TABLE + '_view'} "
                                f"WHERE process_id = {os.getpid()} AND status_id = {StatusEnum.NEW.value}")
            queue_item = self._get_headers(self.cursor.fetchone())
            if queue_item:
                # Update the selected queue item
                update_sql = f"UPDATE queue.{TABLE + '_table'} " \
                             f"SET status_id = {StatusEnum.RETRIEVED.value}, updated_user_id = %s, updated_timestamp=CURRENT_TIMESTAMP() " \
                             f"WHERE queue_item_id = %s"
                values = (updated_user_id, queue_item['queue_item_id'])
                self.cursor.execute(update_sql, values)
                self.logger.end("Entry retrieved and updated from the queue database successfully",
                                object={k: str(v) for k, v in queue_item.items()})  # contains a datetime object
            else:
                self.logger.end("The queue is empty")
        except mysql.connector.Error as e:
            self.connection.connection.rollback()
            self.logger.exception("Error while getting and updating queue item from the queue database", object=e)
            raise
        finally:
            self.connection.commit()
        return queue_item

    def peek(self) -> dict:
        """Get the first item in the queue without changing it"""
        try:
            self.logger.start("Peeking queue item from the queue database")
            sql = f"SELECT * FROM queue.{TABLE + '_view'} WHERE status_id = {StatusEnum.NEW.value} " \
                  f"ORDER BY created_timestamp LIMIT 1"
            self.cursor.execute(sql)
            queue_item = self._get_headers(self.cursor.fetchone())
            self.logger.end("Entry peeked from the queue database successfully" if queue_item else "The queue is empty")
        except Exception as e:
            self.logger.exception("Error while peeking queue item from the queue database", object=e)
            raise
        return queue_item

    def _get_headers(self, queue_item: tuple) -> dict:
        column_names = [col[0] for col in self.cursor.description()]
        return dict(zip(column_names, queue_item or tuple()))
