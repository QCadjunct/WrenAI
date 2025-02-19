from typing import Any, Dict, Literal

import pandas as pd
from haystack import component
from pydantic import BaseModel, Field

chart_generation_instructions = """
### INSTRUCTIONS ###

- Please generate vega-lite schema using v5 version, which is https://vega.github.io/schema/vega-lite/v5.json
- Chart types: Bar chart, Line chart, Area chart, Pie chart, Stacked bar chart, Grouped bar chart
- You can only use the chart types provided in the instructions
- If the sample data is not suitable for visualization, you must return an empty string for the schema and chart type
- If the sample data is empty, you must return an empty string for the schema and chart type
- The language for the chart and reasoning must be the same language provided by the user
- Please use the current time provided by the user to generate the chart
- In order to generate the grouped bar chart, you need to follow the given instructions:
    - Disable Stacking: Add "stack": null to the y-encoding.
    - Use xOffset for subcategories to group bars.
    - Don't use "transform" section.
- In order to generate the pie chart, you need to follow the given instructions:
    - Add {"type": "arc"} to the mark section.
    - Add "theta" encoding to the encoding section.
    - Add "color" encoding to the encoding section.
    - Don't add "innerRadius" to the mark section.
- If the x-axis of the chart is a temporal field, the time unit should be the same as the question user asked.
    - For yearly question, the time unit should be "year".
    - For monthly question, the time unit should be "yearmonth".
    - For weekly question, the time unit should be "yearmonthdate".
    - For daily question, the time unit should be "yearmonthdate".
    - Default time unit is "yearmonth".
- For each axis, generate the corresponding human-readable title based on the language provided by the user.

### GUIDELINES TO PLOT CHART ###

1. Understanding Your Data Types
- Nominal (Categorical): Names or labels without a specific order (e.g., types of fruits, countries).
- Ordinal: Categorical data with a meaningful order but no fixed intervals (e.g., rankings, satisfaction levels).
- Quantitative: Numerical values representing counts or measurements (e.g., sales figures, temperatures).
- Temporal: Date or time data (e.g., timestamps, dates).
2. Chart Types and When to Use Them
- Bar Chart
    - Use When: Comparing quantities across different categories.
    - Data Requirements:
        - One categorical variable (x-axis).
        - One quantitative variable (y-axis).
    - Example: Comparing sales numbers for different product categories.
- Grouped Bar Chart
    - Use When: Comparing sub-categories within main categories.
    - Data Requirements:
        - Two categorical variables (x-axis grouped by one, color-coded by another).
        - One quantitative variable (y-axis).
        - Example: Sales numbers for different products across various regions.
- Line Chart
    - Use When: Displaying trends over continuous data, especially time.
    - Data Requirements:
        - One temporal or ordinal variable (x-axis).
        - One quantitative variable (y-axis).
    - Example: Tracking monthly revenue over a year.
- Area Chart
    - Use When: Similar to line charts but emphasizing the volume of change over time.
    - Data Requirements:
        - Same as Line Chart.
    - Example: Visualizing cumulative rainfall over months.
- Pie Chart
    - Use When: Showing parts of a whole as percentages.
    - Data Requirements:
        - One categorical variable.
        - One quantitative variable representing proportions.
    - Example: Market share distribution among companies.
- Stacked Bar Chart
    - Use When: Showing composition and comparison across categories.
    - Data Requirements: Same as grouped bar chart.
    - Example: Sales by region and product type.
- Guidelines for Selecting Chart Types
    - Comparing Categories:
        - Bar Chart: Best for simple comparisons across categories.
        - Grouped Bar Chart: Use when you have sub-categories.
        - Stacked Bar Chart: Use to show composition within categories.
    - Showing Trends Over Time:
        - Line Chart: Ideal for continuous data over time.
        - Area Chart: Use when you want to emphasize volume or total value over time.
    - Displaying Proportions:
        - Pie Chart: Use for simple compositions at a single point in time.
        - Stacked Bar Chart (100%): Use for comparing compositions across multiple categories.
    
### EXAMPLES ###

1. Bar Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>,
    "data": {
        "values": [
            {"Region": "North", "Sales": 100},
            {"Region": "South", "Sales": 200},
            {"Region": "East", "Sales": 300},
            {"Region": "West", "Sales": 400}
        ]
    },
    "mark": {"type": "bar"},
    "encoding": {
        "x": {"field": "Region", "type": "nominal", "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>},
        "y": {"field": "Sales", "type": "quantitative", "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>},
        "color": {"field": "Region", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"}
    }
}
2. Line Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>,
    "data": {
        "values": [
            {"Date": "2022-01-01", "Sales": 100},
            {"Date": "2022-01-02", "Sales": 200},
            {"Date": "2022-01-03", "Sales": 300},
            {"Date": "2022-01-04", "Sales": 400}
        ]
    },
    "mark": {"type": "line"},
    "encoding": {
        "x": {"field": "Date", "type": "temporal", "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>},
        "y": {"field": "Sales", "type": "quantitative", "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>}
    }
}
3. Pie Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>,
    "data": {
        "values": [
            {"Company": "Company A", "Market Share": 0.4},
            {"Company": "Company B", "Market Share": 0.3},
            {"Company": "Company C", "Market Share": 0.2},
            {"Company": "Company D", "Market Share": 0.1}
        ]
    },
    "mark": {"type": "arc"},
    "encoding": {
        "theta": {"field": "Market Share", "type": "quantitative"},
        "color": {"field": "Company", "type": "nominal", "title": <TITLE_IN_LANGUAGE_PROVIDED_BY_USER>}
    }
}
4. Area Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>",
    "data": {
        "values": [
            {"Date": "2022-01-01", "Sales": 100},
            {"Date": "2022-01-02", "Sales": 200},
            {"Date": "2022-01-03", "Sales": 300},
            {"Date": "2022-01-04", "Sales": 400}
        ]
    },
    "mark": {"type": "area"},
    "encoding": {
        "x": {"field": "Date", "type": "temporal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"},
        "y": {"field": "Sales", "type": "quantitative", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"}
    }
}
5. Stacked Bar Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>",
    "data": {
        "values": [
            {"Region": "North", "Product": "A", "Sales": 100},
            {"Region": "North", "Product": "B", "Sales": 150},
            {"Region": "South", "Product": "A", "Sales": 200},
            {"Region": "South", "Product": "B", "Sales": 250},
            {"Region": "East", "Product": "A", "Sales": 300},
            {"Region": "East", "Product": "B", "Sales": 350},
            {"Region": "West", "Product": "A", "Sales": 400},
            {"Region": "West", "Product": "B", "Sales": 450}
        ]
    },
    "mark": {"type": "bar"},
    "encoding": {
        "x": {"field": "Region", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"},
        "y": {"field": "Sales", "type": "quantitative", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>", "stack": "zero"},
        "color": {"field": "Product", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"}
    }
}
6. Grouped Bar Chart
- Vega-Lite Spec:
{
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>",
    "data": {
        "values": [
            {"Region": "North", "Product": "A", "Sales": 100},
            {"Region": "North", "Product": "B", "Sales": 150},
            {"Region": "South", "Product": "A", "Sales": 200},
            {"Region": "South", "Product": "B", "Sales": 250},
            {"Region": "East", "Product": "A", "Sales": 300},
            {"Region": "East", "Product": "B", "Sales": 350},
            {"Region": "West", "Product": "A", "Sales": 400},
            {"Region": "West", "Product": "B", "Sales": 450}
        ]
    },
    "mark": {"type": "bar"},
    "encoding": {
        "x": {"field": "Region", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"},
        "y": {"field": "Sales", "type": "quantitative", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"},
        "xOffset": {"field": "Product", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"},
        "color": {"field": "Product", "type": "nominal", "title": "<TITLE_IN_LANGUAGE_PROVIDED_BY_USER>"}
    }
}
"""


