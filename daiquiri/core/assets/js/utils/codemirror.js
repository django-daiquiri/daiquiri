import { EditorView, Decoration } from '@codemirror/view'
import { StateField, StateEffect } from '@codemirror/state'

const addUnderline = StateEffect.define({
  map: ({from, to}, change) => ({from: change.mapPos(from), to: change.mapPos(to)})
})

const underlineField = StateField.define({
  create() {
    return Decoration.none
  },
  update(underlines, tr) {
    underlines = underlines.map(tr.changes)
    for (let e of tr.effects) if (e.is(addUnderline)) {
      underlines = underlines.update({
        add: [underlineMark.range(e.value.from, e.value.to)]
      })
    }
    return underlines
  },
  provide: f => EditorView.decorations.from(f)
})

const underlineMark = Decoration.mark({class: 'cm-error'})

export function underlineRange(view, ranges) {
  let effects = ranges.reduce((effects, range) => {
    if (range.to > range.from) {
      return [...effects, range]
    } else {
      return effects
    }
  }, []).map(({from, to}) => addUnderline.of({from, to}))

  if (!effects.length) return false

  if (!view.state.field(underlineField, false))
    effects.push(StateEffect.appendConfig.of([underlineField]))

  view.dispatch({ effects })

  return true
}
