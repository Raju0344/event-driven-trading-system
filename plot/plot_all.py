from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------
# Utility: create matrix for heatmaps
# -------------------------------------------------
def create_data_matrix(
    df: pd.DataFrame,
    value_col: str,
    row_col: str,
    col_col: str,
    row_vals: list[float],
    col_vals: list[float],
) -> np.ndarray:
    data = np.zeros((len(row_vals), len(col_vals)))

    for i, r in enumerate(row_vals):
        for j, c in enumerate(col_vals):
            data[i, j] = df.loc[
                (df[row_col] == r) & (df[col_col] == c),
                value_col,
            ].values[0]

    return data


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def plot_all():

    # =================================================
    # LOAD OPTIMIZATION DATA
    # =================================================
    opt_csv = "/home/raju/MAIN_DIRECTORY/EventDrivenTrading/output/opt.csv"
    df_opt = pd.read_csv(opt_csv)

    LOOKBACK = 50
    df_opt = df_opt[df_opt["ols_window"] == LOOKBACK]

    z_exit_vals = [0.5, 1.0, 1.5]
    z_entry_vals = [2.0, 3.0, 4.0]

    sharpe_data = create_data_matrix(
        df=df_opt,
        value_col="sharpe",
        row_col="zscore_low",
        col_col="zscore_high",
        row_vals=z_exit_vals,
        col_vals=z_entry_vals,
    )

    drawdown_data = create_data_matrix(
        df=df_opt,
        value_col="max_drawdown_pct",
        row_col="zscore_low",
        col_col="zscore_high",
        row_vals=z_exit_vals,
        col_vals=z_entry_vals,
    )

    # =================================================
    # LOAD EQUITY CURVE DATA
    # =================================================
    equity_csv = "output/equity.csv"
    df_eq = (
        pd.read_csv(
            equity_csv,
            index_col=0,
            parse_dates=True,
        )
        .sort_index()
    )

    # =================================================
    # CREATE FIGURE LAYOUT
    # =================================================
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("white")

    gs = fig.add_gridspec(
        nrows=3,
        ncols=2,
        height_ratios=[1.2, 1, 1],
    )

    ax_sharpe = fig.add_subplot(gs[0, 0])
    ax_dd = fig.add_subplot(gs[0, 1])

    ax_eq = fig.add_subplot(gs[1, :])
    ax_ret = fig.add_subplot(gs[2, 0])
    ax_dd_curve = fig.add_subplot(gs[2, 1])

    # =================================================
    # SHARPE HEATMAP
    # =================================================
    im1 = ax_sharpe.imshow(
        sharpe_data,
        cmap="Blues",
        origin="lower",
        aspect="auto",
    )

    for i in range(sharpe_data.shape[0]):
        for j in range(sharpe_data.shape[1]):
            ax_sharpe.text(j, i, f"{sharpe_data[i, j]:.2f}",
                           ha="center", va="center")

    ax_sharpe.set_xticks(range(len(z_entry_vals)))
    ax_sharpe.set_yticks(range(len(z_exit_vals)))
    ax_sharpe.set_xticklabels(z_entry_vals)
    ax_sharpe.set_yticklabels(z_exit_vals)
    ax_sharpe.set_title("Sharpe Ratio Heatmap")
    ax_sharpe.set_xlabel("Z-Score Entry")
    ax_sharpe.set_ylabel("Z-Score Exit")
    fig.colorbar(im1, ax=ax_sharpe)

    # =================================================
    # DRAWDOWN HEATMAP
    # =================================================
    im2 = ax_dd.imshow(
        drawdown_data,
        cmap="Reds",
        origin="lower",
        aspect="auto",
    )

    for i in range(drawdown_data.shape[0]):
        for j in range(drawdown_data.shape[1]):
            ax_dd.text(j, i, f"{drawdown_data[i, j]:.2f}%",
                       ha="center", va="center")

    ax_dd.set_xticks(range(len(z_entry_vals)))
    ax_dd.set_yticks(range(len(z_exit_vals)))
    ax_dd.set_xticklabels(z_entry_vals)
    ax_dd.set_yticklabels(z_exit_vals)
    ax_dd.set_title("Max Drawdown Heatmap")
    ax_dd.set_xlabel("Z-Score Entry")
    ax_dd.set_ylabel("Z-Score Exit")
    fig.colorbar(im2, ax=ax_dd)

    # =================================================
    # EQUITY CURVE
    # =================================================
    ax_eq.plot(df_eq.index, df_eq["equity_curve"], linewidth=2)
    ax_eq.set_title("Equity Curve")
    ax_eq.set_ylabel("Portfolio Value")
    ax_eq.grid(True)

    # =================================================
    # RETURNS
    # =================================================
    ax_ret.plot(df_eq.index, df_eq["returns"], color="black")
    ax_ret.set_title("Returns")
    ax_ret.grid(True)

    # =================================================
    # DRAWDOWN CURVE
    # =================================================
    ax_dd_curve.plot(df_eq.index, df_eq["drawdown"], color="red")
    ax_dd_curve.set_title("Drawdowns")
    ax_dd_curve.grid(True)

    plt.tight_layout()
    plt.show()
