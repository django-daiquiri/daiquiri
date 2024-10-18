import { isEmpty, isNil, trim } from 'lodash'

import { baseUrl } from 'daiquiri/core/assets/js/utils/meta'

const basePath = `${baseUrl}/query/`

const parseLocation = () => {
  const path = trim(window.location.pathname.replace(basePath, ''), '/')

  // if no path is given display the sql form
  if (isEmpty(path)) {
    return { formKey: 'sql' }
  }

  if (path === 'jobs') {
    return { jobs: true }
  }

  // if a uuid is given, display the corresponding job
  const jobMatch = path.toLowerCase().match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/)
  if (jobMatch) {
    return { jobId: jobMatch[0] }
  }

  return { formKey: path }
}

const updateLocation = ({ jobId, formKey, jobs }) => {
  const pathname = buildPath({ jobId, formKey, jobs })
  if (pathname != window.location.pathname) {
    history.pushState(null, null, pathname)
  }
}

const buildPath = ({ jobId, formKey, jobs }) => {
  let path = basePath

  if (jobs) {
    path += 'jobs/'
  } else {
    if (!isNil(jobId)) {
      path += jobId + '/'
    } else if (!isNil(formKey)) {
      path += formKey + '/'
    }
  }

  return path
}

export { basePath, parseLocation, updateLocation, buildPath }
