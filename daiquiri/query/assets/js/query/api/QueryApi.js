import BaseApi from '../../../../../core/assets/js/api/BaseApi'
import { encodeParams } from '../../../../../core/assets/js/utils/api'

class QueryApi extends BaseApi {

  static fetchStatus() {
    return this.get('/query/api/status/')
  }

  static fetchForms() {
    return this.get('/query/api/forms/')
  }

  static fetchDropdowns() {
    return this.get('/query/api/dropdowns/')
  }

  static fetchQueues() {
    return this.get('/query/api/queues/')
  }

  static fetchQueryLanguages() {
    return this.get('/query/api/querylanguages/')
  }

  static fetchPhases() {
    return this.get('/query/api/phases/')
  }

  static fetchJobs(params) {
    return this.get(`/query/api/jobs/?${encodeParams(params)}`)
  }

  static fetchJob(id) {
    return this.get(`/query/api/jobs/${id}/`)
  }

  static fetchUserSchema(params) {
    return this.get(`/query/api/jobs/tables/?${encodeParams(params)}`)
  }

  static fetchUserExamples() {
    return this.get('/query/api/examples/user/')
  }

  static fetchUserSchemas() {
    return this.get('/query/api/schemas/user/')
  }

  static fetchUserFunctions() {
    return this.get('/query/api/functions/user/')
  }

  static updateJob(id, values) {
    return this.put(`/query/api/jobs/${id}/`, values)
  }

  static abortJob(id) {
    return this.put(`/query/api/jobs/${id}/abort/`)
  }

  static archiveJob(id) {
    return this.delete(`/query/api/jobs/${id}/`)
  }

}

export default QueryApi
