import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import base64
from config import COLORS


NEON_COLORS = [
    "#00d4ff", "#00ff88", "#a855f7", "#f472b6",
    "#fb923c", "#facc15", "#38bdf8", "#4ade80",
    "#c084fc", "#f87171", "#fbbf24", "#34d399",
]


def apply_dark_style():
    plt.rcParams.update({
        "figure.facecolor": COLORS["bg_card"],
        "axes.facecolor": COLORS["bg_card"],
        "axes.edgecolor": COLORS["border"],
        "axes.labelcolor": COLORS["text_secondary"],
        "text.color": COLORS["text_primary"],
        "xtick.color": COLORS["text_muted"],
        "ytick.color": COLORS["text_muted"],
        "grid.color": COLORS["border"],
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "axes.titlecolor": COLORS["text_primary"],
    })


apply_dark_style()


def create_line_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_card"])
    ax.plot(df[x_col], df[y_col], color=NEON_COLORS[0], linewidth=2.5, marker="o",
            markersize=5, markerfacecolor=COLORS["bg_card"], markeredgecolor=NEON_COLORS[0],
            markeredgewidth=2)
    ax.fill_between(df[x_col], df[y_col], alpha=0.1, color=NEON_COLORS[0])
    ax.set_title(title, fontweight="bold", pad=12, color=COLORS["text_primary"])
    ax.set_xlabel(xlabel, color=COLORS["text_secondary"])
    ax.set_ylabel(ylabel, color=COLORS["text_secondary"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.tick_params(colors=COLORS["text_muted"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["border"])
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def create_bar_chart(df, x_col, y_col, title="", xlabel="", ylabel="", figsize=(8, 4), horizontal=False):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_card"])
    if horizontal:
        bars = ax.barh(df[x_col], df[y_col], color=NEON_COLORS[: len(df)], edgecolor=COLORS["bg_card"], linewidth=0.5)
        ax.set_xlabel(ylabel, color=COLORS["text_secondary"])
        ax.set_ylabel(xlabel, color=COLORS["text_secondary"])
    else:
        bars = ax.bar(df[x_col], df[y_col], color=NEON_COLORS[: len(df)], edgecolor=COLORS["bg_card"], linewidth=0.5)
        ax.set_xlabel(xlabel, color=COLORS["text_secondary"])
        ax.set_ylabel(ylabel, color=COLORS["text_secondary"])
        plt.xticks(rotation=45, ha="right")
    ax.set_title(title, fontweight="bold", pad=12, color=COLORS["text_primary"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.tick_params(colors=COLORS["text_muted"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["border"])
    plt.tight_layout()
    return fig


def create_pie_chart(df, label_col, value_col, title="", figsize=(6, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["bg_card"])
    colors = NEON_COLORS[: len(df)]
    wedges, texts, autotexts = ax.pie(
        df[value_col], labels=df[label_col], autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.85,
        wedgeprops=dict(edgecolor=COLORS["bg_card"], linewidth=2),
    )
    for text in texts:
        text.set_color(COLORS["text_secondary"])
        text.set_fontsize(9)
    for at in autotexts:
        at.set_color(COLORS["bg_dark"])
        at.set_fontsize(9)
        at.set_fontweight("bold")
    ax.set_title(title, fontweight="bold", pad=15, color=COLORS["text_primary"])
    plt.tight_layout()
    return fig


def create_kpi_card_figure(label, value, change=None, color=NEON_COLORS[0]):
    fig, ax = plt.subplots(figsize=(3, 1.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg_card"])
    ax.text(0.5, 0.75, str(value), fontsize=26, fontweight="bold",
            ha="center", va="center", color=color, transform=ax.transAxes)
    ax.text(0.5, 0.35, label, fontsize=11, ha="center", va="center",
            color=COLORS["text_secondary"], transform=ax.transAxes)
    if change is not None:
        chg_color = COLORS["success"] if change >= 0 else COLORS["danger"]
        chg_text = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
        ax.text(0.5, 0.12, chg_text, fontsize=10, ha="center", va="center",
                color=chg_color, fontweight="bold", transform=ax.transAxes)
    return fig


def create_multi_bar_chart(df, categories, values_list, labels_list, title="", figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_card"])
    import numpy as np
    x = np.arange(len(categories))
    width = 0.8 / len(values_list)
    for i, (vals, label) in enumerate(zip(values_list, labels_list)):
        offset = (i - len(values_list) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=label, color=NEON_COLORS[i % len(NEON_COLORS)],
               edgecolor=COLORS["bg_card"], linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_title(title, fontweight="bold", pad=12, color=COLORS["text_primary"])
    ax.legend(facecolor=COLORS["bg_card"], edgecolor=COLORS["border"],
              labelcolor=COLORS["text_secondary"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.tick_params(colors=COLORS["text_muted"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["border"])
    plt.tight_layout()
    return fig


def fig_to_image_bytes(fig, fmt="png"):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


def fig_to_base64(fig):
    buf = fig_to_image_bytes(fig)
    return base64.b64encode(buf.read()).decode("utf-8")
