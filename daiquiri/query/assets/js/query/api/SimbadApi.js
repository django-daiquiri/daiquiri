import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class SimbadApi {

  static search(options, search) {
    const params = {
      'Ident': search,
      'output.format': 'votable',
      'output.params': 'main_id,coo(d),otype(V)'
    }

    return fetch(options.url + '?' + encodeParams(params))
      .then((response) => {
        if (response.ok) {
          return response.text()
        }
      }).then((xmlString) => {
        const rows = []

        const domParser = new DOMParser()
        const xml = domParser.parseFromString(xmlString, 'text/xml')
        const xmlRows = [...xml.querySelectorAll('TABLEDATA TR')]
        xmlRows.forEach((xmlRow) => {
          const fields = [...xmlRow.childNodes].map((childNode) => childNode.textContent)
          rows.push({
            object: fields[0],
            type: fields[6],
            ra: fields[1],
            de: fields[2],
          })
        })

        return { rows }
      })
  }
}
