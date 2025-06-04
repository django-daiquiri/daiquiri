import React, { useState, useRef, useCallback, memo } from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { get, isNil, toString } from 'lodash'
import classNames from 'classnames'

import { config, layout } from 'daiquiri/query/assets/js/constants/plot'
import { getColumnLabel } from 'daiquiri/query/assets/js/utils/plot'
import {
  useQueryLanguagesQuery,
  useQueuesQuery,
} from 'daiquiri/query/assets/js/hooks/queries'
import { useSubmitJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

import Errors from 'daiquiri/core/assets/js/components/form/Errors'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const MemoizedPlot = memo(({ columns, plotValues, x, y, onSelected }) => {

  const opacity = x.length > 100000 ? 0.25 : 0.6

  const data = [{
    x: x,
    y: y,
    type: 'scattergl',
    mode: 'markers',
    opacity: opacity,
    marker: {
      size: 5,
      color: plotValues.y.color,
      symbol: plotValues.y.symbol
    },
    hoverinfo: 'skip'
  }]

  const yLabel = getColumnLabel(columns, plotValues.y.column)

  return (
    <Plot
      data={data}
      layout={{
        ...layout,
        xaxis: {
          title: {
            text: getColumnLabel(columns, plotValues.x.column),
          },
        },
        yaxis: {
          title: {
            text: yLabel,
          }
        }
      }}
      style={{ width: '100%' }}
      useResizeHandler={true}
      config={config}
      onSelected={onSelected}
    />
  );
});


const ScatterPlot = ({ columns, plotValues, x, y, loadJob, job }) => {
  const selectedPointsRef = useRef({ x: [], y: [], n: 0 })
  const [errors, setErrors] = useState({})
  const [isFormDisabled, setIsFormDisabled] = useState(true)

  const [values, setValues] = useState({
    table_name: '',
    run_id: '',
    queue: '',
    query: '',
    query_language: '',
  })

  const { data: queues } = useQueuesQuery()
  const { data: queryLanguages } = useQueryLanguagesQuery()

  const mutation = useSubmitJobMutation()

  const getDefaultQueue = () => (isNil(queues) ? '' : queues[0].id)

  const handleSubmit = () => {
    const polyPoints = selectedPointsRef.current.x
      .map((x, index) => `(${x}, ${selectedPointsRef.current.y[index]})`)
      .concat(`(${selectedPointsRef.current.x[0]}, ${selectedPointsRef.current.y[0]})`)
      .join(', ');
    const query = `SELECT *
FROM "${job.schema_name}"."${job.table_name}" as t
WHERE POLYGON '(${polyPoints})' @> POINT(t.${plotValues.x.column}, t.${plotValues.y.column});`

    const postgres = queryLanguages.find(language => toString(language.id).includes('postgres'))
    values.query_language = postgres ? postgres.id : job.query_language
    values.query = query
    values.queue = values.queue == '' ? getDefaultQueue() : values.queue

    mutation.mutate({ values: values, setErrors, loadJob })
  }

  const handleSelection = useCallback((event) => {
    if (event && event.lassoPoints && event.lassoPoints.x.length > 0) {
      selectedPointsRef.current = { x: event.lassoPoints.x, y: event.lassoPoints.y, n: event.points.length }
      setIsFormDisabled(false)
    } else if (event && event.range && event.range.x.length > 0) {
      selectedPointsRef.current = {
        x: [event.range.x[0], event.range.x[0], event.range.x[1], event.range.x[1]],
        y: [event.range.y[0], event.range.y[1], event.range.y[1], event.range.y[0]],
        n: event.points.length
      }
      setIsFormDisabled(false)
    } else {
      selectedPointsRef.current = { x: [], y: [], n: 0 }
      setIsFormDisabled(true)
    }
  }, []);

  if (isNil(x)) {
    return null
  }

  return (
    <div className="card">
      <div className="card-body">
        <div className="ratio ratio-16x9">
          <MemoizedPlot
            columns={columns}
            plotValues={plotValues}
            x={x}
            y={y}
            onSelected={handleSelection}
          />
        </div>
      </div>
      {
        isFormDisabled ? (
          <div className="card-footer text-secondary">
            Select points with the 'Lasso' or 'Box' tool to run a new query on the selected subset.
          </div>
        ) : (
          <div className="card-footer">
            <div className="row">
              <div className="col-md-12">You have selected {selectedPointsRef.current.n} points. Please click 'Submit Query' to submit a new query for the selected region.</div>
            </div>
            <div className="row">
              <div className="col-md-6">
                <Input
                  label={gettext('Table name')}
                  value={values.table_name}
                  errors={errors.table_name}
                  onChange={(table_name) => setValues({ ...values, table_name })}
                />
              </div>
              <div className="col-md-3">
                <Input
                  label={gettext('Run id')}
                  value={values.run_id}
                  errors={errors.run_id}
                  onChange={(run_id) => setValues({ ...values, run_id })}
                />
              </div>
              <div className="col-md-3">
                <Select
                  label={gettext('Queue')}
                  value={values.queue}
                  errors={errors.queue}
                  options={queues}
                  onChange={(queue) => setValues({ ...values, queue })}
                />
              </div>
              <div className="col-md-12">
                <button
                  className={classNames("btn btn-primary", { 'is-invalid': errors.query })}
                  onClick={() => handleSubmit()}
                >Submit Query</button>
                <Errors errors={get(errors.query, 'messages') || errors.query} />
                {
                  errors && errors.query && (
                    <Errors errors={['If the error persists, please contact the website maintainers.']} />
                  )
                }
              </div>
            </div>
          </div>
        )
      }
    </div>
  )
}

ScatterPlot.propTypes = {
  columns: PropTypes.array.isRequired,
  plotValues: PropTypes.object.isRequired,
  x: PropTypes.array,
  y: PropTypes.array,
  loadJob: PropTypes.func.isRequired,
  job: PropTypes.object.isRequired
}

export default ScatterPlot
