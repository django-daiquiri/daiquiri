import { appTheme } from "./theme.js"
import React, { useState, useEffect, useRef } from 'react'
import { isNil } from 'lodash'
import PropTypes from 'prop-types'
import ScatterForm from './plots/ScatterForm'
import { validTypes, excludedUcds } from 'daiquiri/query/assets/js/constants/plot'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'
import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'
import {
    EllipsePointMarker,
    MouseWheelZoomModifier,
    NumericAxis,
    NumberRange,
    SciChartSurface,
    SweepAnimation,
    TrianglePointMarker,
    XyDataSeries,
    XyScatterRenderableSeries,
    ZoomExtentsModifier,
    ZoomPanModifier,
} from "scichart";


export const drawExample = async (rootElement, {xValues, yValues}) => {
    SciChartSurface.configure({
      dataUrl: `/static/query/scichart2d.data`,
      wasmUrl: `/static/query/scichart2d.wasm`
    });

    const { sciChartSurface, wasmContext } = await SciChartSurface.create(rootElement, {
      theme: appTheme.SciChartJsTheme,
    });

    sciChartSurface.xAxes.add(new NumericAxis(wasmContext));
    sciChartSurface.yAxes.add(new NumericAxis(wasmContext, { growBy: new NumberRange(0.05, 0.05) }));

    sciChartSurface.renderableSeries.add(
        new XyScatterRenderableSeries(wasmContext, {
            dataSeries: new XyDataSeries(wasmContext, { xValues, yValues }),
            pointMarker: new EllipsePointMarker(wasmContext, {
                width: 6,
                height: 6,
                strokeThickness: 0,
                fill: appTheme.VividOrange,
            }),
            opacity: 0.8,
            animation: new SweepAnimation({ duration: 600, fadeEffect: true }),
        })
    );

    // Optional: Add Interactivity Modifiers
    sciChartSurface.chartModifiers.add(new ZoomPanModifier({ enableZoom: true }));
    sciChartSurface.chartModifiers.add(new ZoomExtentsModifier());
    sciChartSurface.chartModifiers.add(new MouseWheelZoomModifier());

    sciChartSurface.zoomExtents();

    return { sciChartSurface, wasmContext };

};

export const SciChartComponent = ({ job }) => {
  const chartContainerRef = useRef(null);
  const [chartLoaded, setChartLoaded] = useState(false);

  const [columns, setColumns] = useState([])

  useEffect(() => setColumns(job.columns.filter((column) => (
    validTypes.includes(column.datatype) &&
    !excludedUcds.some((ucd) => (!isNil(column.ucd) && column.ucd.split(';').includes(ucd)))
  ))), [job])


  const [values, setValues] = useState({
    x: {
      column: '',
    },
    y1: {
      column: '',
      color: colors[0].hex,
      symbol: symbols[0].symbol
    },
    y2: {
      column: '',
      color: colors[1].hex,
      symbol: symbols[1].symbol
    },
    y3: {
      column: '',
      color: colors[2].hex,
      symbol: symbols[2].symbol
    }
  })

  useEffect(() => setValues({
    ...values,
    x: {
      ...values.x, column: isNil(columns[0]) ? '' : columns[0].name
    },
    y1: {
      ...values.y1, column: isNil(columns[1]) ? '' : columns[1].name
    }
  }), [columns])


  const { data: xValues, isLoading: isXLoading, error: xError } = useJobPlotQuery(job, values.x.column);
  const { data: yValues, isLoading: isYLoading, error: yError } = useJobPlotQuery(job, values.y1.column);

  useEffect(() => {
    if (
      chartContainerRef.current &&
      xValues &&
      yValues &&
      !isXLoading &&
      !isYLoading &&
      !(xError || yError)
    ) {
      drawExample(chartContainerRef.current, { xValues, yValues })
        .then(() => setChartLoaded(true))
        .catch((error) => {
          console.error("Error drawing chart", error);
        });
    }
  }, [chartContainerRef, xValues, yValues, isXLoading, isYLoading, xError, yError]);

  return (
    <div>
      <ScatterForm columns={columns} values={values} setValues={setValues} />
      <div ref={chartContainerRef} style={{ width: "100%", height: "600px" }}>
      </div>
    </div>
  );
};

SciChartComponent.propTypes = {
  job: PropTypes.object.isRequired,
}

export default SciChartComponent
