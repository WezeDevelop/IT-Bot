import requests
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from aiogram import Bot, Router, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

CRYPTO_LIST = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "binancecoin": "BNB",
    "solana": "SOL"
}
from config import TOKEN


bot = Bot(token=TOKEN)
router = Router()


async def get_crypto_data(crypto_id):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
    response = requests.get(url)
    data = response.json()
    
    market_data = data['market_data']
    return {
        'name': data['name'],
        'symbol': data['symbol'].upper(),
        'current_price': market_data['current_price']['usd'],
        'price_change': {
            '1h': market_data['price_change_percentage_1h_in_currency']['usd'],
            '24h': market_data['price_change_percentage_24h_in_currency']['usd'],
            '7d': market_data['price_change_percentage_7d_in_currency']['usd']
        },
        'volume': market_data['total_volume']['usd'],
        'market_cap': market_data['market_cap']['usd']
    }

async def get_historical_data(crypto_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    return response.json()['prices']

def create_crypto_chart(data, prices):
    # Створюємо DataFrame з історичними даними
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    # Створюємо фігуру з двома частинами
    fig = plt.figure(figsize=(12, 8), facecolor='white')
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])
    # Верхня частина - таблиця
    ax1 = fig.add_subplot(gs[0])
    ax1.axis('off')
    # Дані для таблиці
    table_data = [
        ["", "Price", "1h", "24h", "7d", "24h Volume", "Market Cap"],
        [
            f"{data['name']} {data['symbol']}",
            f"${data['current_price']:,.2f}",
            f"{data['price_change']['1h']:+.1f}%",
            f"{data['price_change']['24h']:+.1f}%",
            f"{data['price_change']['7d']:+.1f}%",
            f"${data['volume']/1e9:.2f}B",
            f"${data['market_cap']/1e12:.2f}T"
        ]
    ]
    # Створюємо таблицю
    table = ax1.table(
        cellText=table_data,
        loc='center',
        cellLoc='center',
        colWidths=[0.25, 0.15, 0.1, 0.1, 0.1, 0.15, 0.15]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)
    # Нижня частина - графік
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(df.index, df['price'], color='blue', linewidth=2)
    ax2.set_title(f"{data['name']} Price Last 7 Days", pad=20)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Price (USD)')
    ax2.grid(True)
    # Зберігаємо графік
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

@router.message(F.text == "Курс криптовалют")
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    for crypto_id, symbol in CRYPTO_LIST.items():
        builder.add(InlineKeyboardButton(
            text=f"{crypto_id.capitalize()} {symbol}",
            callback_data=f"crypto_{crypto_id}")
        )
    builder.adjust(2)
    await message.answer(
        "Виберіть криптовалюту для відображення ціни:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("crypto_"))
async def show_crypto_info(callback: types.CallbackQuery):
    crypto_id = callback.data.split("_")[1]
    
    try:
        data = await get_crypto_data(crypto_id)
        prices = await get_historical_data(crypto_id, 7)
        chart = create_crypto_chart(data, prices)
        
        await callback.message.answer_photo(
            photo=types.BufferedInputFile(
                chart.read(),
                filename="crypto_chart.png"
            ),
            caption=f"📊 {data['name']} ({data['symbol']}) Price Analysis"
        )
        
    except Exception as e:
        await callback.message.answer(f"Error: {str(e)}")
    
    await callback.answer()

async def main():
    await router.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())