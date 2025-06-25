import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from math import sqrt
from sqlalchemy.ext.asyncio import AsyncSession
from app.controller.crypto_market.point_of_entry_and_exit.models_build import build_lstm_model, build_mlp_model, build_gru_model
from app.controller.crypto_market.point_of_entry_and_exit.other import create_sequences
from app.model.db.queries.crypto_tickers import get_all_close_prices_by_symbol


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero_indices = y_true != 0
    if not np.any(non_zero_indices):
        return np.inf
    return np.mean(np.abs((y_true[non_zero_indices] - y_pred[non_zero_indices]) / y_true[non_zero_indices]))


async def point_of_entry_and_exit(symbol: str, trading_style: str, session: AsyncSession) -> str:
    result = await get_all_close_prices_by_symbol(session, symbol)
    closes = [r[0] for r in result.fetchall()]

    if len(closes) < 100:
        return "Недостатньо історичних даних для аналізу."

    closes = closes[-1_000:]
    closes = np.array(closes).reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled_closes = scaler.fit_transform(closes)

    x_x, y = create_sequences(scaled_closes, seq_length=50)
    x_x = x_x.reshape(x_x.shape[0], x_x.shape[1], 1)

    models = {
        "LSTM": build_lstm_model((x_x.shape[1], 1)),
        "GRU": build_gru_model((x_x.shape[1], 1)),
        "MLP": build_mlp_model((x_x.shape[1], 1)),
    }

    metrics = {}
    for name, model in models.items():
        print(f"Навчання моделі: {name}")
        model.fit(x_x, y, epochs=1, batch_size=32, verbose=1)
        preds = model.predict(x_x, verbose=1)

        mae = mean_absolute_error(y, preds)
        rmse = sqrt(mean_squared_error(y, preds))
        r2 = r2_score(y, preds)
        mape = mean_absolute_percentage_error(y, preds)

        metrics[name] = {
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "mape": mape
        }

    # Вибір найкращої моделі на основі суми MAE + RMSE + MAPE
    best_model_name = min(
        metrics,
        key=lambda k: metrics[k]["mae"] + metrics[k]["rmse"]
    )
    best_model = models[best_model_name]

    last_sequence = scaled_closes[-50:].reshape(1, 50, 1)
    predicted_price_scaled = best_model.predict(last_sequence, verbose=0)[0][0]
    predicted_price = scaler.inverse_transform([[predicted_price_scaled]])[0][0]

    current_price = float(closes[-1])
    direction = "🟢 LONG" if predicted_price > current_price else "🔴 SHORT"

    multiplier = {
        "scalping": 0.002,
        "intraday": 0.01,
        "swing": 0.03,
        "investing": 0.05,
    }.get(trading_style.lower(), 0.02)

    entry = current_price
    exit_point = predicted_price * (1 + multiplier) if direction == "🟢 LONG" else predicted_price * (1 - multiplier)

    result_text = f"{symbol.upper()} {direction}\n\n"
    result_text += f"Entry point: {entry:.2f}\n"
    result_text += f"Exit point: {exit_point:.2f}\n\n"
    result_text += (
        f"{best_model_name} "
        f"(R²: {metrics[best_model_name]['r2']:.6f}, "
        f"MAE: {metrics[best_model_name]['mae']:.6f}, "
        f"RMSE: {metrics[best_model_name]['rmse']:.6f}, "
        f"MAPE: {metrics[best_model_name]['mape']:.6f})"
    )

    return result_text
