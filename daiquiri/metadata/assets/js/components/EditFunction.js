import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import { useGroupsQuery } from 'daiquiri/auth/assets/js/hooks/queries'

import { useAccessLevelsQuery, useMetaQuery } from '../hooks/queries'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Markdown from 'daiquiri/core/assets/js/components/form/Markdown'
import Select from 'daiquiri/core/assets/js/components/form/Select'

const EditFunction = ({ values, success, errors, setValues, onSave }) => {
  const { data: accessLevels } = useAccessLevelsQuery()
  const { data: meta } = useMetaQuery()
  const { data: groups } = useGroupsQuery()

  const buttons = (
    <div className="d-flex align-items-center">
      <span className="me-auto">
        <strong>{gettext('Schema')}</strong> {values.label}
      </span>
      <div className={classNames('d-flex align-items-center text-success success-indicator me-2', {
        show: success
      })}>
        <div className="bi bi-check"></div>
      </div>
      <a className="btn btn-secondary btn-sm me-2" href={values.admin_url} target="_blank" rel="noreferrer">
        {gettext('Admin')}
      </a>
      <button className="btn btn-primary btn-sm" onClick={() => onSave('function', values)}>
        {gettext('Save')}
      </button>
    </div>
  )

  return meta && groups && (
    <div className="card">
      <div className="card-header">
        {buttons}
      </div>
      <div className="card-body">
        <form onSubmit={(event => event.preventDefault())}>
          <div className="row">
            <div className="col-md-9">
              <Input
                label={meta.function.name.verbose_name}
                help={meta.function.name.help_text}
                value={values.name}
                errors={errors.name}
                onChange={(name) => setValues({ ...values, name })} />
            </div>
            <div className="col-md-3">
              <Input
                type="number"
                label={meta.function.order.verbose_name}
                help={meta.function.order.help_text}
                value={values.order}
                errors={errors.order}
                onChange={(order) => setValues({ ...values, order })} />
            </div>
          </div>

          <Input
            label={meta.function.query_string.verbose_name}
            help={meta.function.query_string.help_text}
            value={values.query_string}
            errors={errors.query_string}
            onChange={(query_string) => setValues({ ...values, query_string })} />

          <div className="row">
            <div className="col-md-6">
              <Select
                label={meta.function.access_level.verbose_name}
                help={meta.function.access_level.help_text}
                value={values.access_level}
                options={accessLevels}
                errors={errors.access_level}
                onChange={(access_level) => setValues({ ...values, access_level })} />
            </div>
            <div className="col-md-6">
              <Select
                label={meta.function.metadata_access_level.verbose_name}
                help={meta.function.metadata_access_level.help_text}
                value={values.metadata_access_level}
                options={accessLevels}
                errors={errors.metadata_access_level}
                onChange={(metadata_access_level) => setValues({ ...values, metadata_access_level })} />
            </div>
          </div>

          <div className="mb-3">
            <strong className="d-block mb-2">{gettext('Groups with access')}</strong>
            {
              groups.map((group, groupIndex) => (
                <Checkbox
                  key={groupIndex}
                  label={group.name}
                  checked={values.groups.includes(group.id)}
                  onChange={(checked) => setValues({ ...values, groups: checked ? (
                    [ ...values.groups, group.id]
                  ) : (
                    values.groups.filter(group_id => group_id !== group.id)
                  )})}
                />
              ))
            }
          </div>

          <Markdown
            label={meta.function.description.verbose_name}
            help={meta.function.description.help_text}
            value={values.description}
            errors={errors.description}
            onChange={(description) => setValues({ ...values, description })} />
        </form>
      </div>
      <div className="card-footer">
        {buttons}
      </div>
    </div>
  )
}

EditFunction.propTypes = {
  values: PropTypes.object,
  errors: PropTypes.object,
  success: PropTypes.number,
  setValues: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired
}

export default EditFunction
