app.factory('PlotService', ['$resource', '$q', '$filter', function($resource, $q, $filter) {

    /* define the cmap (extracted from the matplotlib) */
    var cmap_viridis = ['#440154', '#440255', '#440357', '#450558', '#45065a', '#45085b', '#46095c', '#460b5e', '#460c5f', '#460e61', '#470f62', '#471163', '#471265', '#471466', '#471567', '#471669', '#47186a', '#48196b', '#481a6c', '#481c6e', '#481d6f', '#481e70', '#482071', '#482172', '#482273', '#482374', '#472575', '#472676', '#472777', '#472878', '#472a79', '#472b7a', '#472c7b', '#462d7c', '#462f7c', '#46307d', '#46317e', '#45327f', '#45347f', '#453580', '#453681', '#443781', '#443982', '#433a83', '#433b83', '#433c84', '#423d84', '#423e85', '#424085', '#414186', '#414286', '#404387', '#404487', '#3f4587', '#3f4788', '#3e4888', '#3e4989', '#3d4a89', '#3d4b89', '#3d4c89', '#3c4d8a', '#3c4e8a', '#3b508a', '#3b518a', '#3a528b', '#3a538b', '#39548b', '#39558b', '#38568b', '#38578c', '#37588c', '#37598c', '#365a8c', '#365b8c', '#355c8c', '#355d8c', '#345e8d', '#345f8d', '#33608d', '#33618d', '#32628d', '#32638d', '#31648d', '#31658d', '#31668d', '#30678d', '#30688d', '#2f698d', '#2f6a8d', '#2e6b8e', '#2e6c8e', '#2e6d8e', '#2d6e8e', '#2d6f8e', '#2c708e', '#2c718e', '#2c728e', '#2b738e', '#2b748e', '#2a758e', '#2a768e', '#2a778e', '#29788e', '#29798e', '#287a8e', '#287a8e', '#287b8e', '#277c8e', '#277d8e', '#277e8e', '#267f8e', '#26808e', '#26818e', '#25828e', '#25838d', '#24848d', '#24858d', '#24868d', '#23878d', '#23888d', '#23898d', '#22898d', '#228a8d', '#228b8d', '#218c8d', '#218d8c', '#218e8c', '#208f8c', '#20908c', '#20918c', '#1f928c', '#1f938b', '#1f948b', '#1f958b', '#1f968b', '#1e978a', '#1e988a', '#1e998a', '#1e998a', '#1e9a89', '#1e9b89', '#1e9c89', '#1e9d88', '#1e9e88', '#1e9f88', '#1ea087', '#1fa187', '#1fa286', '#1fa386', '#20a485', '#20a585', '#21a685', '#21a784', '#22a784', '#23a883', '#23a982', '#24aa82', '#25ab81', '#26ac81', '#27ad80', '#28ae7f', '#29af7f', '#2ab07e', '#2bb17d', '#2cb17d', '#2eb27c', '#2fb37b', '#30b47a', '#32b57a', '#33b679', '#35b778', '#36b877', '#38b976', '#39b976', '#3bba75', '#3dbb74', '#3ebc73', '#40bd72', '#42be71', '#44be70', '#45bf6f', '#47c06e', '#49c16d', '#4bc26c', '#4dc26b', '#4fc369', '#51c468', '#53c567', '#55c666', '#57c665', '#59c764', '#5bc862', '#5ec961', '#60c960', '#62ca5f', '#64cb5d', '#67cc5c', '#69cc5b', '#6bcd59', '#6dce58', '#70ce56', '#72cf55', '#74d054', '#77d052', '#79d151', '#7cd24f', '#7ed24e', '#81d34c', '#83d34b', '#86d449', '#88d547', '#8bd546', '#8dd644', '#90d643', '#92d741', '#95d73f', '#97d83e', '#9ad83c', '#9dd93a', '#9fd938', '#a2da37', '#a5da35', '#a7db33', '#aadb32', '#addc30', '#afdc2e', '#b2dd2c', '#b5dd2b', '#b7dd29', '#bade27', '#bdde26', '#bfdf24', '#c2df22', '#c5df21', '#c7e01f', '#cae01e', '#cde01d', '#cfe11c', '#d2e11b', '#d4e11a', '#d7e219', '#dae218', '#dce218', '#dfe318', '#e1e318', '#e4e318', '#e7e419', '#e9e419', '#ece41a', '#eee51b', '#f1e51c', '#f3e51e', '#f6e61f', '#f8e621', '#fae622', '#fde724'];
    var cmap_inferno = ['#000003', '#000004', '#000006', '#010007', '#010109', '#01010b', '#02010e', '#020210', '#030212', '#040314', '#040316', '#050418', '#06041b', '#07051d', '#08061f', '#090621', '#0a0723', '#0b0726', '#0d0828', '#0e082a', '#0f092d', '#10092f', '#120a32', '#130a34', '#140b36', '#160b39', '#170b3b', '#190b3e', '#1a0b40', '#1c0c43', '#1d0c45', '#1f0c47', '#200c4a', '#220b4c', '#240b4e', '#260b50', '#270b52', '#290b54', '#2b0a56', '#2d0a58', '#2e0a5a', '#300a5c', '#32095d', '#34095f', '#350960', '#370961', '#390962', '#3b0964', '#3c0965', '#3e0966', '#400966', '#410967', '#430a68', '#450a69', '#460a69', '#480b6a', '#4a0b6a', '#4b0c6b', '#4d0c6b', '#4f0d6c', '#500d6c', '#520e6c', '#530e6d', '#550f6d', '#570f6d', '#58106d', '#5a116d', '#5b116e', '#5d126e', '#5f126e', '#60136e', '#62146e', '#63146e', '#65156e', '#66156e', '#68166e', '#6a176e', '#6b176e', '#6d186e', '#6e186e', '#70196e', '#72196d', '#731a6d', '#751b6d', '#761b6d', '#781c6d', '#7a1c6d', '#7b1d6c', '#7d1d6c', '#7e1e6c', '#801f6b', '#811f6b', '#83206b', '#85206a', '#86216a', '#88216a', '#892269', '#8b2269', '#8d2369', '#8e2468', '#902468', '#912567', '#932567', '#952666', '#962666', '#982765', '#992864', '#9b2864', '#9c2963', '#9e2963', '#a02a62', '#a12b61', '#a32b61', '#a42c60', '#a62c5f', '#a72d5f', '#a92e5e', '#ab2e5d', '#ac2f5c', '#ae305b', '#af315b', '#b1315a', '#b23259', '#b43358', '#b53357', '#b73456', '#b83556', '#ba3655', '#bb3754', '#bd3753', '#be3852', '#bf3951', '#c13a50', '#c23b4f', '#c43c4e', '#c53d4d', '#c73e4c', '#c83e4b', '#c93f4a', '#cb4049', '#cc4148', '#cd4247', '#cf4446', '#d04544', '#d14643', '#d24742', '#d44841', '#d54940', '#d64a3f', '#d74b3e', '#d94d3d', '#da4e3b', '#db4f3a', '#dc5039', '#dd5238', '#de5337', '#df5436', '#e05634', '#e25733', '#e35832', '#e45a31', '#e55b30', '#e65c2e', '#e65e2d', '#e75f2c', '#e8612b', '#e9622a', '#ea6428', '#eb6527', '#ec6726', '#ed6825', '#ed6a23', '#ee6c22', '#ef6d21', '#f06f1f', '#f0701e', '#f1721d', '#f2741c', '#f2751a', '#f37719', '#f37918', '#f47a16', '#f57c15', '#f57e14', '#f68012', '#f68111', '#f78310', '#f7850e', '#f8870d', '#f8880c', '#f88a0b', '#f98c09', '#f98e08', '#f99008', '#fa9107', '#fa9306', '#fa9506', '#fa9706', '#fb9906', '#fb9b06', '#fb9d06', '#fb9e07', '#fba007', '#fba208', '#fba40a', '#fba60b', '#fba80d', '#fbaa0e', '#fbac10', '#fbae12', '#fbb014', '#fbb116', '#fbb318', '#fbb51a', '#fbb71c', '#fbb91e', '#fabb21', '#fabd23', '#fabf25', '#fac128', '#f9c32a', '#f9c52c', '#f9c72f', '#f8c931', '#f8cb34', '#f8cd37', '#f7cf3a', '#f7d13c', '#f6d33f', '#f6d542', '#f5d745', '#f5d948', '#f4db4b', '#f4dc4f', '#f3de52', '#f3e056', '#f3e259', '#f2e45d', '#f2e660', '#f1e864', '#f1e968', '#f1eb6c', '#f1ed70', '#f1ee74', '#f1f079', '#f1f27d', '#f2f381', '#f2f485', '#f3f689', '#f4f78d', '#f5f891', '#f6fa95', '#f7fb99', '#f9fc9d', '#fafda0', '#fcfea4'];
    var cmap_cividis = ['#00224d', '#00234f', '#002350', '#002452', '#002554', '#002655', '#002657', '#002759', '#00285b', '#00285c', '#00295e', '#002a60', '#002a62', '#002b64', '#002c66', '#002c67', '#002d69', '#002e6b', '#002f6d', '#002f6f', '#003070', '#003070', '#003170', '#003170', '#043270', '#083370', '#0b3370', '#0e3470', '#11356f', '#14366f', '#16366f', '#18376f', '#1a386f', '#1c386e', '#1d396e', '#1f3a6e', '#213b6e', '#223b6e', '#243c6e', '#253d6d', '#273d6d', '#283e6d', '#2a3f6d', '#2b3f6d', '#2c406d', '#2e416c', '#2f426c', '#30426c', '#31436c', '#32446c', '#34446c', '#35456c', '#36466c', '#37466c', '#38476c', '#39486c', '#3a486b', '#3b496b', '#3d4a6b', '#3e4b6b', '#3f4b6b', '#404c6b', '#414d6b', '#424d6b', '#434e6b', '#444f6b', '#454f6b', '#46506b', '#47516b', '#48516b', '#49526b', '#4a536b', '#4b546c', '#4c546c', '#4d556c', '#4e566c', '#4e566c', '#4f576c', '#50586c', '#51586c', '#52596c', '#535a6c', '#545a6c', '#555b6d', '#565c6d', '#575d6d', '#585d6d', '#595e6d', '#595f6d', '#5a5f6d', '#5b606e', '#5c616e', '#5d616e', '#5e626e', '#5f636e', '#60646e', '#61646f', '#61656f', '#62666f', '#63666f', '#64676f', '#656870', '#666970', '#676970', '#686a70', '#686b71', '#696b71', '#6a6c71', '#6b6d71', '#6c6d72', '#6d6e72', '#6e6f72', '#6e7073', '#6f7073', '#707173', '#717273', '#727374', '#737374', '#747475', '#747575', '#757575', '#767676', '#777776', '#787876', '#797877', '#797977', '#7a7a77', '#7b7b77', '#7c7b78', '#7d7c78', '#7e7d78', '#7f7d78', '#807e78', '#817f78', '#828078', '#838078', '#848178', '#858278', '#858378', '#868378', '#878478', '#888578', '#898678', '#8a8678', '#8b8778', '#8c8878', '#8d8978', '#8e8978', '#8f8a77', '#908b77', '#918c77', '#928c77', '#938d77', '#948e77', '#958f77', '#968f77', '#979076', '#989176', '#999276', '#9a9376', '#9b9376', '#9c9476', '#9d9575', '#9e9675', '#9f9675', '#a09775', '#a19874', '#a29974', '#a39a74', '#a49a74', '#a59b73', '#a69c73', '#a79d73', '#a89e73', '#a99e72', '#aa9f72', '#aba072', '#aca171', '#ada271', '#aea271', '#afa370', '#b0a470', '#b1a570', '#b2a66f', '#b3a66f', '#b4a76f', '#b5a86e', '#b6a96e', '#b7aa6d', '#b8ab6d', '#b9ab6d', '#baac6c', '#bbad6c', '#bcae6b', '#bdaf6b', '#beb06a', '#bfb06a', '#c1b169', '#c2b269', '#c3b368', '#c4b468', '#c5b567', '#c6b567', '#c7b666', '#c8b765', '#c9b865', '#cab964', '#cbba64', '#ccbb63', '#cdbc62', '#cebc62', '#cfbd61', '#d0be60', '#d2bf60', '#d3c05f', '#d4c15e', '#d5c25e', '#d6c35d', '#d7c35c', '#d8c45b', '#d9c55a', '#dac65a', '#dbc759', '#dcc858', '#dec957', '#dfca56', '#e0cb55', '#e1cc54', '#e2cc53', '#e3cd52', '#e4ce51', '#e5cf50', '#e6d04f', '#e8d14e', '#e9d24d', '#ead34c', '#ebd44b', '#ecd54a', '#edd648', '#eed747', '#efd846', '#f1d944', '#f2da43', '#f3da42', '#f4db40', '#f5dc3f', '#f6dd3d', '#f8de3b', '#f9df3a', '#fae038', '#fbe136', '#fde234', '#fde333', '#fde534', '#fde636', '#fde737'];
    var cmap_gray = ['#000000', '#010101', '#020202', '#030303', '#040404', '#050505', '#060606', '#070707', '#080808', '#090909', '#0a0a0a', '#0b0b0b', '#0c0c0c', '#0d0d0d', '#0e0e0e', '#0f0f0f', '#101010', '#111111', '#121212', '#131313', '#141414', '#151515', '#161616', '#171717', '#181818', '#191919', '#1a1a1a', '#1b1b1b', '#1c1c1c', '#1d1d1d', '#1e1e1e', '#1f1f1f', '#202020', '#212121', '#222222', '#232323', '#242424', '#252525', '#262626', '#272727', '#282828', '#292929', '#2a2a2a', '#2b2b2b', '#2c2c2c', '#2d2d2d', '#2e2e2e', '#2f2f2f', '#303030', '#313131', '#323232', '#333333', '#343434', '#353535', '#363636', '#373737', '#383838', '#393939', '#3a3a3a', '#3b3b3b', '#3c3c3c', '#3d3d3d', '#3e3e3e', '#3f3f3f', '#404040', '#414141', '#424242', '#434343', '#444444', '#454545', '#464646', '#474747', '#484848', '#494949', '#4a4a4a', '#4b4b4b', '#4c4c4c', '#4d4d4d', '#4e4e4e', '#4f4f4f', '#505050', '#515151', '#525252', '#535353', '#545454', '#555555', '#565656', '#575757', '#585858', '#595959', '#5a5a5a', '#5b5b5b', '#5c5c5c', '#5d5d5d', '#5e5e5e', '#5f5f5f', '#606060', '#616161', '#626262', '#636363', '#646464', '#656565', '#666666', '#676767', '#686868', '#696969', '#6a6a6a', '#6b6b6b', '#6c6c6c', '#6d6d6d', '#6e6e6e', '#6f6f6f', '#707070', '#717171', '#727272', '#737373', '#747474', '#757575', '#767676', '#777777', '#787878', '#797979', '#7a7a7a', '#7b7b7b', '#7c7c7c', '#7d7d7d', '#7e7e7e', '#7f7f7f', '#808080', '#818181', '#828282', '#838383', '#848484', '#858585', '#868686', '#878787', '#888888', '#898989', '#8a8a8a', '#8b8b8b', '#8c8c8c', '#8d8d8d', '#8e8e8e', '#8f8f8f', '#909090', '#919191', '#929292', '#939393', '#949494', '#959595', '#969696', '#979797', '#989898', '#999999', '#9a9a9a', '#9b9b9b', '#9c9c9c', '#9d9d9d', '#9e9e9e', '#9f9f9f', '#a0a0a0', '#a1a1a1', '#a2a2a2', '#a3a3a3', '#a4a4a4', '#a5a5a5', '#a6a6a6', '#a7a7a7', '#a8a8a8', '#a9a9a9', '#aaaaaa', '#ababab', '#acacac', '#adadad', '#aeaeae', '#afafaf', '#b0b0b0', '#b1b1b1', '#b2b2b2', '#b3b3b3', '#b4b4b4', '#b5b5b5', '#b6b6b6', '#b7b7b7', '#b8b8b8', '#b9b9b9', '#bababa', '#bbbbbb', '#bcbcbc', '#bdbdbd', '#bebebe', '#bfbfbf', '#c0c0c0', '#c1c1c1', '#c2c2c2', '#c3c3c3', '#c4c4c4', '#c5c5c5', '#c6c6c6', '#c7c7c7', '#c8c8c8', '#c9c9c9', '#cacaca', '#cbcbcb', '#cccccc', '#cdcdcd', '#cecece', '#cfcfcf', '#d0d0d0', '#d1d1d1', '#d2d2d2', '#d3d3d3', '#d4d4d4', '#d5d5d5', '#d6d6d6', '#d7d7d7', '#d8d8d8', '#d9d9d9', '#dadada', '#dbdbdb', '#dcdcdc', '#dddddd', '#dedede', '#dfdfdf', '#e0e0e0', '#e1e1e1', '#e2e2e2', '#e3e3e3', '#e4e4e4', '#e5e5e5', '#e6e6e6', '#e7e7e7', '#e8e8e8', '#e9e9e9', '#eaeaea', '#ebebeb', '#ececec', '#ededed', '#eeeeee', '#efefef', '#f0f0f0', '#f1f1f1', '#f2f2f2', '#f3f3f3', '#f4f4f4', '#f5f5f5', '#f6f6f6', '#f7f7f7', '#f8f8f8', '#f9f9f9', '#fafafa', '#fbfbfb', '#fcfcfc', '#fdfdfd', '#fefefe', '#ffffff'];
    
    /* get the base url */
    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    /* configure resources */
    var resources = {
        rows: $resource(baseurl + 'serve/api/rows/')
    }

    var validtypes = ['short', 'int', 'long', 'float', 'double', 'boolean'];
    var excluded_ucd = ['meta.id', 'meta.version'];

    var service = {
        params: {
            page_size: 100000,
        },
        columns: null,
        values: {},
        errors: {},
        labels: {},
        legends:{},
        colors: {},
        symbols: {},
        ready: false,
        webgl: true
    };

    service.available_colors = [{'name':'Red','hex':'#e41a1c'},
                                {'name':'Blue','hex':'#377eb8'},
                                {'name':'Green','hex':'#4daf4a'},
                                {'name':'Violet','hex':'#984ea3'},
                                {'name':'Orange','hex':'#ff7f00'}];

    service.available_cmaps = {
        gray: cmap_gray,
        viridis: cmap_viridis,
        cividis: cmap_cividis,
        inferno: cmap_inferno
    };
    service.cmap = 'viridis';

    /* the name of the symbols has to match the name of plotting methods of Bokeh.Plotting.figure*/
    service.available_symbols = ['circle', 'triangle', 'diamond', 'star'];

    service.available_hist_op = ['>', '<', '=='];
    var math_operations = {
        '>': function(x, y){return x>y;},
        '<': function(x, y){return x<y;},
        '==': function(x, y){return x==y;}
    };

    service.init = function(opt) {
        service.ready = false;

        // look for a webgl key in localStorage
        if (localStorage.getItem('webgl') === 'true') {
          service.webgl = true;
        } else if (localStorage.getItem('webgl') === 'false') {
          service.webgl = false;
        }

        // set up resources and urls
        resources.rows = $resource(baseurl + opt.rows_url);

        // update params
        angular.extend(service.params, opt.params);

        // set columns
        // service.columns = opt.columns
        service.columns = $filter('filter')(opt.columns, (e) => {
            if (validtypes.indexOf(e.datatype) > -1){return true;}
            else {return false;}
        }, true)

        // exclude columns with ucds defined in the excluded_ucd
        service.columns = $filter('filter')(service.columns, (col) => {
            if (excluded_ucd.map((e) => {
                if (col.ucd) {return col.ucd.indexOf(e);}
                else {return -1;}
            }).some((e) => {
                return e>=0;
            })){
                return false;
            }
            else {return true;}
        }, true)


        if (angular.isDefined(service.columns[0])) {
            service.values.x = service.columns[0].name;
        } else {
            service.values.x = null;
        }

        if (angular.isDefined(service.columns[1])) {
          service.values.y = service.columns[1].name;
        } else {
          service.values.y = null;
        }

        service.values.y3 = null;
        service.values.hist_filter = null;
        service.values.hist_filter_number = 0;
        service.values.hist_op = service.available_hist_op[0];

        service.colors.y = service.available_colors[0].hex;
        service.colors.y2 = service.available_colors[1].hex;
        service.colors.y3 = service.available_colors[2].hex;


        service.symbols.y = service.available_symbols[0];
        service.symbols.y2 = service.available_symbols[0];
        service.symbols.y3 = service.available_symbols[0];

        service.update();
    };

    service.update = function() {
        service.clear();

        if (service.values.x) {
            var x_column = $filter('filter')(service.columns, {name: service.values.x}, true)[0];

            if (validtypes.indexOf(x_column.datatype) > -1) {
                service.errors.x = null;

                service.legends.x = x_column.name;
                service.labels.x = x_column.name;
                if (x_column.unit && x_column.unit.length > 0) {
                    service.labels.x += ' [' + x_column.unit + ']';
                }
            } else {
                service.errors.x = x_column.datatype;
            }
        } else {
            service.errors.x = 'empty';
        }

        if (service.values.y) {
            var y_column = $filter('filter')(service.columns, {name: service.values.y}, true)[0];

            if (validtypes.indexOf(y_column.datatype) > -1) {
                service.errors.y = null;

                service.legends.y = y_column.name;
                service.labels.y = y_column.name;
                if (y_column.unit && y_column.unit.length > 0) {
                    service.labels.y += ' [' + y_column.unit + ']';
                }
            } else {
                service.errors.y = y_column.datatype;
            }
        } else {
            service.errors.y = 'empty';
        }

        if (service.values.y2) {
            var y2_column = $filter('filter')(service.columns, {name: service.values.y2}, true)[0];

            if (validtypes.indexOf(y2_column.datatype) > -1) {
                service.errors.y2 = null;

                service.legends.y2 = y2_column.name;
                service.labels.y2 = y2_column.name;
                if (y2_column.unit && y2_column.unit.length > 0) {
                    service.labels.y2 += ' [' + y2_column.unit + ']';
                }
            } else {
                service.errors.y2 = y2_column.datatype;
            }
        } else {
            service.errors.y2 = 'empty';
        }

        if (service.values.y3) {
            var y3_column = $filter('filter')(service.columns, {name: service.values.y3}, true)[0];

            if (validtypes.indexOf(y3_column.datatype) > -1) {
                service.errors.y3 = null;

                service.legends.y3 = y3_column.name;
                service.labels.y3 = y3_column.name;
                if (y3_column.unit && y3_column.unit.length > 0) {
                    service.labels.y3 += ' [' + y3_column.unit + ']';
                }
            } else {
                service.errors.y3 = y3_column.datatype;
            }
        } else {
            service.errors.y3 = 'empty';
        }

        if (service.errors.x === null && service.errors.y === null) {
            service.fetch().then(function() {
              if (service.plottype == 'scatter_plot'){
                service.draw_scatter_plot();
              }
              else if (service.plottype == 'scatter_cmap_plot'){
                  service.draw_scatter_cmap_plot();
              }
              else if (service.plottype == 'histogram'){
                  service.draw_histogram();
              }
              else if (service.plottype == 'histogram_2d'){
                  service.draw_histogram_2d();
              }
              service.ready = true;
            });
        } else {
            service.ready = true;
        }
    };

    service.clear = function() {
        $('#canvas').empty();
    }

    service.fetch = function() {
        
        /* x and y will be always defined (unless query results do not have data */
        var x_params = angular.extend({}, service.params, {
                        column: service.values.x
        });
        var y_params = angular.extend({}, service.params, {
                        column: service.values.y
        });

        var res_promises = [resources.rows.paginate(x_params).$promise,
                        resources.rows.paginate(y_params).$promise];

        /* add y2 and y3 only if there are selected on the html form*/
        if (service.values.y2){
            var y2_params = angular.extend({}, service.params, {
                            column: service.values.y2
            });
            res_promises.push(resources.rows.paginate(y2_params).$promise);
        }

        if (service.values.y3){
            var y3_params = angular.extend({}, service.params, {
                            column: service.values.y3
            });
            res_promises.push(resources.rows.paginate(y3_params).$promise)
        }

        /* fill service.source with the results from the query*/
        return $q.all(res_promises).then(function(results) {
            service.source = new Bokeh.ColumnDataSource({
                data: {
                    x: results[0].results,
                    y: results[1].results
                }
            });
            if (service.values.y2){service.source.data.y2 = results[2].results;}
            if (service.values.y3){service.source.data.y3 = results[3].results;}
          });
    }

    /* create a basic figure template */
    create_figure = function(x_range, y_range){

        var figure_options = {
          width: 840,
          height: 500,
          x_range: x_range,
          y_range: y_range,
          plot_width: $('.col-md-9').width(),
          tools: 'wheel_zoom,box_zoom,reset,save',
          x_axis_label: service.labels.x,
          y_axis_label: service.labels.y,
          background_fill_color: '#f5f5f5'
        }

        if (service.webgl) {
          figure_options['output_backend'] = 'webgl';
        }

        var figure = new Bokeh.Plotting.figure(figure_options);

        figure.toolbar.active_scroll = figure.toolbar.wheel_zoom;
        figure.outline_line_color = '#dddddd';
        figure.toolbar.logo = null;
        return figure;
    }


    get_xlimits = function(){
        return [Math.min.apply(null, service.source.data.x),
                Math.max.apply(null, service.source.data.x)]
    }


    get_ylimits = function(){
        var ymin = Math.min.apply(null, service.source.data.y),
            ymax = Math.max.apply(null, service.source.data.y);
        
        if (service.source.data.y2){
            ymin = Math.min.apply(null, service.source.data.y2.concat([ymin]));
            ymax = Math.max.apply(null, service.source.data.y2.concat([ymax]));
        }

        if (service.source.data.y3){
            ymin = Math.min.apply(null, service.source.data.y3.concat([ymin]));
            ymax = Math.max.apply(null, service.source.data.y3.concat([ymax]));
        }
        return [ymin, ymax]
    }


    service.draw_scatter_plot = function() {
        var xmin, xmax, ymin, ymax;
        [xmin, xmax] = get_xlimits();
        [ymin, ymax] = get_ylimits();

        if (!isNaN(xmin) && !isNaN(xmax) && !isNaN(ymin) && !isNaN(ymax)) {

            // compute a 1% padding around the data
            var xpad, ypad;
            if (xmax == xmin) {
              xpad = 0.001 * xmax;
            } else {
              xpad = 0.01 * (xmax - xmin);
            }
            if (ymax == ymin) {
              ypad = 0.001 * ymax;
            } else {
              ypad = 0.01 * (ymax - ymin);
            }

            // create some ranges for the plot
            var x_range = new Bokeh.Range1d({
              start: xmin - xpad,
              end: xmax + xpad
            });
            var y_range = new Bokeh.Range1d({
              start: ymin - ypad,
              end: ymax + ypad
            });

            var figure = create_figure(x_range, y_range);

            var plot_y1 = figure[service.symbols.y]({
                x: { field: "x" },
                y: { field: "y" },
                source: service.source,
                fill_alpha: 0.4,
                size: 5,
                color: service.colors.y,
                legend_label: service.legends.y
            });
            
            if (service.source.data.y2){
                var plot_y2 = figure[service.symbols.y2]({
                    x: { field: "x" },
                    y: { field: "y2" },
                    source: service.source,
                    fill_alpha: 0.4,
                    size: 5,
                    color: service.colors.y2,
                    legend_label: service.legends.y2
                });
                figure.yaxis[0].axis_label += "; " + service.labels.y2;
            }
             
            if (service.source.data.y3){
                var plot_y3 = figure[service.symbols.y3]({
                    x: { field: "x" },
                    y: { field: "y3" },
                    source: service.source,
                    fill_alpha: 0.4,
                    size: 5,
                    color: service.colors.y3,
                    legend_label: service.legends.y3
                });
                figure.yaxis[0].axis_label += "; " + service.labels.y3;
            }
            
            Bokeh.Plotting.show(figure, $('#canvas'));
            $('.bk-button-bar-list[type="scroll"] .bk-toolbar-button').click();
            $('.bk-button-bar-list[type="inspectors"] .bk-toolbar-button').click();
        }
    }

    service.draw_scatter_cmap_plot = function() {

        var xmin, xmax;
        [xmin, xmax] = get_xlimits();
        var ymin = Math.min.apply(null, service.source.data.y),
            ymax = Math.max.apply(null, service.source.data.y);

        if (!isNaN(xmin) && !isNaN(xmax) && !isNaN(ymin) && !isNaN(ymax)) {

            // compute a 1% padding around the data
            var xpad, ypad;
            if (xmax == xmin) {
              xpad = 0.001 * xmax;
            } else {
              xpad = 0.01 * (xmax - xmin);
            }
            if (ymax == ymin) {
              ypad = 0.001 * ymax;
            } else {
              ypad = 0.01 * (ymax - ymin);
            }

            // create some ranges for the plot
            var x_range = new Bokeh.Range1d({
              start: xmin - xpad,
              end: xmax + xpad
            });
            var y_range = new Bokeh.Range1d({
              start: ymin - ypad,
              end: ymax + ypad
            });

            var figure = create_figure(x_range, y_range);

            var color_mapper = new Bokeh.LinearColorMapper({
                palette: service.available_cmaps[service.cmap],
                low: Math.min.apply(null, service.source.data.y2),
                high: Math.max.apply(null, service.source.data.y2)
            });

            var plot = figure.circle({
                x: { field: "x" },
                y: { field: "y" },
                source: service.source,
                fill_alpha: 0.6,
                size: 8,
                line_width: 0.5,
                color: {field: 'y2', transform: color_mapper}
            });

            var color_bar = new Bokeh.ColorBar({
                color_mapper: color_mapper,
                title: service.labels.y2
            });

            figure.add_layout(color_bar, 'right');

            Bokeh.Plotting.show(figure, $('#canvas'));
            $('.bk-button-bar-list[type="scroll"] .bk-toolbar-button').click();
            $('.bk-button-bar-list[type="inspectors"] .bk-toolbar-button').click();
        }
    }

    service.draw_histogram = function() {

        var xmin, xmax;
        [xmin, xmax] = get_xlimits();

        if (!isNaN(xmin) && !isNaN(xmax)) {

            // construct the histogram
            var bins = Math.floor(Math.sqrt(service.source.data.x.length)) + 1;
            var bin_size = (xmax - xmin)/(bins-1);

            var histogram = new Array(bins).fill(0);
            var histogram_filtered = new Array(bins).fill(0);
            var bin_pos = new Array(bins).fill(0);
            for (var i=0;i<bins;i++){
              bin_pos[i] = xmin + bin_size*(i+0.5);
            }

            for (var x of service.source.data.x) {
                /* use only defined x values for the histogram */
                if (x){
                    histogram[Math.floor((x - xmin) / bin_size)]++;
                }
            }

            if (service.values.y2){
                for (var i in service.source.data.x) {
                    if (service.source.data.x[i]){
                        if (math_operations[service.values.hist_op](service.source.data.y2[i], service.values.hist_filter_number)){
                            histogram_filtered[Math.floor((service.source.data.x[i] - xmin) / bin_size)]++;
                        }
                    }
                }
            }

            var ymax = 1.05*Math.max.apply(null, histogram);
            var ymin = -0.01*ymax;

            // compute a 1% padding around the data
            var xpad, ypad;
            if (xmax == xmin) {
                xpad = 0.001 * xmax;
            } else {
                xpad = 0.05 * (xmax - xmin);
            }
            if (ymax == ymin) {
                ypad = 0.001 * ymax;
            } else {
                ypad = 0.05 * (ymax - ymin);
            }

            // create some ranges for the plot
            var x_range = new Bokeh.Range1d({
                start: xmin - xpad,
                end: xmax + xpad
            });
            var y_range = new Bokeh.Range1d({
                start: ymin - ypad,
                end: ymax + ypad
            });

            var figure = create_figure(x_range, y_range);

            var hist = figure.vbar({
                x: bin_pos,
                width: bin_size,
                top: histogram,
                color: '#377eb8',
                alpha: 0.5,
                legend_label: service.legends.x
            });

            figure.yaxis[0].axis_label = "Frequency";
            if (service.values.y2){
                var hist_t = figure.vbar({
                    x: bin_pos,
                    width: bin_size,
                    top: histogram_filtered,
                    color: '#4daf4a',
                    alpha: 0.4,
                    legend_label: service.legends.x + ', ' + service.legends.y2 + service.values.hist_op + service.values.hist_filter_number
                });
            }

            Bokeh.Plotting.show(figure, $('#canvas'));
            $('.bk-button-bar-list[type="scroll"] .bk-toolbar-button').click();
            $('.bk-button-bar-list[type="inspectors"] .bk-toolbar-button').click();
        }
    }

    service.toggle_webgl = function() {
        service.webgl = !service.webgl;
        service.update();
        localStorage.setItem('webgl', service.webgl);
    }

    return service;
}]);
