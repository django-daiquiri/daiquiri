import { round } from 'lodash'

const bytes2human = (bytes) => {
    const factors = {
        kb: 10**3,
        mb: 10**6,
        gb: 10**9,
        tb: 10**12,
        pb: 10**15,
    }

    if (bytes < factors.kb) {
        return bytes + ' b'
    } else if (bytes < factors.mb) {
        return round(bytes / factors.kb, 1) + ' kB'
    } else if (bytes < factors.gb) {
        return round(bytes / factors.mb, 1) + ' MB'
    } else if (bytes < factors.tb) {
        return round(bytes / factors.gb, 1) + ' GB'
    } else if (bytes < factors.pb) {
        return round(bytes / factors.tb, 1) + ' TB'
    } else {
        return round(bytes / factors.pb, 1) + ' PB'
    }
}

export { bytes2human }
