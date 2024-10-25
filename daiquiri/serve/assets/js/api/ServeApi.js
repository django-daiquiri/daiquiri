import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'
import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class ServeApi extends BaseApi {

  static fetchColumns(params) {
    return this.get(`/serve/api/columns/?${encodeParams(params)}`)
  }

  static fetchRows(params) {
    return this.get(`/serve/api/rows/?${encodeParams(params)}`)
  }

}
