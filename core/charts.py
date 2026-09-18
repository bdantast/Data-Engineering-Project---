import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import base64


COLORS = [
    "#2196F3", "#4CAF50", "#FF9800", "#E91E63",
    "#9C27B0", "#00BCD4", "#FF5722", "#607D8B",
    "#795548", "#CDDC39", "#3F51B5", "#009688",
]


def apply_style():
    plt.rcParams.update({
        "figure.facecolor": "#f8f9fa",
        "axes.facecolor": "#ffffff",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
    })


apply_style()


def create_line_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df[x_col], df[y_col], color=COLORS[0], linewidth=2, marker="o", markersize=4)
    ax.fill_between(df[x_col], df[y_col], alpha=0.1, color=COLORS[0])
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def create_bar_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 4), horizontal=False):
    fig, ax = plt.subplots(figsize=figsize)
    if horizontal:
        ax.barh(df[x_col], df[y_col], color=COLORS[: len(df)])
        ax.set_xlabel(ylabel)
        ax.set_ylabel(xlabel)
    else:
        ax.bar(df[x_col], df[y_col], color=COLORS[: len(df)])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
    ax.set_title(title, fontweight="bold", pad=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    return fig


def create_pie_chart(df, label_col, value_col, title="", figsize=(6, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    colors = COLORS[: len(df)]
    wedges, texts, autotexts = ax.pie(
        df[value_col],
        labels=df[label_col],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.85,
    )
    for text in autotexts:
        text.set_fontsize(9)
    ax.set_title(title, fontweight="bold", pad=15)
    plt.tight_layout()
    return fig


def create_kpi_card_figure(label, value, change=None, color="#2196F3"):
    fig, ax = plt.subplots(figsize=(3, 1.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.75, str(value), fontsize=26, fontweight="bold",
            ha="center", va="center", color=color, transform=ax.transAxes)
    ax.text(0.5, 0.35, label, fontsize=11, ha="center", va="center",
            color="#666666", transform=ax.transAxes)
    if change is not None:
        chg_color = "#4CAF50" if change >= 0 else "#E91E63"
        chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
        ax.text(0.5, 0.12, chg_text, fontsize=10, ha="center", va="center",
                color=chg_color, fontweight="bold", transform=ax.transAxes)
    return fig


def create_multi_bar_chart(df, categories, values_list, labels_list, title="", figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    import numpy as np
    x = np.arange(len(categories))
    width = 0.8 / len(values_list)
    for i, (vals, label) in enumerate(zip(values_list, labels_list)):
        offset = (i - len(values_list) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=label, color=COLORS[i % len(COLORS)])
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_title(title, fontweight="bold", pad=12)
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    return fig


def fig_to_image_bytes(fig, fmt="png"):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def fig_to_base64(fig):
    buf = fig_to_image_bytes(fig)
    return base64.b64encode(buf.read()).decode("utf-8")
