import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.main import app, get_db
from app.config import settings
from app import crud, schemas
from unittest.mock import patch
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестовую базу данных в памяти
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        # Инициализируем FastAPICache с InMemoryBackend для тестов
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Удаляем все таблицы после завершения тестов
        Base.metadata.drop_all(bind=cls.engine)

    def setUp(self):
        # Очищаем базу данных перед каждым тестом
        with self.engine.connect() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
            connection.commit()

    @patch('app.backend_client.BackendClient.check_task_exists')
    def test_create_comment(self, mock_check_task_exists):
        mock_check_task_exists.return_value = True
        response = self.client.post(
            "/comments/",
            json={"content": "Test comment", "task_id": "1", "user_id": 1},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["content"], "Test comment")
        self.assertIn("id", data)

    def test_read_comments(self):
        response = self.client.get("/comments/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    @patch('app.backend_client.BackendClient.check_task_exists')
    def test_read_comment(self, mock_check_task_exists):
        mock_check_task_exists.return_value = True
        # Сначала создаем комментарий
        create_response = self.client.post(
            "/comments/",
            json={"content": "Test comment for reading", "task_id": "1", "user_id": 1},
        )
        create_data = create_response.json()
        comment_id = create_data["id"]

        # Теперь читаем этот комментарий
        response = self.client.get(f"/comments/{comment_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["content"], "Test comment for reading")

    @patch('app.backend_client.BackendClient.check_task_exists')
    def test_update_comment(self, mock_check_task_exists):
        mock_check_task_exists.return_value = True
        # Сначала создаем комментарий
        create_response = self.client.post(
            "/comments/",
            json={"content": "Test comment for updating", "task_id": "1", "user_id": 1},
        )
        create_data = create_response.json()
        comment_id = create_data["id"]

        # Теперь обновляем этот комментарий
        update_response = self.client.put(
            f"/comments/{comment_id}",
            json={"content": "Updated test comment", "task_id": "1", "user_id": 1},
        )
        self.assertEqual(update_response.status_code, 200)
        update_data = update_response.json()
        self.assertEqual(update_data["content"], "Updated test comment")

    @patch('app.backend_client.BackendClient.check_task_exists')
    def test_delete_comment(self, mock_check_task_exists):
        mock_check_task_exists.return_value = True
        # Сначала создаем комментарий
        create_response = self.client.post(
            "/comments/",
            json={"content": "Test comment for deleting", "task_id": "1", "user_id": 1},
        )
        create_data = create_response.json()
        comment_id = create_data["id"]

        # Теперь удаляем этот комментарий
        delete_response = self.client.delete(f"/comments/{comment_id}")
        self.assertEqual(delete_response.status_code, 200)

        # Проверяем, что комментарий действительно удален
        get_response = self.client.get(f"/comments/{comment_id}")
        self.assertEqual(get_response.status_code, 404)

    @patch('app.backend_client.BackendClient.check_task_exists')
    def test_read_task_comments(self, mock_check_task_exists):
        mock_check_task_exists.return_value = True
        # Создаем несколько комментариев для задачи
        self.client.post("/comments/", json={"content": "Task comment 1", "task_id": "2", "user_id": 1})
        self.client.post("/comments/", json={"content": "Task comment 2", "task_id": "2", "user_id": 1})

        response = self.client.get("/tasks/2/comments")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)


if __name__ == '__main__':
    unittest.main()