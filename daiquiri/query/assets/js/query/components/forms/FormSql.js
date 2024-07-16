import React, { useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { get, isNil } from 'lodash'

import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'

import Template from 'daiquiri/core/assets/js/components/Template'

import { useQueryLanguagesQuery, useQueuesQuery } from '../../hooks/queries'
import { useSubmitJobMutation } from '../../hooks/mutations'

import Query from './common/Query'
import Select from './common/Select'
import Text from './common/Text'

import ColumnsDropdown from './dropdowns/ColumnsDropdown'
import ExamplesDropdown from './dropdowns/ExamplesDropdown'
import FunctionsDropdown from './dropdowns/FunctionsDropdown'
import SchemasDropdown from './dropdowns/SchemasDropdown'

const FormSql = ({ form, loadJob, query }) => {

  const [values, setValues] = useState({
    query: query || '',
    table_name: '',
    run_id: '',
    query_language: '',
    queue: '',
  })
  const [errors, setErrors] = useState({})

  const editor = useRef()

  const { data: queues } = useQueuesQuery()
  const { data: queryLanguages } = useQueryLanguagesQuery()
  const mutation = useSubmitJobMutation()

  const getDefaultQueryLanguage = () => queryLanguages[0].id
  const getDefaultQueue = () => queues[0].id

  const [openDropdown, setOpenDropdown] = useLsState('query.openDropdown')

  const handleDrowpdown = (dropdownKey) => {
    setOpenDropdown(openDropdown == dropdownKey ? false : dropdownKey)
  }

  const handleSubmit = () => {
    mutation.mutate({
      values: {
        ...values,
        query_language: values.query_language || getDefaultQueryLanguage(),
        queue: values.queue || getDefaultQueue()
      }, setErrors, loadJob})
  }

  const handleClear = () => {
    setValues({
      query: '\n\n\n',
      table_name: '',
      run_id: '',
      query_language: getDefaultQueryLanguage(),
      queue: getDefaultQueue(),
    })
  }

  const handlePaste = (item) => {
    let query_string = item.query_string

    if (isNil(query_string)) {
      const query_language = values.query_language || getDefaultQueryLanguage()
      const quote_char = queryLanguages.find((ql) => ql.id == query_language).quote_char

      query_string = item.query_strings.map((qs) => (quote_char + qs + quote_char)).join('.')
    }

    // see https://codemirror.net/examples/change/
    editor.current.view.dispatch({
      changes: {
        from: editor.current.view.state.selection.main.from,
        to: editor.current.view.state.selection.main.to,
        insert: query_string
      }
    })
  }

  const handleReplace = (item) => {
    setValues({...values, query: item.query_string})
  }

  return (
    <div className="form mb-4">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="sql-dropdowns">
        <div className="d-md-flex">
          <button type="button" className="btn btn-outline-form dropdown-toggle me-2 mb-2"
                  onClick={() => handleDrowpdown('schemas')}>
            {gettext('Database')}
          </button>
          <button type="button" className="btn btn-outline-form dropdown-toggle me-2 mb-2"
                  onClick={() => handleDrowpdown('columns')}>
            {gettext('Columns')}
          </button>
          <button type="button" className="btn btn-outline-form dropdown-toggle me-2 mb-2"
                  onClick={() => handleDrowpdown('functions')}>
            {gettext('Functions')}
          </button>
          <button type="button" className="btn btn-outline-form dropdown-toggle me-2 mb-2"
                  onClick={() => handleDrowpdown('simbad')}>
            {gettext('Simbad')}
          </button>
          <button type="button" className="btn btn-outline-form dropdown-toggle me-2 me-md-auto mb-2"
                  onClick={() => handleDrowpdown('vizier')}>
            {gettext('VizieR')}
          </button>
          <button type="button" className="btn btn-outline-form dropdown-toggle mb-2"
                  onClick={() => handleDrowpdown('examples')}>
            {gettext('Examples')}
          </button>
        </div>

        {
          openDropdown == 'schemas' && <SchemasDropdown onDoubleClick={handlePaste} />
        }
        {
          openDropdown == 'columns' && <ColumnsDropdown onDoubleClick={handlePaste} />
        }
        {
          openDropdown == 'functions' && <FunctionsDropdown onDoubleClick={handlePaste} />
        }
        {
          openDropdown == 'examples' && <ExamplesDropdown onDoubleClick={handleReplace} />
        }

      </div>

      <div className="sql-form mt-2">
        <div className="mb-3">
          <Query
            label={gettext('SQL query')}
            value={values.query}
            errors={get(errors, 'query.messages') || errors.query}
            setValue={(query) => setValues({...values, query})}
            editor={editor}
          />
        </div>

        <div className="row">
          <div className="col-md-4">
            <Text
              label={gettext('Table name')}
              value={values.table_name}
              errors={errors.table_name}
              setValue={(table_name) => setValues({...values, table_name})}
            />
          </div>
          <div className="col-md-2">
            <Text
              label={gettext('Run id')}
              value={values.run_id}
              errors={errors.run_id}
              setValue={(run_id) => setValues({...values, run_id})}
            />
          </div>
          <div className="col-md-3">
            <Select
              label={gettext('Query language')}
              value={values.query_language}
              errors={errors.query_language}
              options={queryLanguages}
              setValue={(query_language) => setValues({...values, query_language})}
            />
          </div>
          <div className="col-md-3">
            <Select
              label={gettext('Queue')}
              value={values.queue}
              errors={errors.queue}
              options={queues}
              setValue={(queue) => setValues({...values, queue})}
            />
          </div>
        </div>

        <div className="d-flex mt-2">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleSubmit()}>
            {gettext('Submit new SQL Query')}
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={() => handleClear()}>
            {gettext('Clear input window')}
          </button>
        </div>
      </div>
    </div>
  )
}

FormSql.propTypes = {
  form: PropTypes.object.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string
}

export default FormSql
