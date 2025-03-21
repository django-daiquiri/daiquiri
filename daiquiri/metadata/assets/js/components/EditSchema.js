import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import { useGroupsQuery } from 'daiquiri/auth/assets/js/hooks/queries'

import { useAccessLevelsQuery, useLicensesQuery, useMetaQuery } from '../hooks/queries'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Markdown from 'daiquiri/core/assets/js/components/form/Markdown'
import Select from 'daiquiri/core/assets/js/components/form/Select'

import EditName from './EditName'

const EditSchema = ({ values, success, errors, setValues, onSave }) => {
  const { data: accessLevels } = useAccessLevelsQuery()
  const { data: licenses } = useLicensesQuery()
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
      <button className="btn btn-primary btn-sm" onClick={() => onSave('schema', values)}>
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
                label={meta.schema.title.verbose_name}
                help={meta.schema.title.help_text}
                value={values.title}
                errors={errors.title}
                onChange={(title) => setValues({ ...values, title })} />
            </div>
            <div className="col-md-3">
              <Input
                type="number"
                label={meta.schema.order.verbose_name}
                help={meta.schema.order.help_text}
                value={values.order}
                errors={errors.order}
                onChange={(order) => setValues({ ...values, order })} />
            </div>
          </div>

          <div className="row">
            <div className="col-md-4">
              <Select
                label={meta.schema.license.verbose_name}
                help={meta.schema.license.help_text}
                value={values.license}
                options={licenses}
                errors={errors.license}
                onChange={(license) => setValues({ ...values, license })} />
            </div>
            <div className="col-md-4">
              <Input
                label={meta.schema.doi.verbose_name}
                help={meta.schema.doi.help_text}
                value={values.doi}
                errors={errors.doi}
                onChange={(doi) => setValues({ ...values, doi })} />
            </div>
            <div className="col-md-4">
              <Input
                label={meta.schema.utype.verbose_name}
                help={meta.schema.utype.help_text}
                value={values.utype}
                errors={errors.utype}
                onChange={(utype) => setValues({ ...values, utype })} />
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <Input
                type="date"
                label={meta.schema.published.verbose_name}
                help={meta.schema.published.help_text}
                value={values.published || ''}
                errors={errors.published}
                onChange={(published) => setValues({ ...values, published })} />
            </div>
            <div className="col-md-6">
              <Input
                type="date"
                label={meta.schema.updated.verbose_name}
                help={meta.schema.updated.help_text}
                value={values.updated || ''}
                errors={errors.updated}
                onChange={(updated) => setValues({ ...values, updated })} />
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <Select
                label={meta.schema.access_level.verbose_name}
                help={meta.schema.access_level.help_text}
                value={values.access_level}
                options={accessLevels}
                errors={errors.access_level}
                onChange={(access_level) => setValues({ ...values, access_level })} />
            </div>
            <div className="col-md-6">
              <Select
                label={meta.schema.metadata_access_level.verbose_name}
                help={meta.schema.metadata_access_level.help_text}
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
            label={meta.schema.description.verbose_name}
            help={meta.schema.description.help_text}
            value={values.description}
            errors={errors.description}
            onChange={(description) => setValues({ ...values, description })} />
          <Markdown
            label={meta.schema.long_description.verbose_name}
            help={meta.schema.long_description.help_text}
            value={values.long_description}
            errors={errors.long_description}
            onChange={(long_description) => setValues({ ...values, long_description })} />
          <Markdown
            label={meta.schema.attribution.verbose_name}
            help={meta.schema.attribution.help_text}
            value={values.attribution}
            errors={errors.attribution}
            onChange={(attribution) => setValues({ ...values, attribution })} />

          <div className="mb-3">
            <strong className="d-block mb-2">{gettext('Creators')}</strong>
            {
              values.creators.map((creator, creatorIndex) => (
                <EditName
                  key={creatorIndex}
                  person={creator}
                  onChange={(creator) => setValues({
                    ...values, creators: values.creators.map((c, ci) => ci == creatorIndex ? creator : c)
                  })}
                  onRemove={() => setValues({
                    ...values, creators: values.creators.filter((c, ci) => (ci != creatorIndex))
                  })}
                />
              ))
            }
            <button type="button "className="btn btn-success" onClick={() => setValues({
              ...values, creators: [...values.creators, {}]
            })}>
              <i className="bi bi-plus-circle"></i> {gettext('Creator')}
            </button>
          </div>

          <div className="mb-3">
            <strong className="d-block mb-2">{gettext('Contributors')}</strong>
            {
              values.contributors.map((contributor, contributorIndex) => (
                <EditName
                  key={contributorIndex}
                  person={contributor}
                  onChange={(person) => setValues({
                    ...values, contributors: values.contributors.map((c, ci) => ci == contributorIndex ? person : c)
                  })}
                  onRemove={() => setValues({
                    ...values, contributors: values.contributors.filter((c, ci) => (ci != contributorIndex))
                  })}
                />
              ))
            }
            <button type="button "className="btn btn-success" onClick={() => setValues({
              ...values, contributors: [...values.contributors, {}]
            })}>
              <i className="bi bi-plus-circle"></i> {gettext('Contributor')}
            </button>
          </div>
        </form>
      </div>
      <div className="card-footer">
        {buttons}
      </div>
    </div>
  )
}

EditSchema.propTypes = {
  values: PropTypes.object,
  errors: PropTypes.object,
  success: PropTypes.number,
  setValues: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired
}

export default EditSchema
