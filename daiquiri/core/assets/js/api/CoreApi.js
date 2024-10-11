import BaseApi from './BaseApi'

import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class CoreApi extends BaseApi {

  static fetchDataLinks(dataLinkId) {
    const params = {
      'ID': dataLinkId,
      'RESPONSEFORMAT': 'application/json'
    }

    return this.get(`/datalink/links?${encodeParams(params)}`).then(response => response.links)
  }

  static fetchNote(url) {
    return this.getText(url)
  }

}
