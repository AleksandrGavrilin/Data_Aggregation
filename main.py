from telebot.async_telebot import AsyncTeleBot
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime
import json

bot = AsyncTeleBot()

mongo_url = 'mongodb://localhost:27017'
mongo_db_name = 'DataDB'
mongo_collection_name = 'sample_collection'
collection_path = 'DB_files/sample_collection.bson'


# Aggregation of data based on the following input data:
# date, time, and method of data output (month, day or hour).
async def process_aggregation(dt_from, dt_upto, group_type):
    client_db = AsyncIOMotorClient(mongo_url)
    db = client_db[mongo_db_name]
    collection = db[mongo_collection_name]

    if group_type == 'hour':
        pipeline = [
            {
                '$match': {
                    'dt': {
                        '$gte': dt_from,
                        '$lte': dt_upto
                    }
                }
            },
            {
                '$project': {
                    'value': 1,
                    'dt': 1,
                    'date_part': {
                        '$dateToString': {
                            'format': '%Y-%m-%dT%H:00:00',
                            'date': '$dt',
                            'timezone': 'UTC'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$date_part',
                    'total_value': {'$sum': '$value'}
                }
            },
            {
                '$sort': {
                    '_id': 1
                }
            }
        ]
    elif group_type == 'day':
        pipeline = [
            {
                '$match': {
                    'dt': {
                        '$gte': dt_from,
                        '$lte': dt_upto
                    }
                }
            },
            {
                '$fill':
                 {
                     'output':
                {
                    "value": {'value': 0},
                }
                 }
        },
            {
                '$project': {
                    'value': 1,
                    'dt': 1,
                    'date_part': {
                        '$dateToString': {
                            'format': '%Y-%m-%dT00:00:00',
                            'date': '$dt',
                            'timezone': 'UTC'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$date_part',
                    'total_value': {'$sum': '$value'}
                }
            },

            {
                '$sort': {
                    '_id': 1
                }
            }
        ]
    elif group_type == 'month':
        pipeline = [
            {
                '$match': {
                    'dt': {
                        '$gte': dt_from,
                        '$lte': dt_upto
                    }
                }
            },
            {
                '$project': {
                    'value': 1,
                    'dt': 1,
                    'date_part': {
                        '$dateToString': {
                            'format': '%Y-%m-01T00:00:00',
                            'date': '$dt',
                            'timezone': 'UTC'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$date_part',
                    'total_value': {'$sum': '$value'}
                }
            },
            {
                '$sort': {
                    '_id': 1
                }
            }
        ]
    else:
        raise ValueError('Invalid group_type')

    # executing a request for data aggregation and generating a response
    cursor = collection.aggregate(pipeline)
    result = {
            'dataset': [],
            'labels': []
    }

    # Aggregation of data from a collection with transmission of information across several lists.
    async for record in cursor:
        result['dataset'].append(record['total_value'])
        result['labels'].append(record['_id'])
    return result

# Testing in local format without chat bot.
# async def main():
#     dt_from_str = '2022-09-01T00:00:00'
#     dt_upto_str = '2022-12-31T23:59:00'
#     group_type = 'month'
#
#     dt_from_obj = datetime.fromisoformat(dt_from_str)
#     dt_upto_obj = datetime.fromisoformat(dt_upto_str)
#     result = await process_aggregation(dt_from_obj.strftime('%Y-%m-%d %H:%M:%S'),
#                                        dt_upto_obj.strftime('%Y-%m-%d %H:%M:%S'),
#                                        group_type)
#     print(result)


# The test method executes a request to retrieve all documents from the collection and displays them on the console.
# If you see data on the console, your connection is working correctly.
# async def test_db_connection():
#     client_db = AsyncIOMotorClient(mongo_url)
#     db = client_db[mongo_db_name]
#     collection = db[mongo_collection_name]
#
#     cursor = collection.find()
#
#     async for document in cursor:
#         print(document)


# Functions of the relationship between the telegram bot and the project:
# Introduction for a new user.
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
        message_to_user = "Привет! Это тестовый бот для агрегации данных. Воспользуйтесь командой /help, чтобы узнать, как использовать бота."
        await bot.reply_to(message, message_to_user)
        if '/help':
            message_to_help = ('''Для произведения запроса на агрегацию данных ввидите запрос в формате:
                               {
                               "dt_from":"%Y-%m-%dT%H:%M:%S"
                               "dt_upto":"%Y-%m-%dT%H:%M:%S"
                               "group_type":("hour" or "day" or "month")
                               }''')
            await bot.reply_to(message, message_to_help)


@bot.message_handler(content_types=['text'])
async def handle_aggregate(message):
    try:
        text = message.text
        dictionary = json.loads(text)
    except ValueError as e:
        message_reply = "Ошибка формата данных!"
        await bot.send_message(message.chat.id, message_reply)
        return
    try:
        dt_from_str = dictionary['dt_from']
        dt_upto_str = dictionary['dt_upto']
        dt_from = datetime.strptime(dt_from_str, "%Y-%m-%dT%H:%M:%S")
        dt_upto = datetime.strptime(dt_upto_str, "%Y-%m-%dT%H:%M:%S")
    except KeyError as k:
        message_reply = "В запросе отсутствуют даты!"
        await bot.send_message(message.chat.id, message_reply)
        return
    except ValueError as e:
        message_reply = f"Строка даты должна быть формата YYYY-MM-DDTHH:MM:SS. Попробуйте еще раз. Ошибка: {e}"
        await bot.send_message(message.chat.id, message_reply)
        return
    try:
        group_type = dictionary['group_type']
    except KeyError as k:
        message_reply = "Отсутствует период группировки!"
        await bot.send_message(message.chat.id, message_reply)
        return
    if group_type not in {'hour', 'day', 'week', 'month'}:
        message_reply = "Данное значение группировки не в список допустимых значений ('hour', 'day', 'month')"
        await bot.send_message(message.chat.id, message_reply)
        return
    result = await process_aggregation(dt_from, dt_upto, group_type)
    response = {
        "dataset": result['dataset'],
        "labels": [label.replace(" ", "T") for label in result['labels']]
    }
    message_reply = json.dumps(response)

    await bot.send_message(message.chat.id, message_reply)


if __name__ == '__main__':
    # asyncio.run(main())
    # asyncio.run(test_db_connection())
    asyncio.run(bot.polling())
