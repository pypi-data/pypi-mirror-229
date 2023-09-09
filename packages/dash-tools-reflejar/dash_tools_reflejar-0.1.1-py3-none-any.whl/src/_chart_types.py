from plotly.express._core import make_figure
import plotly.graph_objs as go


def histogram(
    data_frame=None,
    x=None,
    y=None,
    color=None,
    pattern_shape=None,
    facet_row=None,
    facet_col=None,
    facet_col_wrap=0,
    facet_row_spacing=None,
    facet_col_spacing=None,
    hover_name=None,
    hover_data=None,
    animation_frame=None,
    animation_group=None,
    category_orders=None,
    labels=None,
    color_discrete_sequence=None,
    color_discrete_map=None,
    pattern_shape_sequence=None,
    pattern_shape_map=None,
    marginal=None,
    opacity=None,
    orientation=None,
    barmode="relative",
    barnorm=None,
    histnorm=None,
    log_x=False,
    log_y=False,
    range_x=None,
    range_y=None,
    histfunc=None,
    cumulative=None,
    nbins=None,
    text_auto=False,
    text="",
    title=None,
    template=None,
    width=None,
    height=None,
) -> go.Figure:
    """
    In a histogram, rows of `data_frame` are grouped together into a
    rectangular mark to visualize the 1D distribution of an aggregate
    function `histfunc` (e.g. the count or sum) of the value `y` (or `x` if
    `orientation` is `'h'`).
    """
    return make_figure(
        args=locals(),
        constructor=go.Histogram,
        trace_patch=dict(
            histnorm=histnorm,
            histfunc=histfunc,
            cumulative=dict(enabled=cumulative),
        ),
        layout_patch=dict(barmode=barmode, barnorm=barnorm),
    )
