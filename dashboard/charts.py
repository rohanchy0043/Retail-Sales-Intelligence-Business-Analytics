import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


THEME = {
    "template": "plotly_white",
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": "#1E293B"},
}


def apply_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=45, b=20), **THEME)
    return fig


def monthly_chart(frame: pd.DataFrame, y: str, title: str, color: str) -> go.Figure:
    data = frame.groupby("Month", observed=True)[y].sum().reset_index()
    fig = px.line(data, x="Month", y=y, title=title, markers=True)
    fig.update_traces(line_color=color)
    return apply_layout(fig)


def bar_chart(data: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False, color: str = "#2563EB") -> go.Figure:
    fig = px.bar(data, x=x, y=y,
                 title=title, color_discrete_sequence=[color], orientation="h" if horizontal else "v")
    fig.update_layout(uniformtext_minsize=8)
    return apply_layout(fig)


def donut_chart(data: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(data, names=names, values=values, hole=0.55, title=title,
                 color_discrete_sequence=["#2563EB", "#38BDF8", "#6366F1", "#14B8A6"])
    return apply_layout(fig)
