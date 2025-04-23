from fastapi import HTTPException, UploadFile
import shutil
import os
from pathlib import Path
import time
import aiofiles

def get_unique_filename(filename: str) -> str:
    """Создает уникальное имя файла, добавляя метку времени"""
    name, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    return f"{name}_{timestamp}{ext}"

async def save_uploaded_file(file: UploadFile, folder: str = "photos") -> str:
    """Сохраняет загруженный файл на диск и возвращает относительный путь для БД"""
    # Проверяем, что файл - изображение
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Загружаемый файл должен быть изображением")
    
    # Создаем уникальное имя файла
    unique_filename = get_unique_filename(file.filename)
    
    # Путь для сохранения файла
    upload_folder = Path("static") / folder
    upload_folder.mkdir(parents=True, exist_ok=True)
    
    # Полный путь к файлу
    file_path = upload_folder / unique_filename
    
    # Сохраняем файл асинхронно
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    
    # Относительный путь для БД
    relative_path = f"{folder}/{unique_filename}"
    return relative_path
