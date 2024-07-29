import BaseApi from 'daiquiri/core/assets/js/api/BaseApi'

class MetadataApi extends BaseApi {

  static fetchUserSchemas() {
    return this.get('/metadata/api/schemas/user/')
  }

  static fetchUserFunctions() {
    return this.get('/metadata/api/functions/user/')
  }

}

export default MetadataApi
