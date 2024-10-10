const webpack = require('webpack')
const { merge } = require('webpack-merge')
const path = require('path')
const CopyPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')

// list of seperate config objects for each django app and their corresponding java script applications
const configList = [
  {
    name: 'auth',
    entry: {
      users: [
        './daiquiri/auth/assets/js/users.js'
      ]
    },
    output: {
      path: path.resolve(__dirname, './daiquiri/auth/static/auth/dist/')
    }
  },
  {
    name: 'contact',
    entry: {
      messages: [
        './daiquiri/contact/assets/js/messages.js'
      ]
    },
    output: {
      path: path.resolve(__dirname, './daiquiri/contact/static/contact/dist/')
    }
  },
  {
    name: 'core',
    entry: {
      base: [
        './daiquiri/core/assets/js/base.js',
        './daiquiri/core/assets/scss/base.scss'
      ]
    },
    output: {
      path: path.resolve(__dirname, './daiquiri/core/static/core/dist/')
    },
    plugins: [
      new CopyPlugin({
        patterns: [
          {
            from: 'img/*',
            context: './daiquiri/core/assets',
          }
        ]
      })
    ]
  },
  {
    name: 'query',
    entry: {
      examples: [
        './daiquiri/query/assets/js/examples/examples.js',
        './daiquiri/query/assets/scss/examples.scss'
      ],
      jobs: [
        './daiquiri/query/assets/js/jobs/jobs.js',
        './daiquiri/query/assets/scss/jobs.scss'
      ],
      query: [
        './daiquiri/query/assets/js/query/query.js',
        './daiquiri/query/assets/scss/query.scss'
      ]
    },
    output: {
      path: path.resolve(__dirname, './daiquiri/query/static/query/')
    }
  }
]

// base config for all endpoints
const baseConfig = {
  resolve: {
    alias: {
      daiquiri: path.resolve(__dirname, './daiquiri/')
    },
    extensions: ['*', '.js', '.jsx']
  },
  output: {
    filename: 'js/[name].js'
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/[name].css',
      chunkFilename: 'css/[id].css'
    })
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        options: { presets: ['@babel/env','@babel/preset-react'] }
      },
      {
        test: /\.s?css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /(fonts|files)\/.*\.(svg|woff2?|ttf|eot|otf)(\?.*)?$/,
        loader: 'file-loader',
        type: 'javascript/auto',
        options: {
          name: 'fonts/[name].[ext]',
          esModule: false
        }
      },
      {
        test: /\.svg$|\.png$|\.jpg$/,
        loader: 'file-loader',
        options: {
          name: 'img/[name].[ext]'
        }
      }
    ]
  }
}

// special config for development
const developmentConfig = {
  devtool: 'eval',
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('development')
    })
  ]
}

// special config for production
const productionConfig = {
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    })
  ],
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()]
  }
}

// combine config depending on the provided --mode arg
module.exports = (env, argv) => {
  return configList.map(config => {
    if (argv.mode === 'development') {
      return merge(config, baseConfig, developmentConfig)
    } else {
      return merge(config, baseConfig, productionConfig)
    }
  })
}