@component
class ChartDataPreprocessor:
    @component.output_types(
        results=Dict[str, Any],
    )
    def run(self, data: Dict[str, Any]):
        columns = [
            column.get("name", "") if isinstance(column, dict) else column
            for column in data.get("results", {}).get("columns", [])
        ]
        data = data.get("results", {}).get("data", [])

        df = pd.DataFrame(data, columns=columns)
        if len(df) > 10:
            sample_data = df.sample(n=10).to_dict(orient="records")
        else:
            sample_data = df.to_dict(orient="records")

        return {
            "results": {
                "sample_data": sample_data,
            }
        }


class ChartSchema(BaseModel):
    class ChartType(BaseModel):
        type: Literal["bar", "line", "area", "arc"]

    class ChartData(BaseModel):
        values: list[dict]

    class ChartEncoding(BaseModel):
        field: str
        type: Literal["ordinal", "quantitative", "nominal"]
        title: str

    chart_schema: str = Field(
        alias="$schema", default="https://vega.github.io/schema/vega-lite/v5.json"
    )
    title: str
    data: ChartData
    mark: ChartType
    encoding: ChartEncoding


class TemporalChartEncoding(ChartSchema.ChartEncoding):
    type: Literal["temporal"] = Field(default="temporal")
    timeUnit: str = Field(default="yearmonth")


