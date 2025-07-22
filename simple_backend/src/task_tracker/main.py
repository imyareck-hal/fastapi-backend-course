from fastapi import FastAPI
import json
import requests

app = FastAPI()


JSONBIN_URL = "https://api.jsonbin.io/v3/b/687f3b5e7b4b8670d8a53ab4"
HEADERS = {
    "X-Master-Key": "$2a$10$0UeL3zzjEX9DA7uZGmjaM.W.gkXkNw9UtgZJdIVwtSD0sQzhV6Mta",
    "Content-Type": "application/json"
}


class Task:
    def __init__(self, id_task: int, name_task: str, status_task: str):
        self.id = id_task
        self.name = name_task
        self.status = status_task

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status
        }


class TaskStorage:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        response = requests.get(JSONBIN_URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            self.tasks = data.get("record", [])
        else:
            self.tasks = []

    def save_tasks(self):
        payload = {"record": self.tasks}
        response = requests.put(JSONBIN_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("Ошибка при сохранении данных в jsonbin.io")

    def get_all_tasks(self):
        return self.tasks

    def add_task(self, task: Task):
        self.tasks.append(task.to_dict())
        self.save_tasks()

    def get_next_id(self):
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1

    def find_task_by_id(self, task_id: int):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def delete_task_by_id(self, task_id: int):
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                removed_task = self.tasks.pop(i)
                self.save_tasks()
                return removed_task
        return None


storage = TaskStorage()


@app.get("/tasks")
def get_tasks():
    return storage.get_all_tasks()

@app.post("/tasks")
def create_task(name: str = None, status: str = None):
    if name is None or status is None:
        return {"error": "Не указаны имя и(или) статус"}

    new_id = storage.get_next_id()
    new_task = Task(new_id, name, status)
    storage.add_task(new_task)
    return new_task.to_dict()

@app.put("/tasks")
def update_task(id_put: int, name: str = None, status: str = None):
    task = storage.find_task_by_id(id_put)
    if not task:
        return {"error": "id не найден"}

    if name is not None:
        task["name"] = name
    if status is not None:
        task["status"] = status

    storage.save_tasks()
    return task

@app.delete("/tasks")
def delete_task(id_delete: int):
    deleted_task = storage.delete_task_by_id(id_delete)
    if not deleted_task:
        return {"error": "Задача не найдена"}
    return {"status": "deleted", "task_info": deleted_task}