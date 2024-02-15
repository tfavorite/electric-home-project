const createChart = function(chartdiv, chartName, fieldName, chartData, yAxisOptions) {
    const root = am5.Root.new(chartdiv);

    // Set themes
    // https://www.amcharts.com/docs/v5/concepts/themes/
    const themes = [
        am5themes_Animated.new(root)
    ];
    if ( window?.matchMedia('(prefers-color-scheme: dark)').matches ) {
        themes.push(am5themes_Dark.new(root));
    } 

    root.setThemes(themes);
    
    // Create chart
    // https://www.amcharts.com/docs/v5/charts/xy-chart/
    const chart = root.container.children.push(am5xy.XYChart.new(root, {
      panX: true,
      panY: true,
      wheelX: "panX",
      wheelY: "zoomX",
      pinchZoomX: true,
      paddingLeft:0,
      paddingRight:1
    }));
    
    // Add cursor
    // https://www.amcharts.com/docs/v5/charts/xy-chart/cursor/
    const cursor = chart.set("cursor", am5xy.XYCursor.new(root, {}));
    cursor.lineY.set("visible", false);
    
    
    // Create axes
    // https://www.amcharts.com/docs/v5/charts/xy-chart/axes/
    const xRenderer = am5xy.AxisRendererX.new(root, {});
    
    xRenderer.grid.template.setAll({
      location: 1
    })
    
    const xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
      maxDeviation: 0.3,
      categoryField: "heating_type",
      renderer: xRenderer,
      tooltip: am5.Tooltip.new(root, {})
    }));
    
    const yRenderer = am5xy.AxisRendererY.new(root, {
      strokeOpacity: 0.1
    })
    
    const yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, Object.assign({
      maxDeviation: 0.3,
      renderer: yRenderer ,
      min: 0
    }, yAxisOptions)));

    chart.topAxesContainer.children.push(am5.Label.new(root, {
        text: chartName,
        fontSize: 25,
        fontWeight: "400",
        x: am5.p50,
        centerX: am5.p50
      }));

    chart.get("colors").set("colors", [
        am5.color(0x800020),
        am5.color(0x04AA6D)
      ]);
    
    // Create series
    // https://www.amcharts.com/docs/v5/charts/xy-chart/series/
    const series = chart.series.push(am5xy.ColumnSeries.new(root, {
      name: chartName,
      xAxis: xAxis,
      yAxis: yAxis,
      valueYField: fieldName,
      sequencedInterpolation: true,
      categoryXField: "heating_type",
      tooltip: am5.Tooltip.new(root, {
        labelText: "{valueY}"
      })
    }));
    
    series.columns.template.setAll({ cornerRadiusTL: 5, cornerRadiusTR: 5, strokeOpacity: 0 });
    series.columns.template.adapters.add("fill", function (fill, target) {
      return chart.get("colors").getIndex(series.columns.indexOf(target));
    });
    
    series.columns.template.adapters.add("stroke", function (stroke, target) {
      return chart.get("colors").getIndex(series.columns.indexOf(target));
    });
    
    xAxis.data.setAll(chartData);
    series.data.setAll(chartData);
    
    
    // Make stuff animate on load
    // https://www.amcharts.com/docs/v5/concepts/animations/
    series.appear(1000);
    chart.appear(1000, 100);
};
