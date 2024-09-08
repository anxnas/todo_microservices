from aiogram.fsm.context import FSMContext

async def save_user_token(state: FSMContext, token: str):
    await state.update_data(token=token)

async def get_user_token(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get('token')