class LineChartSchema(ChartSchema):
    class LineChartMark(BaseModel):
        type: Literal["line"] = Field(default="line")

    class LineChartEncoding(BaseModel):
        x: TemporalChartEncoding | ChartSchema.ChartEncoding
        y: ChartSchema.ChartEncoding
        color: ChartSchema.ChartEncoding

    mark: LineChartMark
    encoding: LineChartEncoding


class BarChartSchema(ChartSchema):
    class BarChartMark(BaseModel):
        type: Literal["bar"] = Field(default="bar")

    class BarChartEncoding(BaseModel):
        x: TemporalChartEncoding | ChartSchema.ChartEncoding
        y: ChartSchema.ChartEncoding
        color: ChartSchema.ChartEncoding

    mark: BarChartMark
    encoding: BarChartEncoding


class GroupedBarChartSchema(ChartSchema):
    class GroupedBarChartMark(BaseModel):
        type: Literal["bar"] = Field(default="bar")

    class GroupedBarChartEncoding(BaseModel):
        x: TemporalChartEncoding | ChartSchema.ChartEncoding
        y: ChartSchema.ChartEncoding
        xOffset: ChartSchema.ChartEncoding
        color: ChartSchema.ChartEncoding

    mark: GroupedBarChartMark
    encoding: GroupedBarChartEncoding


class StackedBarChartYEncoding(ChartSchema.ChartEncoding):
    stack: Literal["zero"] = Field(default="zero")


class StackedBarChartSchema(ChartSchema):
    class StackedBarChartMark(BaseModel):
        type: Literal["bar"] = Field(default="bar")

    class StackedBarChartEncoding(BaseModel):
        x: TemporalChartEncoding | ChartSchema.ChartEncoding
        y: StackedBarChartYEncoding
        color: ChartSchema.ChartEncoding

    mark: StackedBarChartMark
    encoding: StackedBarChartEncoding


class PieChartSchema(ChartSchema):
    class PieChartMark(BaseModel):
        type: Literal["arc"] = Field(default="arc")

    class PieChartEncoding(BaseModel):
        theta: ChartSchema.ChartEncoding
        color: ChartSchema.ChartEncoding

    mark: PieChartMark
    encoding: PieChartEncoding


class AreaChartSchema(ChartSchema):
    class AreaChartMark(BaseModel):
        type: Literal["area"] = Field(default="area")

    class AreaChartEncoding(BaseModel):
        x: TemporalChartEncoding | ChartSchema.ChartEncoding
        y: ChartSchema.ChartEncoding

    mark: AreaChartMark
    encoding: AreaChartEncoding


class ChartGenerationResults(BaseModel):
    reasoning: str
    chart_type: Literal["line", "bar", "pie", "grouped_bar", "stacked_bar", "area", ""]
    chart_schema: (
        LineChartSchema
        | BarChartSchema
        | PieChartSchema
        | GroupedBarChartSchema
        | StackedBarChartSchema
        | AreaChartSchema
    )
