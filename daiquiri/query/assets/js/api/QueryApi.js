import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'
import { downloadFile, encodeParams } from 'daiquiri/core/assets/js/utils/api'

class QueryApi extends BaseApi {

  static fetchStatus() {
    return this.get('/query/api/status/')
  }

  static fetchForms() {
    return this.get('/query/api/forms/')
  }

  static fetchForm(key) {
    return this.get(`/query/api/forms/${key}/`)
  }

  static fetchDropdowns() {
    return this.get('/query/api/dropdowns/')
  }

  static fetchDownloadForms(id) {
    return this.get(`/query/api/jobs/${id}/downloadforms/`)
  }

  static fetchSubmittedDownloads(id) {
    return this.get(`/query/api/jobs/${id}/downloads/`)
  }

  static fetchDownloadFormats() {
    return this.get('/query/api/downloadformats/')
  }

  static fetchJobs(params) {
    return this.get(`/query/api/jobs/?${encodeParams(params)}`)
  }

  static fetchJobsIndex() {
    return this.get('/query/api/jobs/index/')
  }

  static fetchJobsTables(params) {
    return this.get(`/query/api/jobs/tables/?${encodeParams(params)}`)
  }

  static fetchJob(id) {
    return this.get(`/query/api/jobs/${id}/`)
  }

  static submitJob(values, formKey = null) {
    if (formKey) {
      return this.post(`/query/api/jobs/forms/${formKey}/`, values)
    } else {
      return this.post('/query/api/jobs/', values)
    }
  }

  static uploadJob(values) {
    var formData = new FormData()
    for (const [key, value] of Object.entries(values)) {
      formData.append(key, value)
    }

    return this.upload('/query/api/jobs/upload/', formData)
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

  static fetchJobColumns(id, params) {
    return this.get(`/query/api/jobs/${id}/columns/?${encodeParams(params)}`)
  }

  static fetchJobRows(id, params) {
    return this.get(`/query/api/jobs/${id}/rows/?${encodeParams(params)}`)
  }

  static submitDownloadJob(id, downloadKey, data) {
    return this.post(`/query/api/jobs/${id}/download/${downloadKey}/`, data)
  }

  static fetchUserExamples() {
    return this.get('/query/api/examples/user/')
  }

  static fetchQueues() {
    return this.get('/query/api/queues/')
  }

  static fetchQueryLanguages() {
    return this.get('/query/api/querylanguages/')
  }

}

export default QueryApi
