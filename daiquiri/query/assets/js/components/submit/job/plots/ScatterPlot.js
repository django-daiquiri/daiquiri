import React, { useState, useRef, useEffect, useCallback, memo } from 'react'
import PropTypes from 'prop-types'
import Plot from 'react-plotly.js'
import { isNil, toString } from 'lodash'

import { config, layout } from 'daiquiri/query/assets/js/constants/plot'
import { getColumnLabel } from 'daiquiri/query/assets/js/utils/plot'
import {
  useFormQuery,
  useQueryLanguagesQuery,
  useQueuesQuery,
} from 'daiquiri/query/assets/js/hooks/queries'
import { useSubmitJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'

import Errors from 'daiquiri/core/assets/js/components/form/Errors'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const MemoizedPlot = memo(({ columns, values, x, y, onSelected }) => {

  const opacity = x.length > 100000 ? 0.25 : 0.6

  const data = [{
      x: x,
      y: y,
      type: 'scattergl',
      mode: 'markers',
      opacity: opacity,
      marker : {
        size: 5,
        color: values.y.color,
        symbol: values.y.symbol
      },
      hoverinfo: 'skip'
  }]

  const yLabel = getColumnLabel(columns, values.y.column)

  return (
    <Plot
      data={data}
      layout={{
      ...layout,
        xaxis: {
          title: {
            text: getColumnLabel(columns, values.x.column),
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


const ScatterPlot = ({ columns, values, x, y, loadJob, job }) => {
  const { data: form } = useFormQuery('sql')
  const { data: queues } = useQueuesQuery()
  const { data: queryLanguages } = useQueryLanguagesQuery()

  const [isClicked, setIsClicked] = useState(false);
  const [text, setText] = useState('');
  const [errors, setErrors] = useState({})


  const [tableValues, setTableValues] = useState({
    table_name: '',
    run_id: '',
    queue: '',
    query: '',
    query_language:'',
  })

  const [isButtonDisabled, setIsButtonDisabled] = useState(true)
  const selectedPointsRef = useRef({x:[], y:[], n: 0})

  const mutation = useSubmitJobMutation()

  const getDefaultQueue = () => (isNil(queues) ? '' : queues[0].id)

  const handleSubmit = () => {
    const polyPoints = selectedPointsRef.current.x
    .map((x, index) => `(${x}, ${selectedPointsRef.current.y[index]})`)
    .concat(`(${selectedPointsRef.current.x[0]}, ${selectedPointsRef.current.y[0]})`)
    .join(', ');
    const query = `SELECT *
FROM "${job.schema_name}"."${job.table_name}" as t
WHERE POLYGON '(${polyPoints})' @> POINT(t.${values.x.column}, t.${values.y.column});`

    const postgres = queryLanguages.find(language => toString(language.id).includes('postgres'))
    tableValues.query_language = postgres ? postgres.id : job.query_language

    tableValues.query = query
    tableValues.queue = tableValues.queue == '' ?  getDefaultQueue() : ''

    mutation.mutate({ values:tableValues, setErrors, loadJob })
  }


  const getInitialValues = () =>
    isNil(form) || isEmpty(form.fields)
      ? {}
      : {
          ...form.fields.reduce(
            (initialValues, field) => ({
              ...initialValues,
              [field.key]: field.default_value || '',
            }),
            {}
          ),
        }

  const handleSelection = useCallback((event) => {
    if (event && event.lassoPoints && event.lassoPoints.x.length > 0) {
      selectedPointsRef.current = { x: event.lassoPoints.x, y: event.lassoPoints.y, n: event.points.length }
      setIsButtonDisabled(false)
    } else if (event && event.range && event.range.x.length > 0) {
      selectedPointsRef.current = {
        x: [event.range.x[0], event.range.x[0], event.range.x[1], event.range.x[1]],
        y: [event.range.y[0], event.range.y[1], event.range.y[1], event.range.y[0]],
        n: event.points.length }
      setIsButtonDisabled(false)
    } else {
      selectedPointsRef.current = { x: [], y: [], n: 0}
      setIsButtonDisabled(true)
      setText('')
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
            values={values}
            x={x}
            y={y}
            onSelected={handleSelection}
          />
        </div>
      </div>
        {
          isButtonDisabled ?  (
              <div className="card-footer text-secondary">
              Select points with the 'Lasso' or 'Box' tool to run a new query on the selected subset.
              </div>
            ) : (
              <div className="card-footer">
                <div className="row">
                    <div className="col-md-6">You have selected {selectedPointsRef.current.n} points.</div>
                </div>
                <div className="row">
                  <div className="col-md-6">
                    <Input
                      label={gettext('Table name')}
                      value={tableValues.table_name}
                      errors={errors.table_name}
                      onChange={(table_name) => setTableValues({ ...tableValues, table_name })}
                    />
                  </div>
                  <div className="col-md-3">
                    <Input
                      label={gettext('Run id')}
                      value={tableValues.run_id}
                      errors={errors.run_id}
                      onChange={(run_id) => setTableValues({ ...tableValues, run_id })}
                    />
                  </div>
                  <div className="col-md-3">
                    <Select
                      label={gettext('Queue')}
                      value={tableValues.queue}
                      errors={errors.queue}
                      options={queues}
                      onChange={(queue) => setTableValues({ ...tableValues, queue })}
                    />
                  </div>
                  <div className="col-md-3">
                    <button
                      className="btn btn-primary"
                      onClick={() => handleSubmit()}
                    >Run query</button>
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
    values: PropTypes.object.isRequired,
    x: PropTypes.array,
    y: PropTypes.array,
    loadJob: PropTypes.func.isRequired,
    job: PropTypes.object.isRequired
}

export default ScatterPlot
