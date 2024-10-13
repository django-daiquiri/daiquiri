import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'
import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class ContactApi extends BaseApi {

  static fetchMessages(params) {
    return this.get(`/contact/api/messages/?${encodeParams(params)}`)
  }

  static updateMessage(id, values) {
    return this.put(`/contact/api/messages/${id}/`, values)
  }

}
