from db.get_db import redis_pool


class RedisRepository:

    async def save_quiz_answers_to_redis(self, user_id: int, company_id: int, quiz_id: int, question_id: int,
                                         user_answer: str, is_correct: bool):

        key = f"quiz_answer:{user_id}:{company_id}:{quiz_id}:{question_id}"

        await redis_pool.setex(key, 48 * 60 * 60, f"{user_answer}:{is_correct}")

    async def get_quiz_answer_from_redis(self, user_id: int, company_id: int, quiz_id: int, question_id: int):
        key = f"quiz_answer:{user_id}:{company_id}:{quiz_id}:{question_id}"
        data = await redis_pool.get(key)

        if data:
            user_answer, is_correct = data.split(":")
            return user_answer, is_correct == "True"

        return None, None
