---
title: Forecasting the Price of Refined Sugar in the Philippines
summary: Modeling retail sugar prices through the 2022 inflation shock using ARIMAX and macroeconomic indicators.
disciplines:
  - data-science
  - research
year: 2025
technologies:
  - Python
  - Pandas
  - Matplotlib
  - Statsmodels
links:
  - label: GitHub
    url: https://github.com/LeinnarF/Math_Modeling_Research_ARIMAX
  - label: GitHub (Visualizations)
    url: https://github.com/LeinnarF/Sugar-Forecasting
---

## The Problem

Sugar is an essential commodity in the Philippines, present in nearly every household and serving as a core input for bakeries, food processors, and beverage manufacturers. When sugar prices shift, the effect cascades quickly across consumer budgets and small businesses. For most of the past decade, domestic refined sugar traded predictably near 50 pesos per kilogram. In 2022, however, a convergence of import delays, post-pandemic demand spikes, and global inflation drove prices to historic highs above 100 pesos.

Standard time-series models rely on an asset's past prices to project its future. In agricultural commodities, that assumption breaks down during severe economic and supply shocks. We set out to test whether incorporating real-world macroeconomic, agricultural, and weather factors into an Autoregressive Integrated Moving Average with Exogenous Inputs (ARIMAX) framework could accurately predict retail sugar prices through a period of extreme volatility.

![[sugar-historical-price.png|Ten-Year Historical Retail Sugar Price (2014–2024)|80%]]

The ten-year price history highlights this structural break. Retail prices remained remarkably stable for nearly eight years before the sharp 2022 surge—creating a regime shift that univariate trend models cannot anticipate on their own.

## The Approach

Developed as mathematical modeling research for our MAT305 course, we assembled a 120-month dataset spanning September 2014 to August 2024. Alongside domestic retail prices, we compiled seven exogenous indicators: domestic production, mill withdrawals (as a proxy for demand), global refined sugar prices, the USD-to-PHP exchange rate, headline inflation, and monthly precipitation and maximum temperature in Negros Occidental, where the vast majority of Philippine sugarcane is grown.

Correlation analysis confirmed that external economic pressures heavily shaped local prices. The USD-to-PHP exchange rate showed the strongest positive relationship (r = 0.83), followed by domestic inflation (r = 0.70) and global sugar prices (r = 0.66). Domestic mill withdrawals showed a strong negative correlation (r = -0.58), reflecting how supply constraints tightened market availability during the price run-up.

Both raw prices and the exogenous series were non-stationary, with an initial Augmented Dickey-Fuller (ADF) test p-value of 0.66. First-order differencing made the series stationary (p < 0.0001), fixing our integration order at d = 1. We split the 120-month series chronologically: the first 96 months trained the models and guided grid-search parameter selection, while the final 24 months (September 2022 to August 2024) served as an out-of-sample test window covering peak price volatility.

## The Result

![[sugar-arima-baseline.png|Baseline Univariate ARIMA(1,1,1) Forecast vs. Actual Prices|80%]]

We first benchmarked a standard univariate ARIMA(1,1,1) model. Relying solely on historical price momentum, the baseline failed completely when confronted with the 2022 inflation shock. Its projection flatlined along pre-crisis levels, finishing with a Mean Absolute Percentage Error (MAPE) of **76.64%** and an RMSE of **77.92 pesos**.

![[sugar-arimax-test-evaluation.png|ARIMAX(1,1,1) Out-of-Sample Test Evaluation|80%]]

Incorporating the exogenous indicators into an ARIMAX(1,1,1) model resolved that blind spot. Grounded by exchange rates, global benchmark trends, and domestic demand, the model adapted to the regime change—capturing both the steep initial climb and the subsequent stabilization around 85 pesos across the entire 24-month test window.

## Evaluation & 36-Month Forecast

Comparing the two models side by side underscores the value of external economic signals during structural market shifts. On the same 24-month test window, ARIMAX reduced mean absolute error from 68.64 pesos to **4.95 pesos** and brought MAPE down from 76.64% to **5.62%**.

**Model Performance Comparison (24-Month Test Set)**

| Model | Order | MAE (PHP) | RMSE (PHP) | MAPE | AIC |
| --- | --- | --- | --- | --- | --- |
| ARIMA (Baseline) | (1, 1, 1) | 68.64 | 77.92 | 76.64% | 434.26 |
| **ARIMAX (With Exogenous Inputs)** | **(1, 1, 1)** | **4.95** | **6.60** | **5.62%** | **442.03** |

Diagnostic checks confirmed that the ARIMAX residuals behaved as clean white noise. A Ljung-Box test failed to reject independence across twelve consecutive lags (p > 0.50), verifying that the model captured the underlying temporal structure.

![[sugar-forecast-36months.png|36-Month Retail Sugar Price Forecast (2024–2027) with 95% Confidence Intervals|80%]]

To project prices 36 months ahead (September 2024 through August 2027), we first forecasted each exogenous variable using univariate ARIMA and Holt-Winters exponential smoothing, then fed those trajectories into the trained ARIMAX model. The forecast projects that retail refined sugar will hold steady within a corridor of **82.80 to 84.92 pesos per kilogram** rather than reverting to pre-2022 levels.

When we validated the first eight months of this out-of-sample projection (September 2024 to April 2025) against actual Department of Agriculture retail price monitoring records, the model achieved a **0.51% MAPE**—an average absolute error of just **43 centavos per kilogram** (RMSE of 0.56 pesos).

## Takeaway

Agricultural commodities do not move in isolation. When macroeconomic or supply disruptions hit, historical prices alone cannot anticipate where the market is headed; pairing time-series structure with currency, inflation, and supply-demand indicators is essential.

At the same time, this research highlighted the practical tradeoff of ARIMAX forecasting: projecting into the future requires forecasting the exogenous inputs first, which compounds uncertainty over multi-year horizons. Within a six- to twelve-month planning window, however, the framework proved remarkably accurate for real-world price monitoring.
