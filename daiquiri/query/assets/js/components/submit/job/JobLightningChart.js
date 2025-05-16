import { lightningChart, Themes, ColorRGBA, SolidFill, SolidLine } from "@lightningchart/lcjs";
import { useId, useRef, useEffect, useState } from 'react'
import { isNil } from 'lodash'
import { useJobPlotQuery } from 'daiquiri/query/assets/js/hooks/queries'
import ScatterForm from './plots/ScatterForm'
import { validTypes, excludedUcds } from 'daiquiri/query/assets/js/constants/plot'
import { colors, symbols } from 'daiquiri/query/assets/js/constants/plot'

export const Chart = ({ job }) => {
  const data = [{x: 0, y: 0}, {x: 1, y: 1}, {x: 2, y: 4}, {x: 3, y: 9}]
  const id = useId()
  const [chartObj, setChartObj] = useState(undefined);
  //const [chart, setChart] = useState(undefined);

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
    const container = document.getElementById(id);

    const licenseKey = process.env.LIGHTNING_CHART_LICENSE;

    if (!container) return
    const lc = lightningChart({
      license: licenseKey,
      licenseInformation: {
        appTitle: "LightningChart JS Trial",
        company: "LightningChart Ltd."
      }
    })
    const chart = lc.ChartXY({
      theme: Themes.darkGold,
      container,
    });
    chart.setCursorMode(undefined)
    const pointSeries = chart.addPointSeries()
    pointSeries.setPointSize(2)
    pointSeries.setPointFillStyle(
      new SolidFill({ color: ColorRGBA(255, 0, 0, 150)})
    )

    setChartObj({lc, chart, pointSeries })
    /*
    pointSeries.add(new Array(1000000).fill(0).map(() => ({
      x: Math.random(),
      y: Math.random()
    })))
    */
    return () => {
      lc.dispose();
    };
  }, [id]);

  useEffect(() => {
    if (chartObj && xValues && yValues && xValues.length === yValues.length) {
      const points = xValues.map((x, index) => ({
        x,
        y: yValues[index]
      }));
      chartObj.pointSeries.clear().add(points);
    }
  }, [chartObj, xValues, yValues]);

  return (
      <div>
      <ScatterForm columns={columns} values={values} setValues={setValues} />
      <div id={id} style={{ width: "100%", height: "600px" }}></div>
      </div>

  )
};

