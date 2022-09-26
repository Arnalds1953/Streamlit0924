import altair as alt

def get_chart(data):
    hover = alt.selection_single(
        fields=["订单时间"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="销售曲线图")
        .mark_line()
        .encode(
            x="订单时间",
            y="总销售额",
            # color="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="订单时间",
            y="总销售额",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("订单时间", title="Date"),
                alt.Tooltip("总销售额", title="Price (USD)"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()
