import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class SimbadApi {

  static search(url, search) {
    const params = {
      'Ident': search,
      'output.format': 'votable',
      'output.params': 'main_id,coo(d),otype(V)'
    }

    return fetch(url + '?' + encodeParams(params))
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
          const children = xmlRow.childNodes
          const row = {
            object: children[0].textContent,
            type: children[6].textContent,
            ra: children[1].textContent,
            de: children[2].textContent,
          }
          rows.push(row)
        })

        return rows
      })
  }
}
