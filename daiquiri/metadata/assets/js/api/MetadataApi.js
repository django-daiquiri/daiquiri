import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'

class MetadataApi extends BaseApi {

  static fetchManagementSchemas() {
    return this.get('/metadata/api/schemas/management/')
  }

  static fetchManagementFunctions() {
    return this.get('/metadata/api/functions/management/')
  }

  static fetchUserSchemas() {
    return this.get('/metadata/api/schemas/user/')
  }

  static fetchUserFunctions() {
    return this.get('/metadata/api/functions/user/')
  }

  static fetchSchema(id) {
    return this.get(`/metadata/api/schemas/${id}/`)
  }

  static createSchema(values) {
    return this.post('/metadata/api/schemas/', values)
  }

  static updateSchema(id, values) {
    return this.put(`/metadata/api/schemas/${id}/`, values)
  }

  static fetchTable(id) {
    return this.get(`/metadata/api/tables/${id}/`)
  }

  static createTable(values) {
    return this.post('/metadata/api/tables/', values)
  }

  static updateTable(id, values) {
    return this.put(`/metadata/api/tables/${id}/`, values)
  }

  static discoverTable(id) {
    return this.post(`/metadata/api/tables/${id}/discover/`)
  }

  static fetchColumn(id) {
    return this.get(`/metadata/api/columns/${id}/`)
  }

  static createColumn(values) {
    return this.post('/metadata/api/columns/', values)
  }

  static updateColumn(id, values) {
    return this.put(`/metadata/api/columns/${id}/`, values)
  }

  static discoverColumn(id) {
    return this.post(`/metadata/api/columns/${id}/discover/`)
  }

  static fetchFunction(id) {
    return this.get(`/metadata/api/functions/${id}/`)
  }

  static createFunction(values) {
    return this.post('/metadata/api/functions/', values)
  }

  static updateFunction(id, values) {
    return this.put(`/metadata/api/functions/${id}/`, values)
  }

  static fetchLicenses() {
    return this.get('/metadata/api/licenses/')
  }

  static fetchAccessLevels() {
    return this.get('/metadata/api/accesslevels/')
  }

  static fetchMeta() {
    return this.get('/metadata/api/meta/')
  }

}

export default MetadataApi
