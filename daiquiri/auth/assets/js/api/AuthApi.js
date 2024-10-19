import { isNil } from 'lodash'

import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'
import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class AuthApi extends BaseApi {

  static fetchProfiles(params) {
    return this.get(`/auth/api/profiles/?${encodeParams(params)}`)
  }

  static updateProfile(id, values, action) {
    if (isNil(action)) {
      return this.put(`/auth/api/profiles/${id}/`, values)
    } else {
      return this.put(`/auth/api/profiles/${id}/${action}/`)
    }
  }

  static fetchSettings() {
    return this.get('/auth/api/settings/')
  }

  static fetchGroups() {
    return this.get('/auth/api/groups/')
  }

}
