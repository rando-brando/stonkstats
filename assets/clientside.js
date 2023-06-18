window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        suggest_options: function(query, data) {
            if (query) {
                var df = JSON.parse(data)
                var filteredData = df.filter(function(row) {
                    var search = query.toLowerCase()
                    var symbol = row.symbol.toLowerCase()
                    var name = row.companyName.toLowerCase()
                    if (symbol.includes(search) || name.includes(search)) {
                        return row;
                    }
                })
                var rows = filteredData.slice(0,8).map((row, index) => {
                    return {
                        'type': 'Tr',
                        'namespace': 'dash_html_components',
                        'props': {
                            'id': {'index': `result-${index}`, 'type': 'search-row'},
                            'class': 'search-row',
                            'children': [
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'symbol',
                                        'children': row.symbol,
                                    }
                                },
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'company',
                                        'children': row.companyName
                                    }
                                },
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'exchange',
                                        'children': row.exchangeShortName
                                    }
                                }
                            ]
                        }
                    }
                })
                return rows
            }
        },
        select_option: function(clicks, rows) {
            no_update = window.dash_clientside.no_update
            if (rows) {
                for (const [index, row] of rows.entries()) {
                    if (typeof clicks[index] === 'number') {
                        if(clicks[index] > 0) {
                            return [row[0].props.children, null]
                        }
                    }
                }
            }
            return [no_update, no_update]
        }
    }
});