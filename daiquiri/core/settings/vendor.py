VENDOR_CDN = True

VENDOR = {
    'jquery': {
        'url': 'https://code.jquery.com/',
        'js': [
            {
                'path': 'jquery-3.2.1.min.js',
                'sri': 'sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=',
            }
        ]
    },
    'bootstrap': {
        'url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/',
        'js': [
            {
                'path': 'js/bootstrap.min.js',
                'sri': 'sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa',
            }
        ],
        'css': [
            {
                'path': 'css/bootstrap.min.css',
                'sri': 'sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
            }
        ]
    },
    'font-awesome': {
        'url': 'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/',
        'css': [
            {
                'path': 'css/font-awesome.min.css'
            }
        ],
        'font': [
            {
                'path': 'fonts/fontawesome-webfont.eot'
            },
            {
                'path': 'fonts/fontawesome-webfont.woff2'
            },
            {
                'path': 'fonts/fontawesome-webfont.woff'
            },
            {
                'path': 'fonts/fontawesome-webfont.ttf'
            },
            {
                'path': 'fonts/fontawesome-webfont.svg'
            }
        ]
    },
    'angular': {
        'url': 'https://ajax.googleapis.com/ajax/libs/angularjs/1.6.5/',
        'js': [
            {
                'path': 'angular.min.js'
            },
            {
                'path': 'angular-resource.min.js'
            }
        ]
    },
    'ng-infinite-scroll': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/ngInfiniteScroll/1.3.0/',
        'js': [
            {
                'path': 'ng-infinite-scroll.min.js',
                'sri': 'sha256-nUL1iPqMsX6n0f19hNGgkMsUgqQmP5k8PUWbDc1R/jU='
            }
        ]
    },
    'moment': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.18.1/',
        'js': [
            {
                'path': 'moment.min.js',
                'sri': 'sha256-1hjUhpc44NwiNg8OwMu2QzJXhD8kcj+sJA3aCQZoUjg='
            }
        ]
    },
    'codemirror': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/',
        'js': [
            {
                'path': 'codemirror.min.js',
                'sri': 'sha256-0LRLvWWVXwt0eH0/Bzd0PHICg/bSMDIe5sXgaDSpZaA='
            },
            {
                'path': 'addon/mode/overlay.min.js',
                'sri': 'sha256-ffWkw3Pn4ieMygm1vwdRKcMtBJ6E6kuBi8GlVVPXWEs='
            },
                        {
                'path': 'mode/sql/sql.min.js',
                'sri': 'sha256-AYn1SMwJJCzQwlDkZLt7gAA3v8M14QZ7X5fGnJ2juYU='
            },
            {
                'path': 'mode/markdown/markdown.min.js',
                'sri': 'sha256-NzPBTZOCkVLaG/iTZe2XXF4cIyer9J0C0Z1FRN3WqNc='
            },
            {
                'path': 'addon/runmode/runmode.min.js',
                'sri': 'sha256-zO/lIsoS+q+kwzLO/YDjAGkeHUEw7Ql6ceZ4UMbityU='
            }
        ],
        'css': [
            {
                'path': 'codemirror.min.css',
                'sri': 'sha256-wluO/w4cnorJpS0JmcdTSYzwdb5E6u045qa4Ervfb1k='
            }
        ]
    },
    'Bokeh': {
        'url': 'https://cdnjs.cloudflare.com/ajax/libs/bokeh/0.12.9/',
        'js': [
            {
                'path': 'bokeh.min.js',
                'sri': 'sha256-gm+i+GziZJeKlRYH8akT+7hC0yT0tK+VCoxApQ/uU1A='
            },
                        {
                'path': 'bokeh-gl.min.js',
                'sri': 'sha256-lle0sk6DP7Leca/0dBodUdbkGTqtqNUTLkbVZa1PceE='
            },
            {
                'path': 'bokeh-api.min.js',
                'sri': 'sha256-v22ko+YNfTgeB3sa9OjSWmHds7uwi3KjjVBFLhhGdy0='
            }
        ],
        'css': [
            {
                'path': 'bokeh.min.css',
                'sri': 'sha256-Gke8Knvnof6hLUSaaUp++1Chsbh5yxwdjslBLRO5iK4='
            }
        ]
    }
}
