export const layout = {
  autosize: true,
  dragmode: 'pan',
  margin: {
    l: 40,
    r: 40,
    b: 40,
    t: 40
  }
}

export const config = {
  displayModeBar: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['select2d', 'lasso2d']
}

export const colors = [
  {name:'Red', hex:'#e41a1c'},
  {name:'Blue', hex:'#377eb8'},
  {name:'Green', hex:'#4daf4a'},
  {name:'Violet', hex:'#984ea3'},
  {name:'Orange', hex:'#ff7f00'}
]

// see https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales for more colorscales
export const cmaps = ['Viridis', 'Inferno', 'Cividis', 'Grays', 'Turbo', 'Bluered']

export const symbols = [
  {name: 'Circle', symbol: 'circle', materialSymbol: 'circle', fontSize: 14},
  {name: 'Square', symbol: 'square', materialSymbol: 'square', fontSize: 14},
  {name: 'Diamond', symbol: 'diamond', materialSymbol: 'stat_0', fontSize: 22},
  {name: 'Triangle', symbol: 'triangle-up', materialSymbol: 'change_history', fontSize: 16},
  {name: 'Star', symbol: 'star', materialSymbol: 'star', fontSize: 18},
]

export const operations = [
  {name: '>', operation: (x, y) => (x > y)},
  {name: '<', operation: (x, y) => (x < y)},
  {name: '==', operation: (x, y) => (x == y)}
]

export const validTypes = ['short', 'int', 'long', 'float', 'double', 'boolean']

export const excludedUcds = ['meta.id', 'meta.version']
