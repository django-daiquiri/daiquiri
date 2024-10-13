import { encodeParams } from 'daiquiri/core/assets/js/utils/api'

export default class VizierApi {

  static search(options, search) {
    const params = {
      '-source': options.catalogs.join(' '),
      '-c': search,
      '-c.r': 2,
      '-out': '_RA _DEC _r *meta.id.part;meta.main *meta.id;meta.main',
      '-sort': '_r',
      '-out.max': 5
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

        options.catalogs.forEach((catalog) => {
          const xmlDescription = xml.querySelector(`RESOURCE[name='${catalog}'] DESCRIPTION`)
          const xmlRows = [...xml.querySelectorAll(`RESOURCE[name='${catalog}'] TABLEDATA TR`)]

          xmlRows.forEach((xmlRow) => {
            const fields = [...xmlRow.childNodes].map((childNode) => childNode.textContent)

            let id = fields[3]
            if (catalog == 'I/259') {
              id += `-${fields[4]}-${fields[5]}`  // hack for Tycho 2 catalog
            }

            rows.push({
              id: id,
              ra: fields[0],
              de: fields[1],
              distance: fields[2],
              catalog: xmlDescription.textContent
            })
          })
        })

        return { rows }
      })
  }
}
