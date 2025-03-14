import os
import asyncio
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from stability_sdk import client
from stability_sdk.api import generation
from PIL import Image

API_TOKEN = ""
STABILITY_API_KEY = ""

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
stability_api = client.StabilityInference(
    key=STABILITY_API_KEY, 
    verbose=True,
)

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Отправь мне описание изображения, и я сгенерирую его для тебя!")

@dp.message(F.text)
async def generate_image(message: Message):
    await message.answer("Генерирую изображение, пожалуйста, подождите...")
    prompt = message.text

    try:
        answers = stability_api.generate(prompt=prompt, seed=42)
        
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    await message.answer("Ваш запрос был отклонен фильтром контента.")
                    return
                if artifact.type == generation.ARTIFACT_IMAGE:
                    image_data = artifact.binary
                    img = Image.open(io.BytesIO(image_data))
                    
                    temp_file = "temp_image.png"
                    img.save(temp_file, format="PNG")

                    await message.answer_photo(FSInputFile(temp_file))
                    return
        
        await message.answer("Не удалось сгенерировать изображение. Попробуйте другой запрос.")
    
    except Exception as e:
        await message.answer(f"Ошибка при генерации изображения: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())